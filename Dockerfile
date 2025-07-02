FROM python:3.12

# 1) Define /app como carpeta de trabajo
WORKDIR /app

# 2) Instala deps de sistema para pyodbc + SQL Server y git
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https unixodbc unixodbc-dev git \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3) Copia e instala los requirements
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copia TODO el proyecto en /app
#    Esto traerá:
#      - config/
#      - src/
#      - cualquier script o fichero extra
COPY . .

# 5) Asegura que Python busque en /app
ENV PYTHONPATH=/app

# 6) Arranca tu aplicación
CMD ["python", "-m", "src.app"]


