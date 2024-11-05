# Usar una imagen base de Python 3.12.4
FROM python:3.12.4

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt .

# Copiar el archivo .env.list
COPY env.list .

# Copiar el archivo JSON de Firebase al contenedor en la carpeta adecuada
COPY iagenerator-api-firebase-adminsdk-2y02s-7bde0acab5.json /app/

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer los puertos para Streamlit y FastAPI
EXPOSE 8501
EXPOSE 8000

# Comando para iniciar ambos servicios
CMD ["sh", "-c", "uvicorn views.views:app --host 0.0.0.0 --port 8000 & streamlit run views/frontend.py --server.port 8501"]
