import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configurações de Página
st.set_page_config(page_title="FSA Parceiro", layout="centered", page_icon="🚚")

# Estilo Visual SPX Dark
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .card-entrega {
        background-color: #1e1e1e; padding: 15px; border-radius: 12px;
        border-left: 5px solid #ee4d2d; margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #ee4d2d; color: white; font-weight: bold; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. PERSISTÊNCIA DE LOGIN (Não desloga nunca)
if 'autenticado' not in st.session_state:
    # Tenta recuperar o login pela URL (caso o motorista atualize a página)
    params = st.query_params
    if "user" in params:
        st.session_state.autenticado = True
        st.session_state.motorista_id = params["user"]
    else:
        st.session_state.autenticado = False

# 3. URLs das Planilhas
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=5)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🚚 FSA LOGÍSTICA")
    u = st.text_input("ID do Motorista").strip().lower()
    p = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        users = load_data(USER_SHEET_URL)
        if not users.empty:
            valido = users[(users['usuario'].astype(str).str.lower() == u) & (users['senha'].astype(str) == p)]
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = u
                st.query_params["user"] = u # Salva na URL
                st.rerun()
        st.error("Usuário ou senha incorretos.")

# --- PAINEL DE ENTREGAS ---
else:
    st.sidebar.write(f"Motorista: **{st.session_state.motorista_id.upper()}**")
    if st.sidebar.button("Sair"):
        st.query_params.clear()
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Entregas")
    df = load_data(SHEET_URL)
    
    if not df.empty and 'entregador' in df.columns:
        motorista = st.session_state.motorista_id.lower()
        minhas = df[df['entregador'].astype(str).str.lower() == motorista]
        
        for idx, row in minhas.iterrows():
            if str(row.get('status')).lower() == 'entregue': continue
            
            with st.container():
                st.markdown(f"""
                <div class="card-entrega">
                    📍 <b>{row.get('endereco', 'Endereço N/A')}</b><br>
                    <small>Cliente: {row.get('cliente', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                t1, t2 = st.tabs(["🗺️ Rota", "📸 Finalizar"])
                
                with t1:
                    # Rota Direta no Google Maps
                    end_limpo = str(row.get('endereco')).replace(' ', '+')
                    st.link_button("🚀 Abrir Google Maps", f"https://www.google.com/maps/dir/?api=1&destination={end_limpo}+Formosa+GO")
                
                with t2:
                    # Câmera traseira via file_uploader
                    foto = st.file_uploader("Capturar Foto do Comprovante", type=['jpg','png','jpeg'], key=f"f_{idx}")
                    
                    if foto:
                        st.image(foto, width=150)
                        
                        # Prepara o texto para o WhatsApp
                        texto_zap = f"✅ *BAIXA DE ENTREGA - FSA*\n\n" \
                                    f"*Motorista:* {st.session_state.motorista_id.upper()}\n" \
                                    f"*ID:* {idx}\n" \
                                    f"*Local:* {row.get('endereco')}\n" \
                                    f"*Cliente:* {row.get('cliente')}"
                        
                        texto_url = urllib.parse.quote(texto_zap)
                        
                        # --- COLOQUE O NÚMERO DE WHATSAPP DA CENTRAL AQUI ---
                        # Exemplo: 5561999999999
                        NUMERO_CENTRAL = "556191937857" 
                        
                        st.link_button("📲 Enviar Foto p/ Central (WhatsApp)", 
                                       f"https://wa.me/{NUMERO_CENTRAL}?text={texto_url}")
                        
                        st.info("Clique no botão acima para abrir o Zap e anexe a foto que você tirou.")

    else:
        st.warning("Nenhuma entrega encontrada para você hoje.")

st.markdown("<br><center><small>FSA Logística v5.0 - Formosa GO</small></center>", unsafe_allow_html=True)
