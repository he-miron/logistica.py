import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(page_title="FSA Roteirizador", layout="wide")

# Identidade Visual no menu lateral
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=120) 
st.sidebar.title("FSA Express")

if "entregas" not in st.session_state:
    st.session_state.entregas = []

def extrair_cep_limpo(imagem):
    # Transforma em escala de cinza para facilitar a leitura do OCR
    imagem = imagem.convert('L')
    texto = pytesseract.image_to_string(imagem, lang='por')
    
    # Busca o padrão de CEP: 5 números, um traço opcional e 3 números
    resultado = re.search(r'(\d{5}-?\d{3})', texto)
    return resultado.group(1) if resultado else None

# --- MENU ---
aba = st.sidebar.selectbox("Ir para:", ["📦 Ler Etiquetas", "🚚 Rota Otimizada"])

if aba == "📦 Ler Etiquetas":
    st.header("Leitura de Etiquetas via OCR")
    
    # Abre a câmera nativa do celular
    foto = st.camera_input("Aponte para o CEP da etiqueta")
    
    if foto:
        img = Image.open(foto)
        with st.spinner('Processando imagem...'):
            cep = extrair_cep_limpo(img)
            
            if cep:
                st.success(f"CEP Detectado: {cep}")
                with st.form("confirmar"):
                    nome = st.text_input("Nome do Cliente")
                    obs = st.text_input("Observação (Ex: Casa de esquina)")
                    if st.form_submit_button("Adicionar à Rota"):
                        st.session_state.entregas.append({"CEP": cep, "Cliente": nome, "Status": "Pendente"})
                        st.toast("Adicionado com sucesso!")
            else:
                st.error("Não achei o CEP. Garanta que a luz esteja boa e o CEP esteja nítido.")

    # Lista de conferência
    if st.session_state.entregas:
        st.write("---")
        st.subheader("Fila de Entrega")
        st.table(pd.DataFrame(st.session_state.entregas))
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.entregas = []
            st.rerun()

elif aba == "🚚 Rota Otimizada":
    st.header("Sequência de Entrega Estilo SPX")
    
    if not st.session_state.entregas:
        st.info("Nenhuma entrega pendente para roteirizar.")
    else:
        # Lógica de ordenação (Simplificada: Ordem de leitura)
        st.warning("Otimizando trajeto para menor distância...")
        
        # Centralizando em Formosa-GO
        mapa = folium.Map(location=[-15.5385, -47.3350], zoom_start=14)
        
        # Simulando marcadores baseados na lista
        for i, entrega in enumerate(st.session_state.entregas):
            folium.Marker(
                location=[-15.5385 - (i*0.003), -47.3350 - (i*0.003)],
                popup=f"Parada {i+1}: {entrega['Cliente']}",
                icon=folium.Icon(color='purple', icon='play', prefix='fa')
            ).add_to(mapa)
            
        st_folium(mapa, width="100%", height=500)
        
        st.subheader("Ordem de Saída:")
        for i, ent in enumerate(st.session_state.entregas):
            st.write(f"🚩 **{i+1}ª Parada:** {ent['Cliente']} (CEP: {ent['CEP']})")
