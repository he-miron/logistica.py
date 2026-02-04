import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import re
import pandas as pd
import urllib.parse

# Configuração
st.set_page_config(page_title="FSA Smart Scanner", layout="centered")

if "fila" not in st.session_state:
    st.session_state.fila = []

def tratar_imagem(imagem):
    # 1. Converte para escala de cinza
    img = ImageOps.grayscale(imagem)
    # 2. Aumenta o contraste (ajuda a separar letra do fundo)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # 3. Binarização (Preto e Branco puro)
    img = img.point(lambda x: 0 if x < 140 else 255, '1')
    return img

def extrair_endereco_robusto(imagem):
    img_tratada = tratar_imagem(imagem)
    # Configuração do Tesseract para ler blocos de texto
    config_tesseract = '--psm 3' 
    texto_bruto = pytesseract.image_to_string(img_tratada, lang='por', config=config_tesseract)
    
    linhas = [line.strip() for line in texto_bruto.split('\n') if len(line.strip()) > 5]
    
    cep = None
    logradouro = "Não identificado"
    
    # Busca CEP em todas as linhas
    for linha in linhas:
        busca_cep = re.search(r'(\d{5}-?\d{3})', linha)
        if busca_cep:
            cep = busca_cep.group(1)
        
        # Lógica para identificar a rua: Geralmente contém números e palavras como Rua, Av, Quadra, Casa...
        if any(keyword in linha.upper() for keyword in ["RUA", "AV", "AVENIDA", "QDR", "QUADRA", "CASA", "LOTE", "SETOR"]):
            logradouro = linha

    return cep, logradouro, texto_bruto

# --- Interface ---
st.title("🚀 Scanner de Alta Precisão FSA")
st.write("Dica: Mantenha a etiqueta reta e bem iluminada.")

foto = st.camera_input("SCANNER")

if foto:
    img_original = Image.open(foto)
    cep, endereco, bruto = extrair_endereco_robusto(img_original)
    
    if cep or endereco != "Não identificado":
        st.subheader("📍 Dados Capturados")
        
        # Permite edição rápida caso o OCR erre uma letra ou número
        ed_end = st.text_input("Endereço:", value=endereco)
        ed_cep = st.text_input("CEP:", value=cep if cep else "")
        
        if st.button("✅ Confirmar e Salvar na Fila"):
            maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(ed_end + ' ' + ed_cep)}"
            st.session_state.fila.append({
                "Local": ed_end,
                "CEP": ed_cep,
                "Maps": maps_link
            })
            st.success("Adicionado à rota!")
            st.rerun()
    else:
        st.error("Não foi possível isolar o endereço. Tente tirar a foto mais de perto.")
        with st.expander("Ver o que o sistema 'leu'"):
            st.text(bruto)

# --- Fila de Trabalho ---
if st.session_state.fila:
    st.write("---")
    st.subheader("🚚 Roteiro de Entrega")
    for i, item in enumerate(st.session_state.fila):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{i+1}.** {item['Local']} ({item['CEP']})")
        col2.link_button("Ir para GPS", item['Maps'])

    if st.button("Limpar Tudo"):
        st.session_state.fila = []
        st.rerun()
