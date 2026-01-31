import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configurações de Página
st.set_page_config(page_title="SPX Formosa - Logística", layout="wide")

# Estilo Dark Mode Shopee Express
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .stCamera > div { border: 2px solid #ee4d2d; border-radius: 10px; }
    .card-entrega { background: #1e1e1e; padding: 20px; border-radius: 15px; border-bottom: 4px solid #ee4d2d; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 SPX Parceiro - Formosa")

# 2. Integração com Planilha
SHEET_URL = "SUA_URL_DA_PLANILHA_AQUI"

try:
    # 3. LEITOR DE CÓDIGO DE BARRAS / SKU
    # No celular, isso abre a câmera para ler o código do pacote
    st.subheader("🛡️ Conferência de Pacote")
    barcode = st.text_input("Aponte o leitor ou digite o código do pacote")
    
    if barcode:
        st.success(f"✅ Pacote {barcode} verificado no sistema!")

    st.divider()

    # 4. ÁREA DE ENTREGA ATIVA
    st.subheader("📍 Entrega em Curso")
    
    # Exemplo de Card de Endereço
    st.markdown("""
        <div class="card-entrega">
            <p style='margin:0; color:#ee4d2d;'><b>CLIENTE: João da Silva</b></p>
            <p style='font-size:20px;'>Rua 15, Casa 200, Setor Central</p>
            <p style='color:#bbb;'>Referência: Perto da Igreja Matriz</p>
        </div>
    """, unsafe_allow_html=True)

    # 5. COMPROVANTE DE ENTREGA (FOTO)
    st.subheader("📸 Foto do Local/Endereço")
    foto_comprovante = st.camera_input("Tire foto da fachada ou do recebedor")

    if foto_comprovante:
        st.image(foto_comprovante, caption="Foto capturada com sucesso!", use_container_width=True)
        
        # 6. BOTÃO DE FINALIZAÇÃO REAL
        if st.button("🏁 FINALIZAR ENTREGA E NOTIFICAR"):
            st.balloons()
            st.success("Entrega registrada! Os dados da foto e horário foram enviados para a central.")
            # Aqui você integraria com o backend para salvar a imagem

except Exception as e:
    st.info("Aguardando carregamento da rota...")
