FROM python:3.12

WORKDIR /app

# Instala dependencias de sistema
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https unixodbc unixodbc-dev \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  && apt-get clean && rm -rf /var/lib/apt/lists/* \
  && apt-get install -y git

# Copia requirements e instala
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TODO el contenido de tu proyecto (incluye src/, config/, app.py…)
COPY . .

# Asegura que /app está en PYTHONPATH
ENV PYTHONPATH=/app

# Arranca el módulo tal cual lo escribiste
CMD ["python", "-m", "src.app"]
