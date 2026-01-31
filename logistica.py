import streamlit as st
import pandas as pd

# 1. Configurações de Página e Estilo SPX Parceiro
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

# 3. URLs das Planilhas (Substitua pelos seus links CSV do Google Sheets)
# Aba de Pedidos/Entregas
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
# Aba de Usuários/Motoristas
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

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
        users_df = load_data(USER_SHEET_URL)
        if not users_df.empty:
            # Validação na aba 'usuarios' da planilha
            valido = users_df[(users_df['usuario'].astype(str) == user_input) & 
                              (users_df['senha'].astype(str) == pass_input)]
            
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.rerun()
            else:
                st.error("Login ou Senha incorretos.")
        else:
            st.warning("Base de usuários não encontrada. Verifique o link da planilha.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # PAINEL DE LOGÍSTICA (LOGADO)
    st.sidebar.title(f"🚚 {st.session_state.motorista_id.upper()}")
    if st.sidebar.button("Sair/Logout"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Entregas")
    
    df = load_data(SHEET_URL)
    
    if not df.empty:
        # Verifica se as colunas essenciais existem
        if 'entregador' in df.columns:
            # Filtro: Pedidos deste motorista que NÃO estão como 'Entregue'
            minhas_rotas = df[(df['entregador'] == st.session_state.motorista_id) & (df['status'] != 'entregue')]
            
            if minhas_rotas.empty:
                st.success("✅ Nenhuma entrega pendente para você!")
            else:
                for idx, row in minhas_rotas.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class="card-entrega">
                                <p style='color:#ee4d2d; font-size:12px; margin:0;'>ENTREGA #{idx}</p>
                                <p style='font-size:18px; margin:5px 0;'><b>📍 {row.get('endereco', 'Endereço Indisponível')}</b></p>
                                <p style='color:#bbb; margin:0;'>Cliente: {row.get('cliente', 'Ver no Zap')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        tab_rota, tab_baixa = st.tabs(["🗺️ GPS", "📸 Finalizar"])
                        
                        with tab_rota:
                            end_formatado = str(row.get('endereco', '')).replace(' ', '+')
                            link_maps = f"https://www.google.com/maps/search/?api=1&query={end_formatado}+Formosa+GO"
                            st.link_button("Abrir Google Maps", link_maps, use_container_width=True)
                        
                        with tab_baixa:
                            foto = st.camera_input("Foto do Comprovante", key=f"foto_{idx}")
                            if st.button("Confirmar Recebimento", key=f"btn_{idx}"):
                                if foto:
                                    st.success("Entrega finalizada com sucesso!")
                                    st.balloons()
                                else:
                                    st.warning("⚠️ É obrigatório tirar a foto da fachada/comprovante.")
        else:
            st.error("A coluna 'entregador' não foi encontrada na planilha de pedidos.")
    else:
        st.info("Aguardando sincronização com a planilha central...")

st.markdown("<br><hr><center>Formosa Cases Express v2.0</center>", unsafe_allow_html=True)
