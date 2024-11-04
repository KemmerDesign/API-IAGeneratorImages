from fastapi import HTTPException, UploadFile, File, Response, Request, status
from torch import autocast
import torch
import tempfile
from io import BytesIO
from PIL import Image
from fastapi import Depends, HTTPException, status
import models.utils as utilsAIG  # archivo creado para manejar para manipular funciones secundarias.
from models.auth import obtener_usuario_actual, Usuario  # Importa desde auth.py
from fastapi.security import OAuth2PasswordRequestForm
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.exceptions import FirebaseError
from pydantic import BaseModel
import re
import os
import requests
from dotenv import load_dotenv
import base64


class Token(BaseModel):
    access_token: str
    token_type: str

# Carga el modelo de Stable Diffusion
pipe = utilsAIG.descargar_modelo_stable_diffusion()

#Inicializamos Firebase
cred = credentials.Certificate(".venv/iagenerator-api-firebase-adminsdk-2y02s-7bde0acab5.json")
firebase_app = firebase_admin.initialize_app(cred)

#Obtenemos una instancia de la base de datos:
db = firestore.client()

load_dotenv(dotenv_path='env.list')
API_KEY = os.getenv("FIREBASE_API_KEY")

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Construye la solicitud a la API REST
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        data = {
            "email": form_data.username,
            "password": form_data.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=data)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        # Obtén el token de acceso de la respuesta
        id_token = response.json()['idToken']
        
        # Genera tu propio token de acceso (opcional)

        return {"access_token": id_token, "token_type": "bearer"}

    except requests.exceptions.RequestException as e:
        print(f"Error de autenticación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error de autenticación")

async def root():
    return {"message": "Hola! Bienvenido a la API de generación de imágenes."}


async def generar_imagen_te(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        #Convertimos el request a un objeto diferente extrayendo el cuerpo del json.
        data = await request.json()
        #extraemos el texto del anterior objeto
        texto = data.get("texto")

        #Manejamos un posible error si el cuerpo del json esta vacio.
        if not texto:
            raise HTTPException(status_code=400, detail="El campo 'texto' es requerido")


        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Genera la imagen con autocast si hay GPU; usa `torch.no_grad()` si solo hay CPU
        with autocast(device) if device == "cuda" else torch.no_grad():
            image = pipe(texto).images[0]

        # Guardamos la imagen en un archivo temporal para luego mostrarla en el http
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            ruta_imagen = tmp.name

        # Leer el contenido de la imagen
        with open(ruta_imagen, "rb") as f:
            contenido_imagen = f.read()
        
        with open(ruta_imagen, "rb") as f:
            imagen_base64 = base64.b64encode(f.read()).decode()

        db = firestore.client()
        doc_ref = db.collection('imagenes_texto').document()  # Crea un nuevo documento con un ID autogenerado
        doc_ref.set({
            'usuario_id': usuario_actual.username,
            'prompt': texto,
            'imagen_base64': imagen_base64,
            'fecha_creacion': firestore.SERVER_TIMESTAMP  # Usa la marca de tiempo del servidor
        })

        # Devolver el contenido de la imagen como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generar_imagen_imagen(imagen: UploadFile = File(...), prompt: str = "A beautiful landscape", usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        # Leer y convertir la imagen de entradas
        imagen_bytes = await imagen.read()
        imagen_base = Image.open(BytesIO(imagen_bytes)).convert("RGB")

        # Configura los parámetros de generación, por ejemplo el nivel de fuerza (strength) de la transformación
        strength = 0.75  # Puedes ajustar este valor para cambiar el nivel de modificación de la imagen
        guidance_scale = 7.5  # Ajusta este parámetro para controlar la creatividad

        # Realizar la transformación de imagen a imagen
        with autocast("cuda" if torch.cuda.is_available() else "cpu"):
            imagen_generada = pipe(prompt=prompt, image=imagen_base, strength=strength, guidance_scale=guidance_scale).images[0]

        # Guardar la imagen generada en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            imagen_generada.save(tmp.name)
            ruta_imagen = tmp.name

        # Leer el contenido de la imagen generada
        with open(ruta_imagen, "rb") as f:
            contenido_imagen = f.read()

        with open(ruta_imagen, "rb") as f:
            imagen_generada_base64 = base64.b64encode(f.read()).decode()

        imagen_base_base64 = base64.b64encode(imagen_bytes).decode()

        # Guardar las imágenes y el prompt en Firestore
        db = firestore.client()
        doc_ref = db.collection('imagenes_imagen').document()
        doc_ref.set({
            'usuario_id': usuario_actual.username,
            'prompt': prompt,
            'imagen_base_base64': imagen_base_base64,
            'imagen_generada_base64': imagen_generada_base64,
            'fecha_creacion': firestore.SERVER_TIMESTAMP
        })

        # Devolver la imagen generada como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Registro de usuarios en la base de datos Firebase/firestore database
async def registrar_usuario(request: Request):
    try:
        data = await request.json()
        correo = data.get("correo")
        passwordA = data.get("contraseña")

        # Validar el formato del correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            raise HTTPException(status_code=400, detail="Correo electrónico inválido")

        # Validar la complejidad de la contraseña (ejemplo simple)
        if len(passwordA) < 6:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")

        # Crear el usuario en Firebase Authentication
        usuario = auth.create_user(
            email=correo,
            password=passwordA
        )

        # Guardar la información adicional del usuario en Firestore (opcional)

        return {"message": f"Usuario creado con ID: {usuario.uid}"}

    except FirebaseError as e:
        if e.code == 'auth/email-already-exists':
            raise HTTPException(status_code=400, detail="Ya existe una cuenta con este correo electrónico") from e
        # Manejar otros errores de Firebase Authentication
        raise HTTPException(status_code=500, detail="Error al registrar usuario") from e
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar usuario") from e