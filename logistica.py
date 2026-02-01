import streamlit as st
import pandas as pd
import urllib.parse
import requests
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FSA Parceiro", layout="centered", page_icon="🚚")

# Estilo Visual Dark SPX
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .card-entrega {
        background-color: #1e1e1e; padding: 18px; border-radius: 12px;
        border-left: 6px solid #ee4d2d; margin-bottom: 15px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background-color: #ee4d2d; color: white; font-weight: bold; 
        border-radius: 8px; width: 100%; height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CONEXÃO E API ---

def conectar_google_sheets():
    """Conecta na planilha com permissão de edição/deleção"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Tenta ler dos Secrets (Nuvem) primeiro, se não achar, busca o arquivo local
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
            
        client = gspread.authorize(creds)
        # ID da sua planilha extraído da URL informada
        ID_PLANILHA = "1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ"
        return client.open_by_key(ID_PLANILHA).get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Erro de Conexão: Verifique as credenciais e o compartilhamento da planilha. ({e})")
        return None

def upload_imgbb(foto_arquivo):
    """Faz upload da foto e retorna o link direto"""
    API_KEY = "1cb13947c3ee801f4cef2fbda3a42c59"
    try:
        img_b64 = base64.b64encode(foto_arquivo.getvalue())
        res = requests.post("https://api.imgbb.com/1/upload", {"key": API_KEY, "image": img_b64})
        return res.json()["data"]["url"]
    except:
        return None

# --- LÓGICA DE LOGIN ---

if 'autenticado' not in st.session_state:
    query_user = st.query_params.get("user")
    if query_user:
        st.session_state.autenticado = True
        st.session_state.motorista_id = query_user
    else:
        st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🚚 FSA LOGÍSTICA")
    u = st.text_input("ID do Motorista").strip().lower()
    p = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        USER_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"
        try:
            users_df = pd.read_csv(USER_CSV)
            users_df.columns = [c.strip().lower() for c in users_df.columns]
            valido = users_df[(users_df['usuario'].astype(str).str.lower() == u) & (users_df['senha'].astype(str) == p)]
            
            if not valido.empty:
                st.session_state.autenticado = True
                st.session_state.motorista_id = u
                st.query_params["user"] = u
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        except:
            st.error("Erro ao validar usuários.")

# --- TELA PRINCIPAL ---
else:
    st.sidebar.write(f"Conectado como: **{st.session_state.motorista_id.upper()}**")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.query_params.clear()
        st.rerun()

    st.title("📋 Entregas Pendentes")
    
    sheet = conectar_google_sheets()
    
    if sheet:
        # Obtém todos os dados atuais da planilha
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        df.columns = [c.strip().lower() for c in df.columns]
        
        motorista_logado = st.session_state.motorista_id.lower()
        entregas_filtradas = df[df['entregador'].astype(str).str.lower() == motorista_logado]

        if entregas_filtradas.empty:
            st.success("✅ Nenhuma entrega pendente para você!")
        else:
            for idx, row in entregas_filtradas.iterrows():
                with st.container():
                    st.markdown(f'<div class="card-entrega">📍 <b>{row.get("endereco", "N/A")}</b><br><small>Cliente: {row.get("cliente", "N/A")}</small></div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        end_gps = str(row.get('endereco')).replace(' ', '+')
                        st.link_button("🗺️ Abrir Rota", f"https://www.google.com/maps/dir/?api=1&destination={end_gps}+Formosa+GO")
                    
                    with col2:
                        foto = st.file_uploader("📸 Foto", type=['jpg','jpeg','png'], key=f"foto_{idx}")
                    
                    if st.button("CONCLUIR ENTREGA ✅", key=f"btn_{idx}"):
                        if foto:
                            with st.spinner("Excluindo registro e salvando comprovante..."):
                                url_foto = upload_imgbb(foto)
                                if url_foto:
                                    # gspread inicia na linha 1 e tem cabeçalho, então linha = index + 2
                                    sheet.delete_rows(int(idx) + 2)
                                    
                                    msg_zap = f"✅ *ENTREGA FINALIZADA*\n\n*Motorista:* {motorista_logado.upper()}\n*Endereço:* {row.get('endereco')}\n*Comprovante:* {url_foto}"
                                    url_zap = f"https://wa.me/556191937857?text={urllib.parse.quote(msg_zap)}"
                                    
                                    st.success("Baixa realizada com sucesso!")
                                    st.link_button("📲 Notificar WhatsApp", url_zap)
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Erro ao enviar imagem.")
                        else:
                            st.warning("É obrigatório tirar a foto para finalizar!")
    else:
        st.warning("Aguardando conexão com o servidor Google...")

st.markdown("<br><center><small>FSA Logística v10.0 - Formosa GO</small></center>", unsafe_allow_html=True)
