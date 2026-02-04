import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import folium
from streamlit_folium import st_folium
import urllib.parse

# 1. Configuração de Alta Performance
st.set_page_config(page_title="FSA Smart Log", layout="wide", page_icon="🚀")

# CSS para interface de coletor de dados profissional
st.markdown("""
    <style>
    .stCamera { border: 5px solid #7000FF; border-radius: 15px; }
    .entrega-card { 
        background-color: #1e1e1e; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #00FF00; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if "fila_entrega" not in st.session_state:
    st.session_state.fila_entrega = []

def processamento_sofisticado(imagem):
    # Melhora a imagem para leitura (Escala de cinza e Contraste)
    img_cinza = imagem.convert('L')
    texto = pytesseract.image_to_string(img_cinza, lang='por')
    
    # --- MÁQUINA DE EXTRAÇÃO (REGEX) ---
    # Busca CEP
    cep = re.search(r'(\d{5}-?\d{3})', texto)
    # Busca padrões comuns de endereço (Rua, Av, Travessa + número)
    rua = re.search(r'(Rua|Av|Avenida|Travessa|Al\.)\s+([A-ZÀ-Úa-z\s\d]+),?\s*(\d+)', texto, re.IGNORECASE)
    
    dados = {
        "cep": cep.group(1) if cep else None,
        "endereco": rua.group(0) if rua else "Endereço não detectado",
        "texto_bruto": texto
    }
    return dados

# 2. Interface Principal
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=120)
menu = st.sidebar.selectbox("Módulo", ["🚀 Coletor Automático", "🗺️ Rota em Tempo Real"])

if menu == "🚀 Coletor Automático":
    st.title("Scanner FSA Smart")
    st.write("Aponte a câmera. O sistema lerá e enviará para a fila automaticamente.")
    
    foto = st.camera_input("SCANNER ATIVO")
    
    if foto:
        img = Image.open(foto)
        resultado = processamento_sofisticado(img)
        
        if resultado['cep']:
            # Lógica de Fila Automática
            nova_entrega = {
                "id": len(st.session_state.fila_entrega) + 1,
                "local": resultado['endereco'],
                "cep": resultado['cep'],
                "maps": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(resultado['endereco'] + ' ' + resultado['cep'])}",
                "status": "📦 Na fila"
            }
            
            # Evita duplicados (opcional)
            if not any(e['cep'] == resultado['cep'] for e in st.session_state.fila_entrega):
                st.session_state.fila_entrega.append(nova_entrega)
                st.balloons()
                st.success(f"LIDO: {resultado['endereco']} - CEP: {resultado['cep']}")
            else:
                st.warning("Esta etiqueta já foi lida e está na fila.")
        else:
            st.error("Falha na leitura automática. Tente focar no bloco de endereço da etiqueta.")

    # Exibição da Fila Estilo Checklist
    if st.session_state.fila_entrega:
        st.write("---")
        st.subheader("📋 Fila de Roteirização Instantânea")
        for ent in st.session_state.fila_entrega:
            st.markdown(f"""
            <div class="entrega-card">
                <b>PARADA {ent['id']}</b> | {ent['status']}<br>
                📍 {ent['local']}<br>
                <small>CEP: {ent['cep']}</small>
            </div>
            """, unsafe_allow_html=True)

elif menu == "🗺️ Rota em Tempo Real":
    if not st.session_state.fila_entrega:
        st.info("Aguardando capturas de etiquetas...")
    else:
        st.subheader("Mapa de Calor e Roteiro")
        
        # Mapa
        m = folium.Map(location=[-15.53, -47.33], zoom_start=13)
        for i, ent in enumerate(st.session_state.fila_entrega):
            folium.Marker(
                [-15.53 - (i*0.004), -47.33 - (i*0.004)],
                popup=ent['local'],
                icon=folium.Icon(color='purple', icon='truck', prefix='fa')
            ).add_to(m)
        st_folium(m, width="100%", height=400)
        
        # Botões de Ação para o Entregador
        for ent in st.session_state.fila_entrega:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"**{ent['id']} - {ent['local']}**")
            if col_b.link_button("Abrir GPS", ent['maps']):
                pass # O link_button já faz o redirect
