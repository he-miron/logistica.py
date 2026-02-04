import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. Configurações de Segurança e Interface
st.set_page_config(page_title="FSA Smart Vision", layout="centered", page_icon="👁️")

st.markdown("""
    <style>
    .stCamera { border: 4px solid #7000FF; border-radius: 20px; }
    .result-box { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 6px solid #00FF00; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Configuração da API
# Tenta pegar a chave do Streamlit Cloud Secrets primeiro
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Se rodar localmente, coloque sua chave aqui
    API_KEY = "SUA_CHAVE_AQUI"

genai.configure(api_key=API_KEY)

def processar_com_ia(imagem_pil, modo):
    # Usamos o nome de modelo mais estável disponível atualmente
    # Se 'gemini-1.5-flash' der 404, o sistema tentará o 'gemini-1.5-pro'
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro-vision') # Fallback para versões antigas

    if modo == "Logística (Etiquetas)":
        prompt = """
        Você é um assistente de logística da FSA Market. 
        Analise a imagem da etiqueta e extraia COM PRECISÃO:
        1. Endereço completo (Rua, Número, Bairro, Cidade).
        2. CEP (apenas números).
        3. Nome do Cliente (se visível).
        Responda em formato de lista simples.
        """
    else:
        prompt = """
        Você é um especialista em decifrar caligrafia médica e textos cursivos complexos. 
        Transcreva o texto da imagem de forma fiel e organizada. 
        Se for uma receita, identifique medicamentos e dosagens.
        """

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# 3. Interface do Usuário
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=120) # Logo FSA
st.title("👁️ FSA Smart Vision")
st.caption("Leitor de Inteligência Artificial para Logística e Documentos")

modo = st.segmented_control("O que vamos ler agora?", ["Logística (Etiquetas)", "Manuscrito (Receitas)"], default="Logística (Etiquetas)")

foto = st.camera_input("POSICIONE O PAPEL NA FRENTE DA CÂMERA")

if foto:
    img = Image.open(foto)
    
    with st.spinner('A IA está processando os dados...'):
        try:
            texto_decifrado = processar_com_ia(img, modo)
            
            st.markdown("### ✅ Resultado da Transcrição")
            st.markdown(f"<div class='result-box'>{texto_decifrado}</div>", unsafe_allow_html=True)

            if modo == "Logística (Etiquetas)":
                # Tenta extrair o endereço para o botão de GPS
                linhas = texto_decifrado.split('\n')
                endereco_para_mapa = ""
                for linha in linhas:
                    if "Endereço" in linha or "Rua" in linha:
                        endereco_para_mapa = linha.split(":")[-1].strip()
                
                if endereco_para_mapa:
                    link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(endereco_para_mapa)}"
                    st.link_button("🚀 ABRIR NO GOOGLE MAPS", link_maps)
            
            st.button("📥 SALVAR NO HISTÓRICO")

        except Exception as e:
            st.error(f"Erro de Conexão: {str(e)}")
            st.info("Dica: Verifique se sua API KEY está ativa no Google AI Studio.")
