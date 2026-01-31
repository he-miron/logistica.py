import streamlit as st
import pandas as pd

st.set_page_config(page_title="Formosa Log", layout="wide")

# Estilo para o motoboy
st.markdown("<style>.stApp{background-color:#121212; color:white;}</style>", unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=522097234&single=true&output=csv"

@st.cache_data(ttl=10)
def load_logistica():
    return pd.read_csv(SHEET_URL)

st.title("🚚 Painel de Entregas")

try:
    df = load_logistica()
    
    # Limpa nomes de colunas (remove espaços extras)
    df.columns = [c.strip().lower() for c in df.columns]

    if 'endereco' not in df.columns:
        st.error(f"⚠️ A coluna 'endereco' não foi encontrada. As colunas atuais são: {list(df.columns)}")
        st.info("Ajuste o topo da sua planilha para ter a coluna: endereco")
    else:
        # Se a coluna existir, mostra os pedidos
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                    <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #ee4d2d; margin-bottom:10px;">
                        <p style="margin:0;"><b>📍 {row['endereco']}</b></p>
                        <p style="color:#bbb; font-size:14px;">Bairro: {row.get('bairro', 'Não informado')}</p>
                        <p style="color:#bbb; font-size:14px;">Cliente: {row.get('cliente', 'Ver no Zap')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botão GPS
                maps_url = f"https://www.google.com/maps/search/{str(row['endereco']).replace(' ', '+')}+Formosa+GO"
                st.link_button(f"🗺️ Rota para o Pedido {index+1}", maps_url, use_container_width=True)

except Exception as e:
    st.error(f"Erro de conexão: {e}")
