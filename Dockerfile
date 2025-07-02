FROM python:3.12

# 1. Directorio de trabajo real
WORKDIR /src

# 2. Dependencias de sistema…
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https unixodbc unixodbc-dev \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  && apt-get clean && rm -rf /var/lib/apt/lists/* \
  && apt-get install -y git

# 3. Instala requirements.txt
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia TODO el código en /src
COPY src/ .

# 5. Asegura que Python busque en /src
ENV PYTHONPATH=/src

# 6. Arranca tu app como módulo
CMD ["python", "-m", "src.app"]

