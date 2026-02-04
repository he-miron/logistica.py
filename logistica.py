import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FSA Smart Vision", layout="centered", page_icon="👁️")

# Estilo CSS para modo noturno e cards profissionais
st.markdown("""
    <style>
    .stCamera { border: 4px solid #7000FF; border-radius: 20px; }
    .result-box { 
        background-color: #1e1e1e; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 6px solid #00FF00; 
        color: white;
        font-family: 'Courier New', Courier, monospace;
    }
    .main-title { color: #7000FF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API (SEGURANÇA) ---
# Tenta buscar nos Secrets do Streamlit Cloud. Se não achar, abre campo no app.
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Insira sua Gemini API Key", type="password")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        st.error(f"Erro ao configurar API: {e}")
else:
    st.warning("⚠️ Aguardando Chave API. Configure nos Secrets do Streamlit Cloud.")

# --- FUNÇÃO DE INTELIGÊNCIA ARTIFICIAL ---
def processar_com_ia(imagem_pil, modo):
    # Usando o modelo estável mais recente
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if modo == "📦 Logística (Etiquetas)":
        prompt = """
        Você é um assistente de logística da FSA Market. 
        Analise a etiqueta e extraia APENAS:
        - Endereço completo (Rua, Número, Bairro, Cidade)
        - CEP (apenas números)
        - Nome do Cliente
        Formate como uma lista simples e limpa.
        """
    else:
        prompt = """
        Você é um especialista em decifrar caligrafia médica e textos cursivos complexos. 
        Transcreva o texto desta imagem de forma fiel e perfeita. 
        Se for uma receita médica, organize por Medicamentos, Dosagens e Instruções.
        Se o texto estiver muito difícil, use o contexto médico para deduzir.
        """

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- INTERFACE DO USUÁRIO ---
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=120) # Sua Logo FSA
st.sidebar.title("FSA Smart Vision")
st.sidebar.markdown("---")

st.markdown("<h1 class='main-title'>👁️ Smart Reader Pro</h1>", unsafe_allow_html=True)

# Seleção de modo de uso
modo = st.radio("Selecione o modo de leitura:", ["📦 Logística (Etiquetas)", "⚕️ Decifrador (Receita/Cursiva)"])

# Captura de Imagem
foto = st.camera_input("POSICIONE O PAPEL E TIRE A FOTO")

if foto and API_KEY:
    img = Image.open(foto)
    
    with st.spinner('A IA está analisando a imagem...'):
        try:
            resultado = processar_com_ia(img, modo)
            
            st.markdown("### 📝 Resultado da Transcrição")
            st.markdown(f"<div class='result-box'>{resultado}</div>", unsafe_allow_html=True)

            # Lógica extra para Logística (Botão GPS)
            if modo == "📦 Logística (Etiquetas)":
                # Tenta isolar o endereço para o Google Maps
                linhas = resultado.split('\n')
                endereco_final = ""
                for linha in linhas:
                    if "Endereço" in linha or "Rua" in linha:
                        endereco_final = linha.split(":")[-1].strip()
                
                if endereco_final:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(endereco_final)}"
                    st.link_button("🚀 ABRIR ROTA NO GOOGLE MAPS", maps_url)
            
            # Botão para copiar/salvar (simulado)
            st.button("📋 Salvar no Histórico Diário")

        except Exception as e:
            st.error(f"Erro no processamento: {e}")
            st.info("Verifique se sua API Key é válida e se você tem conexão com a internet.")

elif not API_KEY:
    st.info("ℹ️ Para começar, insira sua API Key no menu lateral ou nos Secrets.")

# Rodapé informando a origem
st.markdown("---")
st.caption("FSA Market | Formosa-GO | Powered by Gemini AI 1.5 Flash")
