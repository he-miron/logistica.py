import streamlit as st
import pytesseract
from PIL import Image
import re
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(page_title="FSA Roteirizador", layout="wide")

# Interface com sua Logo
st.sidebar.image("https://r.jina.ai/i/6f9a0c...", width=150)
st.sidebar.title("FSA Roteirização")
menu = st.sidebar.radio("Navegação", ["Escanear Etiquetas", "Mapa de Rota"])

# Banco de dados temporário (na sessão)
if "entregas" not in st.session_state:
    st.session_state.entregas = []

def extrair_cep(imagem):
    # Converte imagem para escala de cinza para melhorar o OCR
    texto = pytesseract.image_to_string(imagem, lang='por')
    # Procura por padrões de CEP (00000-000 ou 00000000)
    padrao_cep = re.search(r'\d{5}-?\d{3}', texto)
    return padrao_cep.group(0) if padrao_cep else None

if menu == "Escanear Etiquetas":
    st.header("📸 Leitor de Etiquetas (FSA Express)")
    
    arquivo_foto = st.camera_input("Tire foto da etiqueta")
    
    if arquivo_foto:
        img = Image.open(arquivo_foto)
        with st.spinner('Lendo endereço...'):
            cep_detectado = extrair_cep(img)
            
            if cep_detectado:
                st.success(f"CEP Identificado: {cep_detectado}")
                nome_cliente = st.text_input("Nome do Cliente (Opcional)")
                
                if st.button("Confirmar Entrega"):
                    st.session_state.entregas.append({
                        "cep": cep_detectado,
                        "cliente": nome_cliente or "Cliente Avulso"
                    })
                    st.toast("Adicionado à lista!")
            else:
                st.error("Não foi possível ler o CEP. Tente aproximar mais a câmera.")

    # Exibe lista atual
    if st.session_state.entregas:
        st.write("---")
        st.subheader("📦 Entregas na Fila")
        df = pd.DataFrame(st.session_state.entregas)
        st.table(df)
        if st.button("Limpar Lista"):
            st.session_state.entregas = []
            st.rerun()

elif menu == "Mapa de Rota":
    st.header("🚚 Rota Otimizada")
    
    if not st.session_state.entregas:
        st.warning("Nenhuma entrega registrada.")
    else:
        # Aqui o sistema organizaria os CEPs por proximidade
        st.info("Visualizando pontos de entrega em Formosa-GO")
        
        # Mapa centralizado em Formosa
        m = folium.Map(location=[-15.53, -47.33], zoom_start=14)
        
        for idx, item in enumerate(st.session_state.entregas):
            folium.Marker(
                [-15.53 - (idx*0.005), -47.33 - (idx*0.005)], # Simulação de geolocalização por CEP
                popup=f"Parada {idx+1}: {item['cliente']}\nCEP: {item['cep']}",
                tooltip=f"Entrega {idx+1}"
            ).add_to(m)
            
        st_folium(m, width=1000)
