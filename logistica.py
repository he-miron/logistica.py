import streamlit as st
import pandas as pd

# 1. Configurações de Página
st.set_page_config(page_title="FSA Parceiro - Formosa", layout="centered", page_icon="🚚")

# Estilo Visual SPX Dark (Otimizado para Mobile)
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
        background-color: #ee4d2d;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. URLs e Cache
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=10)
def load_and_clean_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. Lógica de Autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🚚 FSA LOGÍSTICA")
    user_input = st.text_input("ID do Motorista").strip().lower()
    pass_input = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        users_df = load_and_clean_data(USER_SHEET_URL)
        if not users_df.empty:
            valido = users_df[(users_df['usuario'].astype(str).str.lower() == user_input) & 
                              (users_df['senha'].astype(str) == pass_input)]
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.rerun()
        st.error("Credenciais inválidas.")

# 4. Painel de Entregas
else:
    st.sidebar.write(f"Motorista: **{st.session_state.motorista_id.upper()}**")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Entregas")
    df = load_and_clean_data(SHEET_URL)

    if not df.empty and 'entregador' in df.columns:
        motorista_atual = str(st.session_state.motorista_id).lower()
        entregas = df[(df['entregador'].astype(str).str.lower() == motorista_atual) & 
                      (df['status'].astype(str).str.lower() != 'entregue')]

        if entregas.empty:
            st.success("✅ Nenhuma entrega pendente!")
        else:
            for idx, row in entregas.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-entrega">
                            <small>ID: {idx}</small><br>
                            <b>📍 {row.get('endereco', 'Endereço não informado')}</b><br>
                            <span style='color: #bbb;'>Cliente: {row.get('cliente', 'N/A')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    tab1, tab2 = st.tabs(["🗺️ Rota", "📸 Baixa"])
                    
                    with tab1:
                        # Link do Google Maps corrigido para máxima compatibilidade
                        end_dest = f"{row.get('endereco', '')} Formosa GO"
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={end_dest.replace(' ', '+')}"
                        st.link_button("🚀 Iniciar GPS", maps_url)

                    with tab2:
                        # SOLUÇÃO PARA A CÂMERA: file_uploader abre a câmera nativa no celular
                        foto = st.file_uploader("Capturar Comprovante", type=['png', 'jpg', 'jpeg'], key=f"foto_{idx}")
                        
                        if foto:
                            st.image(foto, caption="Foto carregada", width=150)
                            
                        if st.button("Confirmar Entrega ✅", key=f"btn_{idx}"):
                            if foto:
                                st.success(f"Entrega {idx} finalizada!")
                                st.balloons()
                            else:
                                st.warning("Por favor, tire a foto antes de confirmar.")
    else:
        st.info("Aguardando carregamento da base de dados...")
