import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="AQUINO Smart Vision", layout="centered", page_icon="👁️")

# --- AUTENTICAÇÃO SEGURA ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("🔑 Gemini API Key", type="password")

if API_KEY:
    try:
        # Configura a API
        genai.configure(api_key=API_KEY)
        
        # TESTE CRÍTICO: Verifica quais modelos sua chave REALMENTE acessa
        # Isso limpa o erro de 'modelo não encontrado'
        modelos_disponiveis = [m.name for m in genai.list_models()]
        
        # Escolhe o melhor modelo disponível (prioriza Flash, depois Pro)
        if "models/gemini-1.5-flash" in modelos_disponiveis:
            NOME_MODELO = "gemini-1.5-flash"
        elif "models/gemini-1.5-pro" in modelos_disponiveis:
            NOME_MODELO = "gemini-1.5-pro"
        else:
            # Pega o primeiro modelo que suporta geração de conteúdo como última opção
            NOME_MODELO = modelos_disponiveis[0].replace("models/", "")
            
    except Exception as e:
        st.error(f"Erro ao conectar com Google AI: {e}")
else:
    st.warning("⚠️ Insira a chave API para ativar o scanner.")

def processar_ia(imagem_pil, modo):
    # Inicializa o modelo detectado no teste acima
    model = genai.GenerativeModel(NOME_MODELO)
    
    if modo == "📦 Logística":
        prompt = "Leia a etiqueta e extraia: Endereço completo, CEP e Cliente. Seja direto."
    else:
        prompt = "Decifre esta caligrafia/receita médica. Transcreva medicamentos e instruções de uso."

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- INTERFACE ---
st.title("👁️ AQUINO Smart Vision")
st.write(f"Conectado ao modelo: `{NOME_MODELO if API_KEY else 'Aguardando...'}`")

modo = st.radio("Selecione o Uso:", ["📦 Logística", "⚕️ Decifrador"])
foto = st.camera_input("Scanner")

if foto and API_KEY:
    img = Image.open(foto)
    with st.spinner('A IA está analisando...'):
        try:
            resultado = processar_ia(img, modo)
            st.markdown("### ✅ Resultado:")
            st.info(resultado)
            
            if modo == "📦 Logística":
                # Link para GPS
                busca = urllib.parse.quote(resultado[:150])
                st.link_button("🚀 Abrir no Google Maps", f"https://www.google.com/maps/search/{busca}")
                
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
