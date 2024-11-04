from fastapi import FastAPI, Depends, Request, UploadFile, File
from models.auth import obtener_usuario_actual, Usuario  
from fastapi.security import OAuth2PasswordRequestForm
from controllers.controllers import generar_imagen_imagen, generar_imagen_te, login_for_access_token, registrar_usuario  # Asegúrate de importar la función correcta
from pydantic import BaseModel


app = FastAPI()


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)  # Llama a la función en controllers.py

@app.post("/generar-imagen-texto")
async def generar_imagen_texto_view(request: Request, usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return await generar_imagen_te(request, usuario_actual)  # Llamar a la función correcta

@app.post("/generar-imagen-imagen")
async def generar_imagen_imagen_view(imagen: UploadFile = File(...), prompt: str = "A beautiful landscape", usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return await generar_imagen_imagen(imagen, prompt, usuario_actual)

@app.post("/registrar_usuario")  # Endpoint en views.py
async def registrar_usuario_view(request: Request):
    return await registrar_usuario(request)  # Llamar a la función en controllers.py