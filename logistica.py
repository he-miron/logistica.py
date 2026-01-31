import streamlit as st
import pandas as pd

# 1. Configurações de Página
st.set_page_config(page_title="Formosa Log - Entregador", layout="wide", page_icon="📦")

# 2. Estilo Visual (Focado em leitura rápida no sol/rua)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .delivery-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #ee4d2d;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .status-badge {
        background-color: #ee4d2d;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .address-text { font-size: 1.1rem; color: #ffffff; margin: 10px 0; }
    /* Botões Grandes para o dedo do motoboy */
    .stButton>button {
        height: 50px;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexão com a Planilha (Aba de Pedidos/Logística)
# Certifique-se de que este link aponta para a aba onde as vendas caem
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"

@st.cache_data(ttl=30) # Atualiza a cada 30 segundos
def load_logistica():
    df = pd.read_csv(SHEET_URL)
    return df

# Cabeçalho
st.title("🚀 Formosa Log")
st.write("Painel de Entregas em Tempo Real")

try:
    df = load_logistica()
    
    # Filtro: Mostra apenas o que não foi entregue (assumindo coluna 'status')
    # Se sua planilha não tiver a coluna 'status', ele mostrará tudo
    if 'status' in df.columns:
        pendentes = df[df['status'] != 'Entregue']
    else:
        pendentes = df

    if pendentes.empty:
        st.success("✅ Nenhuma entrega pendente. Bom descanso!")
    else:
        for index, row in pendentes.iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="delivery-card">
                        <span class="status-badge">AGUARDANDO COLETA</span>
                        <p class="address-text">📍 <b>{row['endereco']}</b></p>
                        <p style="color: #bbb; margin: 0;">Bairro: {row['bairro'] if 'bairro' in row else 'Centro'}</p>
                        <p style="color: #bbb; margin: 0;">Cliente: {row['cliente'] if 'cliente' in row else 'Não informado'}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botões de Ação
                col1, col2 = st.columns(2)
                
                with col1:
                    # Roteirizador: Abre o Google Maps
                    endereco_busca = f"{row['endereco']}, Formosa, GO"
                    link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_busca.replace(' ', '+')}"
                    st.link_button("🗺️ Abrir GPS", link_maps, use_container_width=True)
                
                with col2:
                    if st.button("✅ Entregue", key=f"btn_{index}", use_container_width=True):
                        st.balloons()
                        st.success(f"Pedido de {row['cliente']} finalizado!")
                        # Nota: Para atualizar a planilha automaticamente, precisaríamos da API do Google. 
                        # Por enquanto, você dá a baixa manual ao receber o aviso.

except Exception as e:
    st.error(f"Erro ao conectar com a central: {e}")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Pedidos"):
    st.rerun()
