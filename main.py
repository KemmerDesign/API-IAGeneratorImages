from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Request
from diffusers import StableDiffusionPipeline
from torch import autocast
import torch
import tempfile
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import utils as utilsAIG #archivo creado para manejar para manipular funciones secundarias.
from utils_security import crear_access_token, obtener_usuario_actual, Usuario, obtener_usuario# Importar funciones de utils_security.py
from fastapi.security import OAuth2PasswordRequestForm


# Carga el modelo de Stable Diffusion
pipe = utilsAIG.descargar_modelo_stable_diffusion()

app = FastAPI()

async def autenticar_usuario(username: str, password: str):
    # Simula la autenticación del usuario
    # En este ejemplo, se autentica al usuario si el nombre de usuario es "testuser" y la contraseña es "cualquier_contraseña"
    usuario_correcto = await obtener_usuario(username)
    if usuario_correcto is not None and password == "cualquier_contraseña":
        return usuario_correcto
    return None

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Aquí debes implementar la lógica para autenticar al usuario
    # con tu base de datos (que veremos más adelante)
    usuario = await autenticar_usuario(form_data.username, form_data.password)  
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = crear_access_token(data={"sub": usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "Hola! Bienvenido a la API de generación de imágenes."}

@app.post("/generar-imagen-texto")
async def generar_imagen(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
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

        # Devolver el contenido de la imagen como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generar-imagen-imagen")
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

        # Devolver la imagen generada como respuesta
        return Response(content=contenido_imagen, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))