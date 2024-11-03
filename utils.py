from diffusers import StableDiffusionPipeline
import torch

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