import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="FSA Smart Reader", layout="centered", page_icon="👁️")

# Inserir sua chave API do Google AI Studio aqui
# Obtenha em: https://aistudio.google.com/
API_KEY = "AIzaSyA6DVvDWwiVss6hF90klKgF8cD2Qwmppxw"
genai.configure(api_key=API_KEY)

# Estilo para parecer um App Nativo Premium
st.markdown("""
    <style>
    .stCamera { border: 4px solid #7000FF; border-radius: 20px; }
    .result-box { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border-left: 6px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

if "lista_leitura" not in st.session_state:
    st.session_state.lista_leitura = []

def processar_com_ia(imagem_pil, modo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if modo == "Etiqueta/Logística":
        prompt = """
        Analise esta etiqueta. Extraia APENAS o endereço completo e o CEP. 
        Formate a resposta exatamente assim:
        Endereço: [Rua, Número, Bairro, Cidade]
        CEP: [Somente números]
        Se houver nome de cliente, adicione:
        Cliente: [Nome]
        """
    else:
        prompt = """
        Você é um especialista em decifrar caligrafia cursiva e receitas médicas. 
        Transcreva o texto da imagem de forma fiel. Se for uma receita, organize por:
        1. Medicamentos e Dosagens
        2. Instruções de Uso
        Seja preciso, mesmo com letras difíceis.
        """

    response = model.generate_content([prompt, imagem_pil])
    return response.text

# --- Interface ---
st.title("👁️ FSA Smart Vision")
modo = st.segmented_control("O que vamos ler?", ["Etiqueta/Logística", "Receita/Cursiva"], default="Etiqueta/Logística")

foto = st.camera_input("CAPTURE A IMAGEM")

if foto:
    img = Image.open(foto)
    
    with st.spinner('A IA está decifrando a caligrafia...'):
        try:
            texto_decifrado = processar_com_ia(img, modo)
            
            st.markdown("### 📝 Resultado da Análise")
            st.markdown(f"<div class='result-box'>{texto_decifrado}</div>", unsafe_allow_html=True)

            if modo == "Etiqueta/Logística":
                # Botão para abrir no Maps automaticamente
                # Tentamos extrair o endereço do texto para o link
                if "Endereço:" in texto_decifrado:
                    endereco_limpo = texto_decifrado.split("Endereço:")[1].split("\n")[0]
                    link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(endereco_limpo)}"
                    st.link_button("🚀 INICIAR ROTA NO GPS", link_maps)
            
            if st.button("📥 Salvar na Fila"):
                st.session_state.lista_leitura.append(texto_decifrado)
                st.toast("Salvo com sucesso!")

        except Exception as e:
            st.error(f"Erro ao processar: {e}. Verifique sua chave API.")

# Histórico Rápido
if st.session_state.lista_leitura:
    with st.expander("📋 Histórico de Leituras"):
        for item in reversed(st.session_state.lista_leitura):
            st.write(item)
            st.divider()
