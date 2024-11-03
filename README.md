# API-IAGeneradorImágenes

Esta API, desarrollada con FastAPI, te permite generar imágenes a partir de texto utilizando el modelo Stable Diffusion.

## Funcionalidades:

* Recibe un prompt (texto) en una solicitud POST.
* Genera una imagen a partir del prompt usando Stable Diffusion.
* Devuelve la imagen generada directamente en la respuesta HTTP.

## Tecnologías utilizadas:

<div style="display: flex; justify-content: space-around;">
  <img src="https://cosasdedevs.com/media/sections/images/fastapi.png" alt="FastAPI" width="100px">
  <img src="https://miro.medium.com/v2/resize:fit:1400/1*Rbq9cDCJpGq7HKeNAeIitg.jpeg" alt="StableDiffusion" width="100px">
  <img src="https://quansight.com/wp-content/uploads/2023/09/PyTorch-logo.jpg" alt="PyTorch" width="100px">
</div>

* **FastAPI:** Framework web moderno y de alto rendimiento para construir APIs en Python.
* **Stable Diffusion:** Modelo de aprendizaje automático de última generación para la generación de imágenes a partir de texto.
* **PyTorch:** Librería de aprendizaje profundo que proporciona flexibilidad y velocidad para el entrenamiento y la inferencia de modelos como Stable Diffusion.


## Configuración:

1. **Clonar el repositorio:**

   ```bash
   git clone [https://github.com/KemmerDesign/API-IAGeneratorImages.git](https://github.com/KemmerDesign/API-IAGeneratorImages.git)
 
2. **Crear el Enviroment (Entorno)**

    Para crear un entorno virtual para este proyecto, se recomienda ejecutar el siguiente comando en la terminal:

     ```bash: python -m venv .venv```

    Para activar el entorno virtual, utiliza el siguiente comando (recuerda que debes estar en la misma carpeta donde creaste el entorno):

    ``` bash: .venv/Scripts/activate ```

    Esto activara el entorno de pruebas en el que se va a trabajar; ya teniendo el entorno activado debemos proceder a instalar las siguientes librerias que son indispensables para que el proyecto corra:

3. **Instalar librerías necesarias para este proyecto**

    ```
    pip install fastapi uvicorn
    pip install diffusers transformers
    pip install torch torchvision torchaudio
    pip install torch
    pip install python-dotenv
    pip install python-multipart
    pip install accelerate
    python.exe -m pip install --upgrade pip
    ```
    Asegúrate de estar en la terminal, en el directorio donde se encuentra el archivo **main.py**, y con el entorno virtual activado. Luego, ejecuta el siguiente comando para iniciar el servidor de FastAPI:

4. **Lanzando la API**

    Debes revisar que estando en la terminal estas en el mismo directorio en el que esta el archivo **main.py**, y adicional verifica que tienes el entorno de ejecución activado, el comando para lanzar el servidor es el siguiente:

    ```bash: uvicorn main:app --reload```
    

    ![Mi imagen](img\readme\launch_api.png)

    Cuando ejecutes el comando si es la primera vez tardara un tiempo en lo que descarga el modelo Stable Diffusion que se usara para desplegar esta aplicación, debes tener paciencia:

    ![Mi imagen](img\readme\api_loading.png)

    Una vez se halla terminado de ejecutar el servidor deberia estar en funcionando correctamente:

    ![Mi imagen](img\readme\api_fullcharged.png)

5. **Postman Testing**

    Para empezar a probar se sugiere usar postman o un software similar, ten en cuenta que la direccion ip en la que el servidor se ejecuta es la siguiente ```http://127.0.0.1:8000```, la primera solicitud de imagen que se va a realiar va a ser por medio de un **promt**, como el metodo que vamos a recibir es un request lo que haremos es enviar un json con el cuerpo del **promt**.
    
    ## Disclaimer
    Por ahora el promt que debe recibir esta API tiene que estar redactado en ingles, de otra manera nos va a arrojar error.
    ---

    La direccion que usaremos para enviar el primer request es la siguiente: ```http://127.0.0.1:8000/generar-imagen-texto``` y como cuerpo se debe enviar un json ```{"texto": "a dog with a hat"}```:

    ![Mi imagen](img\readme\1-postman-testing.png)

    Cuando le des al boton **Send** se hara la solicitud formal al servidor, el proceso va a tardar y dependera de si en el computador en el que se le esta ejecutando tiene una o varias **GPU** que soporten **CUDA**, y si el caso es el contrario ejecutara directamente desde la **CPU**, se debe recordar que la generacion de imagen es una operación de redes convulucionales que matematicamente le cuesta mucho a la **CPU** realizar, por eso la mejor opcion es ejecutar este proyecto en un pc con una **GPU** de muy buenas prestaciones que soporte los **CUDA-CORES**.

    Cuando se envie el request se verda de esta manera en **Postman**:

    ![Mi imagen](https://drive.google.com/file/d/1Tw-KiQFh5XD521eRWGGXyRePrctoGSUX/view?usp=sharing)

    Y de esta manera en el ide o en este caso en **VSCode**:

    ![Mi imagen](img\readme\1-B-postman-testing.png)

    Al terminar la generación de imagen por medio de un promt se vera asi en **Postman**:

    ![Mi imagen](img\readme\1-C-postman-testing.png)

    La imagen que esta abajo es la que el modelo de **Stable Diffusion** creo.


    ## To-Do

    1. Crear el metodo especializado para generar una imagen a partir de una imagen.
    2. Implementar seguridad a la API.
    3. Realizar conexiones con bases de datos non-sql.
    4. Implementar StreamLit para prototipar un front-end muy rapido.
    5. Dockerizar el proyecto.
    6. Desplegar el proyecto en algún servicio cloud como **AWS**, **Google Platform**.
