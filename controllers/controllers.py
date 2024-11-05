from io import BytesIO
import os
import re
import tempfile
import base64
import requests
import torch
import models.utils as utilsAIG
import firebase_admin
from PIL import Image
from dotenv import load_dotenv
from fastapi import (Depends, File, HTTPException, Request, Response,UploadFile, status)
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin import auth, firestore, credentials
from firebase_admin.exceptions import FirebaseError
from pydantic import BaseModel
from torch import autocast
from models.auth import obtener_usuario_actual, Usuario

class Token(BaseModel):
    access_token: str
    token_type: str

# Carga el modelo de Stable Diffusion
pipe = utilsAIG.descargar_modelo_stable_diffusion()

#Inicializamos Firebase
cred = credentials.Certificate("iagenerator-api-firebase-adminsdk-2y02s-7bde0acab5.json")
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
            "returnSecureToken": True,
        }
        response = requests.post(url, json=data)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        # Obtén el token de acceso de la respuesta que viene directamente de Firebase
        id_token = response.json()["idToken"]

        # Retornamos el token como cuerpo de respuesta del response y el tipo de autentificacion que se esta manejando.
        return {"access_token": id_token, "token_type": "bearer"}

    #Manejo de exepciones en consola.
    except requests.exceptions.RequestException as e:
        print(f"Error de autenticación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error de autenticación"
        )

#Raiz de entrada del servicio.
async def root():
    return {"message": "Hola! Bienvenido a la API de generación de imágenes."}

async def generar_imagen_te(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        # Convertimos el request a un objeto diferente extrayendo el cuerpo del json.
        data = await request.json()
        # extraemos el texto del anterior objeto
        texto = data.get("texto")

        # Manejamos un posible error si el cuerpo del json esta vacio.
        if not texto:
            raise HTTPException(status_code=400, detail="El campo 'texto' es requerido")

        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Genera la imagen con autocast si hay GPU; usa `torch.no_grad()` si solo hay CPU
        with autocast(device) if device == "cuda" else torch.no_grad():#El autocast trabaja la precisión mixta del modelo variando entre float16 y float32 optimizando el uso de memoria en la GPU
            image = pipe(texto).images[0] #Acá esta ingresando el promt como parametro para que el modelo empiece a trabajar.

        # Guardamos la imagen en un archivo temporal para luego mostrarla en el http
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            ruta_imagen = tmp.name

        # Leer el contenido de la imagen
        with open(ruta_imagen, "rb") as f:
            contenido_imagen = f.read()

        with open(ruta_imagen, "rb") as f:
            imagen_base64 = base64.b64encode(f.read()).decode()

        #TODO: generar una clase o función especializada a parte con este fragmento de codigo, para hacer que su mantenimiento sea modular y mas facil de realizar.
        doc_ref = db.collection("imagenes_texto").document()
        doc_ref.set(
            {
                "usuario_id": usuario_actual.username, #se almacena el uid del usuario que hizo la solicitud de la imagen.
                "prompt": texto, #Se envía como string el promt para ser almacenado.
                "imagen_base64": imagen_base64, #Se almacena la imagen en base64 que es un formato de String soportado por la BD
                "fecha_creacion": firestore.SERVER_TIMESTAMP,  # Usa la marca de tiempo del servidor
            }
        )
        
        # Devolver el contenido de la imagen como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generar_imagen_imagen(imagen: UploadFile = File(...), prompt: str = "A beautiful landscape", usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    try:
        print("Inicio de generación de imagen a imagen")

        # Leer y convertir la imagen de entrada
        imagen_bytes = await imagen.read()
        imagen_base = Image.open(BytesIO(imagen_bytes)).convert("RGB")
        print("Imagen base cargada y convertida")

        # Configuración de parámetros de generación
        strength = 0.75
        guidance_scale = 7.5

        # Realizar la transformación de imagen a imagen

        #Seleccion de hardaware disponible en el entorno para ejecutar el programa.
        device = "cuda" if torch.cuda.is_available() else "cpu"
        with autocast(device) if device == "cuda" else torch.no_grad():#El autocast trabaja la precisión mixta del modelo variando entre float16 y float32 optimizando el uso de memoria en la GPU
            imagen_generada = pipe(prompt=prompt, image=imagen_base, strength=strength, guidance_scale=guidance_scale).images[0] #Punto de entrada del promt y la imagen como referencia.
        print("Imagen generada exitosamente")

        # Guardar la imagen generada temporalmente
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            imagen_generada.save(tmp.name)
            ruta_imagen = tmp.name
        print("Imagen generada guardada temporalmente en", ruta_imagen)

        # Leer el contenido de la imagen generada para respuesta y conversión a base64
        with open(ruta_imagen, "rb") as f:
            contenido_imagen = f.read()
            imagen_generada_base64 = base64.b64encode(contenido_imagen).decode()

        

        # Guardar las imágenes y el prompt en Firestore
        #TODO: generar una clase o función especializada a parte con este fragmento de codigo, para hacer que su mantenimiento sea modular y mas facil de realizar.
        # Usa la instancia db importada desde firebase_config.py
        #FIXME: analizar mejor esta parte del codigo ya que esta generando problemas a la hora de almacenar informacion en la base de datos.
        #los archivos que esta recibiendo son muy pesados para Firestore y nos estan pidiendo que sean guardados en otro modulo llamado Storage
        #La implementacion de este codigo esta tardando un poco por los protocolos de validacion directa en Firebase, que hace que se generen
        #redundancias ciclicas y se obliga a re plantear el orden de todo el codigo.
        '''
        # Convertir la imagen base a base64
        imagen_base_base64 = base64.b64encode(imagen_bytes).decode()
        print("Conversiones a base64 completadas")

        db = firestore.client()
        doc_ref = db.collection('imagenes_imagen').document()
        doc_ref.set({
            'usuario_id': usuario_actual.username,
            'prompt': prompt,
            'imagen_base_base64': imagen_base_base64,
            'imagen_generada_base64': imagen_generada_base64,
            'fecha_creacion': firestore.SERVER_TIMESTAMP
        })
        print("Datos guardados en Firestore")
        '''
        # Devolver la imagen generada como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

    except Exception as e:
        print("Error al generar la imagen:", str(e))
        raise HTTPException(status_code=500, detail=f"Error al generar la imagen: {str(e)}")

#TODO: se tiene que implementar seguridad en este punto ya que la creación de usuarios se puede hacer sin ningun inconveniente y al quedar registrado el correo y la contraseña
#TODO: la generacion del token se realiza por defecto y esto hace que cualquier usuario pueda acceder al servicio en general.

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