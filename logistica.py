import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# Configuração da página
st.set_page_config(page_title="FSA Roteirizador", layout="wide")

# Inicializa o leitor de OCR (Carrega uma vez e guarda em cache)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['pt'])

reader = load_ocr()

def extrair_dados_etiqueta(imagem):
    # Converte imagem para array
    img_array = np.array(imagem)
    resultado = reader.readtext(img_array, detail=0)
    # Aqui entra a lógica para identificar o CEP ou Endereço no meio do texto
    # Exemplo simplificado: procurando um padrão de CEP
    texto_completo = " ".join(resultado)
    return texto_completo

# --- INTERFACE ---
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=150) # Sua logo
st.sidebar.title("FSA Roteirização")
opcao = st.sidebar.radio("Menu", ["Escanear Etiquetas", "Ver Rota Otimizada"])

if "lista_enderecos" not in st.session_state:
    st.session_state.lista_enderecos = []

if opcao == "Escanear Etiquetas":
    st.header("📸 Escaneamento de Etiquetas")
    
    upload = st.file_uploader("Tire uma foto ou suba a imagem da etiqueta", type=['png', 'jpg', 'jpeg'])
    
    if upload:
        img = Image.open(upload)
        st.image(img, caption="Etiqueta carregada", width=300)
        
        if st.button("Processar e Extrair Endereço"):
            texto = extrair_dados_etiqueta(img)
            st.success(f"Texto detectado: {texto}")
            
            # Simulação de extração (Em um app real, usaríamos Regex para pegar o CEP)
            endereco_fake = st.text_input("Confirme ou corrija o endereço extraído:", value=texto[:50])
            
            if st.button("Adicionar à Lista de Entrega"):
                st.session_state.lista_enderecos.append(endereco_fake)
                st.rerun()

    st.write("---")
    st.subheader("📍 Lista de Entregas Atual")
    st.write(st.session_state.lista_enderecos)

elif opcao == "Ver Rota Otimizada":
    st.header("🚚 Rota Estilo SPX")
    
    if len(st.session_state.lista_enderecos) < 2:
        st.warning("Adicione pelo menos 2 endereços para gerar uma rota.")
    else:
        # Aqui integraríamos com a API do Google Maps ou OpenStreetMap (OSRM)
        st.info("Otimizando sequência de entrega para menor tempo...")
        
        # Simulação de Mapa
        m = folium.Map(location=[-15.44, -47.28], zoom_start=13) # Coordenadas de Formosa-GO
        
        # Adicionando marcadores (Simulados)
        for i, end in enumerate(st.session_state.lista_enderecos):
            folium.Marker(
                location=[-15.44 - (i*0.01), -47.28 - (i*0.01)], # Offset simulado
                popup=f"Parada {i+1}: {end}",
                icon=folium.Icon(color="purple", icon="shopping-cart")
            ).add_to(m)
        
        st_folium(m, width=1000, height=500)
        
        st.subheader("📋 Sequência de Entrega Sugerida")
        for i, end in enumerate(st.session_state.lista_enderecos):
            st.write(f"**{i+1}ª Parada:** {end}")
