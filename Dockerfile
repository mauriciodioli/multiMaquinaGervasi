FROM python:3.12

WORKDIR /app

# Instala dependencias del sistema para pyodbc + SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Capa 3: Copiar solo el archivo de requisitos para aprovechar la caché
COPY src/requirements.txt .

# Capa 4: Instalar dependencias desde el archivo de requisitos
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y git

# Capa 6: Copiar todo el código fuente
COPY src/ .

# Capa 7: Comando por defecto para ejecutar la aplicación
CMD ["python", "./app.py"]

