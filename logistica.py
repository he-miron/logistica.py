import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import folium
from streamlit_folium import st_folium
import urllib.parse

# 1. Configurações Iniciais
st.set_page_config(page_title="FSA Roteirizador", layout="wide", page_icon="🚚")

# Estilo Dark para combinar com sua marca
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #7000FF; color: white; }
    </style>
    """, unsafe_allow_html=True)

if "entregas" not in st.session_state:
    st.session_state.entregas = []

def extrair_cep_limpo(imagem):
    imagem = imagem.convert('L')
    texto = pytesseract.image_to_string(imagem, lang='por')
    resultado = re.search(r'(\d{5}-?\d{3})', texto)
    return resultado.group(1) if resultado else None

# 2. Barra Lateral (Identidade FSA)
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=120) 
st.sidebar.title("FSA Express")
aba = st.sidebar.radio("Navegação", ["📦 Escanear Etiquetas", "🗺️ Rota e GPS"])

# 3. Aba de Leitura
if aba == "📦 Escanear Etiquetas":
    st.header("Leitura de Etiquetas")
    foto = st.camera_input("Aponte para o endereço/CEP")
    
    if foto:
        img = Image.open(foto)
        with st.spinner('Lendo dados...'):
            cep = extrair_cep_limpo(img)
            if cep:
                st.success(f"CEP Detectado: {cep}")
                with st.form("detalhes"):
                    nome = st.text_input("Nome do Cliente", placeholder="Ex: Miron de Aquino")
                    rua = st.text_input("Rua e Número (Opcional)", placeholder="Ex: Rua 15, 200")
                    if st.form_submit_button("Confirmar Entrega"):
                        # Criamos o link de busca para o Maps aqui
                        endereco_busca = f"{rua}, {cep}, Formosa, GO"
                        link_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(endereco_busca)}"
                        
                        st.session_state.entregas.append({
                            "Cliente": nome,
                            "CEP": cep,
                            "Endereço": endereco_busca,
                            "Mapa": link_maps
                        })
                        st.success("Adicionado à fila de entrega!")
            else:
                st.error("CEP não encontrado. Tente focar melhor ou limpar a lente.")

# 4. Aba de Roteirização e GPS
elif aba == "🗺️ Rota e GPS":
    st.header("🚚 Roteiro de Entregas Otimizado")
    
    if not st.session_state.entregas:
        st.info("Sua fila de entregas está vazia.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Mapa Interativo
            mapa = folium.Map(location=[-15.5385, -47.3350], zoom_start=14)
            for i, ent in enumerate(st.session_state.entregas):
                folium.Marker(
                    location=[-15.5385 - (i*0.002), -47.3350 - (i*0.002)],
                    popup=ent['Cliente'],
                    tooltip=f"Parada {i+1}",
                    icon=folium.Icon(color='purple', icon='info-sign')
                ).add_to(mapa)
            st_folium(mapa, width="100%", height=450)

        with col2:
            st.subheader("Ordem de Entrega")
            for i, ent in enumerate(st.session_state.entregas):
                with st.expander(f"🚩 {i+1}ª: {ent['Cliente']}"):
                    st.write(f"**CEP:** {ent['CEP']}")
                    st.write(f"**Local:** {ent['Endereço']}")
                    # Botão que abre o Google Maps nativo do celular
                    st.markdown(f'''
                        <a href="{ent['Mapa']}" target="_blank">
                            <button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">
                                📍 ABRIR NO GOOGLE MAPS
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)

        if st.sidebar.button("🗑️ Resetar Diária"):
            st.session_state.entregas = []
            st.rerun()
