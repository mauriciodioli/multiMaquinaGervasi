FROM python:3.12

# 1. Define el directorio de trabajo
WORKDIR /app

# 2. Instala dependencias de sistema (pyodbc + SQL Server)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Copia sólo requirements para cachear la instalación de pip
COPY src/requirements.txt .

# 4. Instala las librerías Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instala git (si lo necesitas)
RUN apt update && apt install -y git

# 6. Copia el paquete src completo dentro de /app/src
COPY src ./src

# 7. Arranca la app usando su módulo
CMD ["python", "-m", "src.app"]
