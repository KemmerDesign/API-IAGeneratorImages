FROM python:3.12.4

WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala Supervisord
RUN apt-get update && apt-get install -y supervisor

EXPOSE 8000

# Crea un archivo de configuración para Supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Comando para iniciar Supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]