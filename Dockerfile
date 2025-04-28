# Usa imagen oficial de Python 3.12
FROM python:3.12

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /src

# Instala las librerías necesarias del sistema para pyodbc
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev

# Copia primero los requirements para aprovechar el cache de Docker
COPY requirements.txt .

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del proyecto
# Capa 6: Copiar todo el código fuente
COPY src/ .

# Variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Exponer el puerto que Flask va a usar
EXPOSE 5000

# Comando por defecto
CMD ["python", "./app.py"]
