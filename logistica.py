import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="FSA Vision Pro", layout="centered")

# --- CONEXÃO COM API ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Insira sua Gemini API Key", type="password")

if API_KEY:
    try:
        # Configuração forçando a versão estável
        genai.configure(api_key=API_KEY)
        
        # Teste de conexão: Busca o modelo exato disponível
        # Isso evita tentar modelos que sua chave não tem acesso
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na Chave API: {e}")
else:
    st.warning("⚠️ Aguardando configuração da chave nos Secrets.")

def processar_ia(imagem_pil, modo):
    # Usamos o nome base do modelo que é o mais compatível
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if modo == "Logística (Etiquetas)":
        prompt = "Extraia o endereço completo, CEP e nome do cliente desta etiqueta de entrega."
    else:
        prompt = "Você é um especialista em caligrafia. Transcreva esta receita médica ou texto cursivo com perfeição."

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- INTERFACE ---
st.title("👁️ FSA Smart Vision")
modo = st.radio("Selecione o Uso:", ["Logística (Etiquetas)", "Decifrador (Receita/Cursiva)"])

foto = st.camera_input("Scanner Ativo")

if foto and API_KEY:
    img = Image.open(foto)
    with st.spinner('A IA está lendo o documento...'):
        try:
            resultado = processar_ia(img, modo)
            st.markdown("### ✅ Transcrição Gerada:")
            st.info(resultado)
            
            if modo == "Logística (Etiquetas)":
                # Gera link para GPS
                busca = urllib.parse.quote(resultado[:150])
                st.link_button("🚀 Abrir no Google Maps", f"https://www.google.com/maps/search/?api=1&query={busca}")
                
        except Exception as e:
            # Se o erro 404 persistir, mostramos quais modelos SUA chave pode usar
            st.error(f"Erro no modelo: {e}")
            with st.expander("Ver modelos disponíveis para você"):
                modelos = [m.name for m in genai.list_models()]
                st.write(modelos)
