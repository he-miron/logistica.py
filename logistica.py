import streamlit as st
import urllib.parse
import requests
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FSA Entrega", page_icon="🚚")

# --- FUNÇÃO UPLOAD (IMGBB) ---
def fazer_upload_imgbb(foto_arquivo):
    API_KEY = "1cb13947c3ee801f4cef2fbda3a42c59"
    try:
        img_b64 = base64.b64encode(foto_arquivo.getvalue())
        res = requests.post("https://api.imgbb.com/1/upload", {"key": API_KEY, "image": img_b64})
        return res.json()["data"]["url"]
    except:
        return None

# --- INTERFACE ---
st.title("🚚 FSA Logística - Baixa Rápida")
st.markdown("Preencha os dados e tire a foto para gerar o comprovante.")

# Campos manuais para o motorista (Mais simples que banco de dados)
motorista = st.text_input("Seu Nome/ID")
endereco = st.text_input("Endereço da Entrega")
foto = st.camera_input("📸 Tire a foto do comprovante")

if foto and motorista and endereco:
    with st.spinner("Gerando link da foto..."):
        link_foto = fazer_upload_imgbb(foto)
        
        if link_foto:
            st.success("Foto processada com sucesso!")
            
            # Monta a mensagem
            mensagem = f"✅ *ENTREGA REALIZADA*\n\n" \
                       f"*Motorista:* {motorista.upper()}\n" \
                       f"*Local:* {endereco}\n" \
                       f"*Foto:* {link_foto}"
            
            texto_url = urllib.parse.quote(mensagem)
            NUMERO_CENTRAL = "556191937857"
            
            # Botão de Envio
            st.link_button("📲 ENVIAR PARA WHATSAPP", f"https://wa.me/{NUMERO_CENTRAL}?text={texto_url}")
        else:
            st.error("Erro ao gerar link da foto. Tente novamente.")

elif foto:
    st.warning("⚠️ Por favor, preencha seu nome e o endereço antes de enviar.")
