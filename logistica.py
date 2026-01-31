import streamlit as st
import pandas as pd

# 1. Configurações de Página
st.set_page_config(page_title="SPX Parceiro - Formosa", layout="centered", page_icon="🚚")

# Estilo Visual SPX Dark
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

# 2. Inicialização de Memória
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.motorista_id = ""

# 3. URLs das Planilhas (Verifique se estão publicadas como CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=10)
def load_and_clean_data(url):
    try:
        df = pd.read_csv(url)
        # Limpeza pesada de colunas para evitar KeyError
        df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        return df
    except Exception as e:
        return pd.DataFrame()

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("SPX LOGÍSTICA")
    
    user_input = st.text_input("ID do Motorista").strip().lower()
    pass_input = st.text_input("Senha", type="password").strip()
    
    if st.button("ENTRAR"):
        users_df = load_and_clean_data(USER_SHEET_URL)
        if not users_df.empty and 'usuario' in users_df.columns:
            valido = users_df[(users_df['usuario'].astype(str) == user_input) & 
                              (users_df['senha'].astype(str) == pass_input)]
            
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.rerun()
            else:
                st.error("Usuário ou Senha incorretos.")
        else:
            # Login de emergência caso a planilha de usuários falhe
            if user_input == "admin" and pass_input == "123":
                st.session_state.autenticado = True
                st.session_state.motorista_id = "admin"
                st.rerun()
            else:
                st.error("Erro na base de dados. Verifique a coluna 'usuario' e 'senha'.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAINEL DE LOGÍSTICA ---
else:
    st.sidebar.title(f"🚚 {st.session_state.motorista_id.upper()}")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Entregas")
    
    df = load_and_clean_data(SHEET_URL)
    
    if not df.empty:
        # Verifica se as colunas essenciais existem após a limpeza
        colunas = df.columns.tolist()
        
        if 'entregador' in colunas and 'status' in colunas:
            # Filtro inteligente
            minhas_rotas = df[(df['entregador'].astype(str).str.lower() == st.session_state.motorista_id) & 
                              (df['status'].astype(str).str.lower() != 'entregue')]
            
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
                        
                        tab_gps, tab_baixa = st.tabs(["🗺️ GPS", "📸 Finalizar"])
                        
                        with tab_gps:
                            endereco = str(row.get('endereco', 'Formosa GO')).replace(' ', '+')
                            st.link_button("Abrir no Maps", f"https://www.google.com/maps/search/?api=1&query={endereco}", use_container_width=True)
                        
                        with tab_baixa:
                            foto = st.camera_input("Foto do Local/Comprovante", key=f"f_{idx}")
                            if st.button("Confirmar Entrega", key=f"b_{idx}"):
                                if foto:
                                    st.success("Entrega finalizada!")
                                    st.balloons()
                                else:
                                    st.warning("⚠️ Tire a foto para validar.")
        else:
            st.error(f"Erro de colunas! Planilha lida como: {colunas}")
            st.info("Certifique-se de ter as colunas: cliente, endereco, entregador, status")
    else:
        st.warning("Aguardando dados da planilha...")

st.markdown("<br><hr><center>Formosa Cases Logística v2.1</center>", unsafe_allow_html=True)
