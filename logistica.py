import streamlit as st
import pandas as pd
import requests

# 1. Configurações de Página
st.set_page_config(page_title="FSA Parceiro - Formosa", layout="centered", page_icon="🚚")

# Estilo Visual SPX Dark
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .card-entrega {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #ee4d2d;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #ee4d2d; color: white; font-weight: bold; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Persistência de Login (Não desloga ao atualizar)
if 'autenticado' not in st.session_state:
    query_id = st.query_params.get("user_id")
    if query_id:
        st.session_state.autenticado = True
        st.session_state.motorista_id = query_id
    else:
        st.session_state.autenticado = False

# 3. Função de Envio Direto (Telegram)
def enviar_telegram(foto_arquivo, mensagem):
    # --- INSIRA SEUS DADOS AQUI ---
    TOKEN = "SEU_TOKEN_DO_BOT_AQUI"
    CHAT_ID = "SEU_ID_DO_TELEGRAM_AQUI"
    # ------------------------------
    
    url_foto = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {'photo': foto_arquivo.getvalue()}
    data = {'chat_id': CHAT_ID, 'caption': mensagem}
    
    try:
        response = requests.post(url_foto, files=files, data=data)
        return response.status_code == 200
    except:
        return False

# 4. URLs e Cache
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=5)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- INTERFACE ---
if not st.session_state.autenticado:
    st.title("🚚 FSA LOGÍSTICA")
    user_input = st.text_input("ID do Motorista").strip().lower()
    pass_input = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        users_df = load_data(USER_SHEET_URL)
        if not users_df.empty:
            valido = users_df[(users_df['usuario'].astype(str).str.lower() == user_input) & 
                              (users_df['senha'].astype(str) == pass_input)]
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.query_params["user_id"] = user_input
                st.rerun()
        st.error("Credenciais inválidas.")
else:
    st.sidebar.write(f"Motorista: **{st.session_state.motorista_id.upper()}**")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

    st.title("📋 Minhas Entregas")
    df = load_data(SHEET_URL)

    if not df.empty and 'entregador' in df.columns:
        motorista_atual = str(st.session_state.motorista_id).lower()
        entregas = df[(df['entregador'].astype(str).str.lower() == motorista_atual) & 
                      (df['status'].astype(str).str.lower() != 'entregue')]

        for idx, row in entregas.iterrows():
            with st.container():
                st.markdown(f'<div class="card-entrega"><b>📍 {row.get("endereco", "N/A")}</b></div>', unsafe_allow_html=True)
                t1, t2 = st.tabs(["🗺️ Rota", "📸 Baixa"])
                
                with t1:
                    end = f"{row.get('endereco', '')} Formosa GO".replace(' ', '+')
                    st.link_button("🚀 Iniciar GPS", f"https://www.google.com/maps/dir/?api=1&destination={end}")

                with t2:
                    foto = st.file_uploader("Tirar Foto", type=['jpg','png'], key=f"f_{idx}")
                    if st.button("Finalizar Entrega", key=f"b_{idx}"):
                        if foto:
                            msg = f"✅ ENTREGA FINALIZADA\nMotorista: {st.session_state.motorista_id}\nLocal: {row.get('endereco')}"
                            if enviar_telegram(foto, msg):
                                st.success("Foto enviada para a central!")
                                st.balloons()
                            else:
                                st.error("Erro ao enviar. Verifique o Token/ID.")
                        else:
                            st.warning("Tire a foto primeiro!")
