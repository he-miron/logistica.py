import streamlit as st
import pandas as pd

# 1. Configurações de Página e Estilo
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

# 2. Inicialização do Estado
# Verifica se existe a combinação usuario + senha na planilha
            valido = users_df[(users_df['usuario'].astype(str) == user_input) & 
                              (users_df['senha'].astype(str) == pass_input)]
            
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = user_input
                st.rerun()
            else:
                st.error("Usuário ou senha não encontrados na base.")
        except Exception as e:
            st.error(f"Erro ao acessar base de usuários: {e}")

# 3. Função de Dados
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=0&single=true&output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

# --- LÓGICA DE TELAS ---

if not st.session_state.autenticado:
    # TELA DE LOGIN
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("SPX LOGÍSTICA")
    
    user_input = st.text_input("ID do Motorista")
    pass_input = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        # Login Temporário enquanto você não configura a aba de usuários
        if user_input == "moto1" and pass_input == "123":
            st.session_state.autenticado = True
            st.session_state.motorista_id = user_input
            st.rerun()
        else:
            st.error("Credenciais inválidas.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # PAINEL DO MOTORISTA
    st.sidebar.title(f"🚚 {st.session_state.motorista_id.upper()}")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Rotas")
    
    try:
        df = load_data(SHEET_URL)
        
        # Filtro por motorista (Garanta que a coluna 'entregador' existe na planilha)
        if 'entregador' in df.columns:
            entregas = df[(df['entregador'] == st.session_state.motorista_id) & (df['status'] != 'Entregue')]
        else:
            entregas = df # Mostra tudo se a coluna não existir ainda

        if entregas.empty:
            st.success("✅ Nenhuma entrega pendente!")
        else:
            for idx, row in entregas.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-entrega">
                            <p style='color:#ee4d2d; font-size:12px; margin:0;'>PEDIDO #{idx}</p>
                            <p style='font-size:18px; margin:5px 0;'><b>📍 {row.get('endereco', 'Endereço não cadastrado')}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    tab_rota, tab_foto = st.tabs(["🗺️ Rota", "📸 Baixa"])
                    
                    with tab_rota:
                        end = str(row.get('endereco', '')).replace(' ', '+')
                        st.link_button("Abrir Maps", f"https://www.google.com/maps/search/?api=1&query={end}+Formosa+GO", use_container_width=True)
                    
                    with tab_foto:
                        foto = st.camera_input("Foto do Comprovante", key=f"cam_{idx}")
                        if st.button("Confirmar Entrega", key=f"btn_{idx}"):
                            if foto:
                                st.success("Entrega finalizada!")
                                st.balloons()
                            else:
                                st.warning("Tire a foto primeiro!")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
