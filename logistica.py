import streamlit as st
import pandas as pd

# 1. Configurações de Página
st.set_page_config(page_title="SPX Parceiro - Login", layout="centered", page_icon="🚚")

# 2. Sistema de Autenticação Simples
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# 3. Estilo Visual (CSS Customizado)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .login-box {
        background-color: #1e1e1e;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #ee4d2d;
        text-align: center;
    }
    .stButton>button { background-color: #ee4d2d; color: white; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown('<div style="text-align:center;"><h1 style="color:#ee4d2d;">🚚 SPX LOGÍSTICA</h1><p>Painel do Motorista Parceiro</p></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        usuario = st.text_input("ID do Motorista")
        senha = st.text_input("Senha de Acesso", type="password")
        
        if st.button("ENTRAR NO SISTEMA"):
            # Aqui você define o login (ex: motorista1 / formosa2026)
            if usuario == "moto1" and senha == "123":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas. Fale com a central.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- APP DE LOGÍSTICA (PÁGINA RESTRITA) ---
else:
    st.sidebar.button("Sair / Logout", on_click=lambda: st.session_state.update({"autenticado": False}))
    
    st.title("🚚 Entregas do Dia")
    st.write(f"Bem-vindo, Parceiro **{usuario if 'usuario' in locals() else 'Motorista'}**")

    # Conteúdo de Logística (Barcode + Câmera + Rota)
    tabs = st.tabs(["📋 Rotas", "📸 Comprovante", "📊 Ganhos"])

    with tabs[0]:
        st.subheader("Pedidos em Formosa")
        # Simulação de card de entrega
        st.info("📍 Rua 14, Centro - Entregar para: Maria")
        if st.button("Abrir Rota no Maps"):
            st.write("Abrindo GPS...")

    with tabs[1]:
        st.subheader("Finalizar Entrega")
        barcode = st.text_input("Escanear Código de Barras")
        foto = st.camera_input("Foto do Comprovante")
        if st.button("Confirmar Entrega"):
            st.success("Dados enviados com sucesso!")

    with tabs[2]:
        st.metric("Ganhos de Hoje", "R$ 120,50", "+ R$ 15,00")
        st.write("Total de 8 entregas concluídas.")
