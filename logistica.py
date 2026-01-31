import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configurações de Página e Estilo SPX Dark
st.set_page_config(page_title="SPX Parceiro - Formosa", layout="centered", page_icon="🚚")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .card-entrega {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #ee4d2d;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background-color: #ee4d2d;
        color: white;
        font-weight: bold;
        height: 50px;
        border-radius: 10px;
    }
    .login-box {
        background-color: #1e1e1e;
        padding: 40px;
        border-radius: 20px;
        border-top: 5px solid #ee4d2d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização do Estado (Login e Memória)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.motorista_id = ""

# 3. Função para carregar Dados (Planilha Mestra)
# IMPORTANTE: Use o link da sua aba de 'pedidos' ou 'logistica'
SHEET_URL = "SUA_URL_AQUI"
# Aba de usuários para validar login
USER_SHEET_URL = "SUA_URL_DA_ABA_USUARIOS_AQUI"

@st.cache_data(ttl=10)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

# --- FLUXO DE TELAS ---

if not st.session_state.autenticado:
    # TELA DE LOGIN
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("SPX LOGÍSTICA")
    st.write("Acesso Restrito ao Motorista")
    
    user_input = st.text_input("ID do Motorista (ex: moto_joao)")
    pass_input = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        try:
            users_df = load_data(USER_SHEET_URL)
            # Validação simples na planilha
            valido = users_df[(users_df['usuario'] == user_input) & (users_df['senha'].astype(str) == pass_input)]
            
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.rerun()
            else:
                st.error("Login ou Senha incorretos.")
        except:
            st.error("Erro ao conectar com banco de usuários.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # APP DE LOGÍSTICA LOGADO
    st.sidebar.title(f"🚚 {st.session_state.motorista_id.upper()}")
    if st.sidebar.button("Sair/Logout"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Rotas")
    
    try:
        df = load_data(SHEET_URL)
        
        # FILTRO: Mostra apenas o que é deste motorista e está PENDENTE
        entregas = df[(df['entregador'] == st.session_state.motorista_id) & (df['status'] != 'Entregue')]

        if entregas.empty:
            st.success("✅ Tudo limpo! Nenhuma entrega pendente.")
        else:
            for idx, row in entregas.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-entrega">
                            <p style='color:#ee4d2d; font-size:12px; margin:0;'>PEDIDO #{idx}</p>
                            <p style='font-size:18px; margin:5px 0;'><b>📍 {row['endereco']}</b></p>
                            <p style='color:#bbb; margin:0;'>Cliente: {row['cliente']} | Bairro: {row['bairro']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Funções de Ação (Tabs para organizar o espaço no celular)
                    tab_rota, tab_foto = st.tabs(["🗺️ Rota", "📸 Baixa"])
                    
                    with tab_rota:
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={str(row['endereco']).replace(' ', '+')}+Formosa+GO"
                        st.
