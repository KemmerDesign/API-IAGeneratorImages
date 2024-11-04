import streamlit as st
import requests

st.title("Generador de imágenes con IA")

# Formulario de inicio de sesión
st.header("Inicio de sesión")
username = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    if username and password:
        response = requests.post(
            "http://127.0.0.1:8000/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token
            st.success("Inicio de sesión exitoso!")
        else:
            st.error("Error de autenticación. Verifica tus credenciales.")
    else:
        st.warning("Por favor, introduce tu correo electrónico y contraseña.")


# Formulario para la generación de imágenes a partir de texto
st.header("Generar imagen a partir de texto")
texto = st.text_area("Introduce el texto:")
if st.button("Generar imagen"):
    if "token" in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(
            "http://127.0.0.1:8000/generar-imagen-texto", 
            json={"texto": texto},
            headers=headers
        )
        if response.status_code == 200:
            st.image(response.content)
        else:
            st.error(f"Error al generar la imagen: {response.status_code}")
    else:
        st.warning("Por favor, inicia sesión para generar imágenes.")

# Formulario para la generación de imágenes a partir de una imagen
st.header("Generar imagen a partir de una imagen")
imagen = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])
prompt = st.text_input("Introduce el prompt:")
if st.button("Generar imagen a partir de imagen"):
    if imagen is not None and prompt:
        files = {"imagen": imagen}
        if "token" in st.session_state:
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.post(
                "http://127.0.0.1:8000/generar-imagen-imagen", 
                files=files, 
                data={"prompt": prompt},
                headers=headers
            )
            if response.status_code == 200:
                st.image(response.content)
            else:
                st.error(f"Error al generar la imagen: {response.status_code}")
        else:
            st.warning("Por favor, inicia sesión para generar imágenes.")
    else:
        st.warning("Por favor, sube una imagen e introduce un prompt.")