import streamlit as st
import pandas as pd

# 1. Configurações de Página
st.set_page_config(page_title="SPX Parceiro - Logística", layout="centered", page_icon="🚚")

# 2. Inicialização do Estado de Login
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.motorista_id = ""

# 3. Estilo Visual (CSS SPX Parceiro)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .login-container { background: #1e1e1e; padding: 40px; border-radius: 20px; border-top: 5px solid #ee4d2d; text-align: center; }
    .card-pedido { background: #262626; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #ee4d2d; }
    .stButton>button { background-color: #ee4d2d; color: white; font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LOGIN ---
def realizar_login(user, pw):
    # Base de dados simples de motoristas (Pode expandir conforme crescer)
    motoristas_validos = {
        "moto_joao": "123",
        "moto_pedro": "456",
        "admin": "formosa2026"
    }
    if user in motoristas_validos and motoristas_validos[user] == pw:
        st.session_state.autenticado = True
        st.session_state.motorista_id = user
        return True
    return False

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("SPX LOGÍSTICA")
    st.subheader("Login do Parceiro")
    
    usuario = st.text_input("Usuário (ID)")
    senha = st.text_input("Senha", type="password")
    
    if st.button("ACESSAR SISTEMA"):
        if realizar_login(usuario, senha):
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA RESTRITA DO MOTORISTA ---
else:
    # Sidebar com informações do motorista
    st.sidebar.title(f"👤 {st.session_state.motorista_id.upper()}")
    st.sidebar.write("Status: Online 🟢")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📋 Minhas Entregas")
    
    # Conexão com a Planilha
    SHEET_URL = "SUA_URL_DA_PLANILHA_AQUI"
    
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # FILTRO MÁGICO: Mostra apenas os pedidos deste motorista
        meus_pedidos = df[df['entregador'] == st.session_state.motorista_id]
        
        if meus_pedidos.empty:
            st.info("Nenhuma entrega pendente para você no momento.")
        else:
            for idx, row in meus_pedidos.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-pedido">
                            <p style='color:#ee4d2d; font-size:12px; margin:0;'>PEDIDO #{idx}</p>
                            <p style='font-size:18px; margin:5px 0;'><b>📍 {row['endereco']}</b></p>
                            <p style='color:#bbb; margin:0;'>Bairro: {row.get('bairro', 'Centro')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Roteirização e Finalização
                    col1, col2 = st.columns(2)
                    with col1:
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={str(row['endereco']).replace(' ', '+')}+Formosa+GO"
                        st.link_button("🗺️ Abrir GPS", maps_url)
                    with col2:
                        # Abre os detalhes para tirar foto e bipar
                        with st.expander("✅ Finalizar"):
                            st.camera_input("Foto do Comprovante", key=f"cam_{idx}")
                            if st.button("Confirmar", key=f"fin_{idx}"):
                                st.success("Entrega Concluída!")
    except Exception as e:
        st.warning("Adicione a coluna 'entregador' na sua planilha para ver os pedidos.")
