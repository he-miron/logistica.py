import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="FSA Smart Vision", layout="centered", page_icon="👁️")

# --- CONEXÃO COM API ---
# Tenta buscar a chave nos Secrets do Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("🔑 Insira sua Gemini API Key", type="password")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # Forçamos a listagem para garantir que o modelo existe na sua conta
        available_models = [m.name for m in genai.list_models()]
    except Exception as e:
        st.error(f"Erro de autenticação: {e}")
else:
    st.warning("⚠️ Chave API não configurada.")

def processar_ia_robusto(imagem_pil, modo):
    # O segredo é usar o sufixo -latest para evitar o erro 404 de versão
    # Se gemini-1.5-flash-latest falhar, ele tentará o gemini-1.5-pro-latest
    model_name = 'gemini-1.5-flash-latest'
    
    # Fallback caso o modelo flash não esteja disponível na região
    if f"models/{model_name}" not in available_models and "models/gemini-1.5-flash" not in available_models:
        model_name = 'gemini-1.5-pro-latest'

    model = genai.GenerativeModel(model_name)
    
    if modo == "📦 Logística":
        prompt = "Analise a etiqueta. Extraia Endereço, CEP e Cliente. Formate como lista."
    else:
        prompt = "Transcreva fielmente esta caligrafia cursiva/receita médica. Organize medicamentos e doses."

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- INTERFACE ---
st.title("👁️ FSA Smart Vision")
modo = st.radio("Selecione o serviço:", ["📦 Logística", "⚕️ Decifrador"])

foto = st.camera_input("Capturar Imagem")

if foto and API_KEY:
    img = Image.open(foto)
    with st.spinner('Decifrando...'):
        try:
            resultado = processar_ia_robusto(img, modo)
            st.markdown("### 📝 Resultado:")
            st.code(resultado, language="text")
            
            if modo == "📦 Logística":
                # Botão GPS Simplificado
                busca = urllib.parse.quote(resultado[:100])
                st.link_button("🚀 Abrir no Google Maps", f"https://www.google.com/maps/search/{busca}")
                
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
            st.info("Dica: Verifique se sua conta no Google AI Studio tem acesso ao modelo 1.5 Flash.")
