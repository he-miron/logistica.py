import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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
        background-color: #ee4d2d;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_email_com_foto(foto_arquivo, info_entrega, motorista):
    destinatario = "mironfsa@gmail.com"
    remetente_email = "seu_email@gmail.com" # Coloque seu e-mail de envio aqui
    remetente_senha = "sua_senha_de_app"    # Coloque sua SENHA DE APP aqui

    msg = MIMEMultipart()
    msg['From'] = remetente_email
    msg['To'] = destinatario
    msg['Subject'] = f"Comprovante de Entrega - {info_entrega['id']} - Motorista: {motorista}"

    corpo = f"""
    <h3>Nova Baixa de Entrega - FSA Logística</h3>
    <b>Motorista:</b> {motorista}<br>
    <b>ID da Entrega:</b> {info_entrega['id']}<br>
    <b>Endereço:</b> {info_entrega['endereco']}<br>
    <b>Cliente:</b> {info_entrega['cliente']}
    """
    msg.attach(MIMEText(corpo, 'html'))

    # Anexar a foto
    img = MIMEImage(foto_arquivo.read())
    img.add_header('Content-Disposition', 'attachment', filename="comprovante.jpg")
    msg.attach(img)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente_email, remetente_senha)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# 2. Persistência de Login (Não sai ao atualizar)
if 'autenticado' not in st.session_state:
    # Verifica se o ID já está na URL (caso o usuário tenha dado F5)
    query_id = st.query_params.get("user_id")
    if query_id:
        st.session_state.autenticado = True
        st.session_state.motorista_id = query_id
    else:
        st.session_state.autenticado = False

# 3. URLs e Cache
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

# --- TELA DE LOGIN ---
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
                # Salva na URL para não perder o login ao atualizar
                st.query_params["user_id"] = user_input
                st.rerun()
        st.error("Credenciais inválidas.")

# --- PAINEL DE ENTREGAS ---
else:
    st.sidebar.write(f"Motorista: **{st.session_state.motorista_id.upper()}**")
    if st.sidebar.button("Sair / Trocar Conta"):
        st.session_state.autenticado = False
        st.query_params.clear() # Limpa a URL ao sair
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
                    
                    t1, t2 = st.tabs(["🗺️ Rota", "📸 Baixa"])
                    
                    with t1:
                        end_dest = f"{row.get('endereco', '')} Formosa GO"
                        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={end_dest.replace(' ', '+')}"
                        st.link_button("🚀 Abrir GPS", maps_url)

                    with t2:
                        foto = st.file_uploader("Tirar Foto do Comprovante", type=['jpg', 'jpeg', 'png'], key=f"f_{idx}")
                        
                        if st.button("Confirmar Entrega ✅", key=f"b_{idx}"):
                            if foto:
                                with st.spinner("Enviando comprovante para central..."):
                                    info = {
                                        "id": idx,
                                        "endereco": row.get('endereco', 'N/A'),
                                        "cliente": row.get('cliente', 'N/A')
                                    }
                                    sucesso = enviar_email_com_foto(foto, info, st.session_state.motorista_id)
                                    
                                    if sucesso:
                                        st.success("Entrega finalizada e e-mail enviado!")
                                        st.balloons()
                                    else:
                                        st.error("Erro ao enviar e-mail. Verifique a conexão.")
                            else:
                                st.warning("⚠️ Você precisa tirar a foto para confirmar.")
