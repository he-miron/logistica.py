import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="SPX Parceiro Formosa", layout="wide", page_icon="🚚")

# Estilo Logística (Cores Escuras/Azul Profissional)
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: white; }
    .delivery-card {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ee4d2d;
        margin-bottom: 15px;
    }
    .status-pendente { color: #ffcc00; font-weight: bold; }
    .btn-maps {
        background-color: #4285F4;
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        text-decoration: none;
        display: block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Link da sua planilha de LOGÍSTICA (Aba de entregas)
SHEET_URL = "SUA_URL_DA_PLANILHA_DE_LOGISTICA_AQUI"

@st.cache_data(ttl=10)
def load_logistica():
    return pd.read_csv(SHEET_URL)

st.title("🚚 SPX - Painel do Entregador")
st.write("Formosa Logística Express")

try:
    df = load_logistica()
    
    # Filtro apenas para pedidos pendentes
    pendentes = df[df['status'] == 'Pendente']

    if pendentes.empty:
        st.success("Tudo entregue! Nenhuma rota pendente em Formosa.")
    else:
        for index, row in pendentes.iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="delivery-card">
                        <p style="margin:0;"><b>PEDIDO #{row['pedido_id']}</b></p>
                        <p style="font-size:18px; margin:5px 0;">📍 {row['endereco']}</p>
                        <p style="color:gray;">Bairro: {row['bairro']} | Cliente: {row['cliente']}</p>
                        <p class="status-pendente">Aguardando Coleta</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Roteirizador: Abre o Google Maps com o endereço
                endereco_completo = f"{row['endereco']}, {row['bairro']}, Formosa, GO"
                link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_completo.replace(' ', '+')}"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<a href="{link_maps}" target="_blank" class="btn-maps">🗺️ Roteirizar (Maps)</a>', unsafe_allow_html=True)
                with col2:
                    if st.button(f"Confirmar Entrega", key=f"entregue_{index}"):
                        st.balloons()
                        st.info(f"Marque o pedido {row['pedido_id']} como 'Entregue' na sua planilha!")

except Exception as e:
    st.warning("Aguardando sincronização com a planilha de logística...")

st.sidebar.markdown("### Perfil do Parceiro")
st.sidebar.write("👤 Entregador: João Motoboy")
st.sidebar.write("💰 Ganhos Hoje: R$ 85,00")
