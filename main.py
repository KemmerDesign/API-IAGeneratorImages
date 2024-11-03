from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Request
from diffusers import StableDiffusionPipeline
from torch import autocast
import torch
import tempfile
from pydantic import BaseModel
from PIL import Image


def descargar_modelo_stable_diffusion():
    """
    Descarga el modelo de Stable Diffusion desde Hugging Face Hub usando diffusers.
    """
    print("Descargando modelo desde Hugging Face Hub...")
    if torch.cuda.is_available():
        # Si hay GPU, carga el modelo en `float16`
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
        pipe = pipe.to("cuda")
    else:
        # Si solo hay CPU, carga el modelo en `float32`
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        pipe = pipe.to("cpu")
    print("Modelo descargado correctamente.")
    return pipe


# Carga el modelo de Stable Diffusion
pipe = descargar_modelo_stable_diffusion()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hola! Bienvenido a la API de generación de imágenes."}

@app.post("/generar-imagen-texto")
async def generar_imagen(request: Request):
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
