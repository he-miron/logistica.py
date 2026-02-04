import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="FSA Smart Vision", layout="centered")

# --- AJUSTE DE API ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Insira sua API Key", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    
def processar_com_ia(imagem_pil, modo):
    # O segredo aqui é usar 'gemini-1.5-flash' sem o prefixo 'models/' 
    # ou usar a versão mais recente e estável
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if modo == "📦 Logística":
        prompt = "Analise a etiqueta e extraia o endereço completo e CEP."
    else:
        prompt = "Decifre este texto manuscrito/receita médica de forma detalhada."

    # Forçar a geração de conteúdo
    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- RESTO DO CÓDIGO ---
st.title("👁️ FSA Smart Vision")
modo = st.radio("Modo:", ["📦 Logística", "⚕️ Decifrador"])
foto = st.camera_input("Scanner")

if foto and API_KEY:
    img = Image.open(foto)
    try:
        resultado = processar_com_ia(img, modo)
        st.write(resultado)
    except Exception as e:
        # Se o 404 persistir, o erro pode ser a versão da biblioteca no requirements
        st.error(f"Erro: {e}")
