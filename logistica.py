import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. Tente buscar a chave dos Secrets do Streamlit (Mais seguro)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY = "SUA_CHAVE_AQUI_PARA_TESTE_LOCAL"

genai.configure(api_key=API_KEY)

def processar_com_ia(imagem_pil, modo):
    # Usando o nome estável mais recente
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if modo == "Etiqueta/Logística":
        prompt = """
        Analise esta etiqueta. Extraia:
        Endereço: [Rua, Número, Bairro, Cidade]
        CEP: [Somente números]
        Cliente: [Nome se houver]
        """
    else:
        prompt = """
        Você é um especialista em decifrar caligrafia cursiva e receitas médicas. 
        Transcreva o texto de forma fiel e organizada.
        """

    # Ajuste para garantir a geração de conteúdo
    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- Interface ---
st.title("👁️ FSA Smart Vision")
# ... resto do código da interface
