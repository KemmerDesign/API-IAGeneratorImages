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
    pip install python-jose[cryptography]
    python.exe -m pip install --upgrade pip
    ```
    Asegúrate de estar en la terminal, en el directorio donde se encuentra el archivo **main.py**, y con el entorno virtual activado. Luego, ejecuta el siguiente comando para iniciar el servidor de FastAPI:

4. **Lanzando la API**

    Debes revisar que estando en la terminal estas en el mismo directorio en el que esta el archivo **main.py**, y adicional verifica que tienes el entorno de ejecución activado, el comando para lanzar el servidor es el siguiente:

    ```bash: uvicorn main:app --reload```
    

    ![Mi imagen](![alt text](image.png))

    Cuando ejecutes el comando si es la primera vez tardara un tiempo en lo que descarga el modelo Stable Diffusion que se usara para desplegar esta aplicación, debes tener paciencia:

    ![Mi imagen](https://i.imgur.com/w25tLH0.png)

    Una vez se halla terminado de ejecutar el servidor deberia estar en funcionando correctamente:

    ![Mi imagen](https://i.imgur.com/bWFzx0u.png)

5. **Postman Testing text-to-image**

    Para empezar a probar se sugiere usar postman o un software similar, ten en cuenta que la direccion ip en la que el servidor se ejecuta es la siguiente ```http://127.0.0.1:8000```, la primera solicitud de imagen que se va a realiar va a ser por medio de un **promt**, como el metodo que vamos a recibir es un request lo que haremos es enviar un json con el cuerpo del **promt**.

    Como la seguridad ya fue implementada de forma parcial para empezar a hacer los test se tendra que tener en cuenta lo siguiente:

    **EndPoint '/token'**

    Desde acá gestionaremos los token necesarios para poder usar la aplicación en este punto el usuario estara simulado y hardcodeado mientras que se realizan las conexiones pertinentes a la base de datos, empezamos entonces por solcitar el token desde postman:

    Debemos usar un **Body** del tipo **x-www-form-urlencoded** que nos va a permitir almacenar el token de autenticación, y le pasamos los parametros **username | testuser** y **password | cualquier_contraseña**, que en este momento son los datos hardcodeados en la API.
    
    ![Mi imagen](https://i.imgur.com/6qRcUKk.png)

    Para poder usar cualquier EndPoint de manera adecuada se debe asegurar que en las solicitudes ingreses el token generado, de otra forma te va a lanzar credential_exception:
    
    ![Mi imagen](https://i.imgur.com/VPuXT0O.png)

    Y en el cuerpo **raw** puedes enviar el JSON con el promt:
    
    ![Mi imagen](https://i.imgur.com/tEEhslR.png)

    ## Disclaimer
    Por ahora el promt que debe recibir esta API tiene que estar redactado en ingles, de otra manera nos va a arrojar error.
    ---

    La direccion que usaremos para enviar el primer request es la siguiente: ```http://127.0.0.1:8000/generar-imagen-texto``` y como cuerpo se debe enviar un json ```{"texto": "a dog with a hat"}```:

    ![Mi imagen](https://i.imgur.com/7Y5tl12.png)

    Cuando le des al boton **Send** se hara la solicitud formal al servidor, el proceso va a tardar y dependera de si en el computador en el que se le esta ejecutando tiene una o varias **GPU** que soporten **CUDA**, y si el caso es el contrario ejecutara directamente desde la **CPU**, se debe recordar que la generacion de imagen es una operación de redes convulucionales que matematicamente le cuesta mucho a la **CPU** realizar, por eso la mejor opcion es ejecutar este proyecto en un pc con una **GPU** de muy buenas prestaciones que soporte los **CUDA-CORES**.

    Cuando se envie el request se verda de esta manera en **Postman**:

    ![Mi imagen](https://i.imgur.com/vUkJL5s.png)

    Y de esta manera en el ide o en este caso en **VSCode**:

    ![Mi imagen](https://i.imgur.com/vUkJL5s.png)

    Al terminar la generación de imagen por medio de un promt se vera asi en **Postman**:

    ![Mi imagen](https://i.imgur.com/qApt5kV.png)

    La imagen que esta abajo es la que el modelo de **Stable Diffusion** creo.

## Disclaimer

Algunas pruebas se estaran relaizandoi en un entorno controlado como lo es **Google Colab** ya que localmente el computador en el que se esta desarrollando la prueba no tiene el hardware sufiente para apoyarse en el modelo de **stable-diffusion-v1-5** para poder generar las imagenes que se requieren, ya que exige un gran consumo de unidades de procesamiento **CUDA-CORES**

---
## Image to Image (Code-Test)

Como se menciona en el disclaimer el computardor en el que se estan desarrollando las pruebas no tiene la capacidad de computo para poder generar las imagenes de una forma rapida, lo que se hizo fue pagar por una cuenta **Google Colab PRO** con el proposito de poder aprovechar de mejor manera la potencia de estos entornos; Esto generara en este proyecto dos formas de testing una de forma local (lento) y otro en un cuaderno o notebook con el paso a paso de como hacerlo y la explicacion de las tecnologías escogidas para ese proposito, a continuacion se relaciona el cuaderno generado para que sea usado:

```git clone https://github.com/KemmerDesign/IAGeneratorGC.git```

Tenga en cuenta que la asignación de recursos por lo menos en **Google Colab** se da bajo demanda, esto quiere decir que si en el momento en el que se hagan las pruebas y usted no disponga de una cuenta PRO, es muy probable que le asignen un entorno de solo ejecucion de **CPU**, si se lo puede permitir es mejor que pague por unidades de computo o un plan mensual.

A continuacion se muestran las pruebas realizadas desde **Google Colab Pro** de la API:

El cuaderno en este punto viene el paso a paso y las tecnologias que se van a usar, por favor ejecutelo de manera sistematica, **pero tenga en cuenta que el usamos NGrok para generar una tunelizacion para poder hacer el testing desde PostMan (en este caso)** asi tenga en cuenta este paso:

![Mi imagen](https://i.imgur.com/XaywPVL.png)

En los recuadros rojo de la iamgen se muestra el link publico que genera NGrok para poder hacer los test desde **PostMan**:

![Mi imagen](https://i.imgur.com/tVtNN9Z.png)

Estos imagenes son algunos **response** que se generaron desde **Google Colab**:
**URL para enviar el texto como (json) de este endpoint**

```https://2f96-34-125-9-203.ngrok-free.app/generar-imagen-texto ```

![Mi imagen](https://i.imgur.com/Y6a2p79.png)

**URL para enviar el Body/from-data de este endpoint**

```https://2f96-34-125-9-203.ngrok-free.app/generar-imagen-imagen```
![Mi imagen](https://i.imgur.com/gtpBEVW.png)

Como se puede ver en la imagen se aprovecha el link de NGrok para correlo en postman, sin embargo el modelo tiene una fuerte tendencia a alucinar, **los parametros se deben reevaluar para validar que sucede o por que suce esto.**


## To-Do
1. Implementar seguridad a la API.
1. Realizar conexiones con bases de datos non-sql.
2. Implementar StreamLit para prototipar un front-end muy rapido.
3. Dockerizar el proyecto.
4. Desplegar el proyecto en algún servicio cloud como **AWS**, **Google Platform**.
