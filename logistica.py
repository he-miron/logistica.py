import streamlit as st
import pandas as pd
import urllib.parse
import requests
import base64

# 1. Configurações de Página
st.set_page_config(page_title="FSA Parceiro", layout="centered", page_icon="🚚")

# --- NOVO: URL DO SCRIPT PARA APAGAR LINHA ---
SCRIPT_URL_APAGAR = "https://script.google.com/macros/s/AKfycbxS_d7UXSaaFv0NxbXVaaNy8SkBCOJlPS_AWPwPl-m1b4yQUvDi_sq1Um5s_kH_Dhlj/exec"

# --- FUNÇÃO PARA GERAR LINK DA IMAGEM (ImgBB) ---
def fazer_upload_imagem(imagem_arquivo):
    API_KEY = "1cb13947c3ee801f4cef2fbda3a42c59" 
    url = "https://api.imgbb.com/1/upload"
    try:
        img_base64 = base64.b64encode(imagem_arquivo.getvalue())
        payload = {"key": API_KEY, "image": img_base64}
        res = requests.post(url, payload)
        return res.json()["data"]["url"]
    except:
        return None

# --- FUNÇÃO PARA APAGAR DO GOOGLE SHEETS ---
def apagar_linha_planilha(id_linha):
    try:
        requests.get(f"{SCRIPT_URL_APAGAR}?id={id_linha}")
        return True
    except:
        return False

# 2. Persistência de Login
if 'autenticado' not in st.session_state:
    params = st.query_params
    if "user" in params:
        st.session_state.autenticado = True
        st.session_state.motorista_id = params["user"]
    else:
        st.session_state.autenticado = False

# 3. URLs de Leitura
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?output=csv"
USER_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhJW43nfokHKiBwhu64dORzbzD8m8Haxy8tEbGRsysr8JG1Wq8s7qgRfHT5ZLLUBkAuHzUJFKODEDZ/pub?gid=221888638&single=true&output=csv"

@st.cache_data(ttl=2) # TTL menor para atualizar rápido após apagar
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- INTERFACE ---
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
                st.query_params["user"] = u
                st.rerun()
        st.error("Erro nas credenciais.")
else:
    st.sidebar.button("Sair", on_click=lambda: (st.session_state.update({"autenticado": False}), st.query_params.clear()))
    st.title("📋 Minhas Entregas")
    
    df = load_data(SHEET_URL)
    if not df.empty and 'entregador' in df.columns:
        minhas = df[df['entregador'].astype(str).str.lower() == st.session_state.motorista_id.lower()]
        
        for idx, row in minhas.iterrows():
            with st.container():
                st.markdown(f'<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #ee4d2d; margin-bottom:10px;">📍 <b>{row.get("endereco")}</b></div>', unsafe_allow_html=True)
                
                t1, t2 = st.tabs(["🗺️ Rota", "📸 Finalizar"])
                
                with t1:
                    end = str(row.get('endereco')).replace(' ', '+')
                    st.link_button("🚀 GPS", f"https://www.google.com/maps/dir/?api=1&destination={end}+Formosa+GO")
                
                with t2:
                    foto = st.file_uploader("📸 Comprovante", type=['jpg','png','jpeg'], key=f"f_{idx}")
                    
                    if st.button("FINALIZAR E APAGAR ✅", key=f"btn_{idx}"):
                        if foto:
                            with st.spinner("Processando baixa..."):
                                link_da_foto = fazer_upload_imagem(foto)
                                if link_da_foto:
                                    # 1. Tenta apagar da planilha
                                    if apagar_linha_planilha(idx):
                                        texto = f"✅ *ENTREGA FINALIZADA E BAIXADA*\n\n*Motorista:* {st.session_state.motorista_id.upper()}\n*Local:* {row.get('endereco')}\n*Foto:* {link_da_foto}"
                                        texto_url = urllib.parse.quote(texto)
                                        NUMERO_CENTRAL = "556191937857"
                                        
                                        st.success("Dados apagados da planilha!")
                                        st.link_button("📲 Comunicar WhatsApp", f"https://wa.me/{NUMERO_CENTRAL}?text={texto_url}")
                                        st.cache_data.clear() # Limpa o cache para sumir da tela
                                    else:
                                        st.error("Erro ao apagar dados. Verifique o Script.")
                        else:
                            st.warning("Tire a foto antes!")
