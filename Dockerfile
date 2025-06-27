# Usa imagen oficial de Python 3.12
FROM python:3.12

# Establece el directorio de trabajo
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

# Copia requirements y los instala
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código fuente, incluida la carpeta src/
COPY . /app/

# Copia el script de copiado y da permisos de ejecución
RUN chmod +x /app/scripts/copiar_archivo.sh

# Variables de entorno para Flask
ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Puerto expuesto
EXPOSE 5000

# Comando para iniciar la app como módulo
CMD ["python", "-m", "src.app"]
