FROM python:3.12
WORKDIR /app

# 1) Dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https unixodbc unixodbc-dev git \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2) Python libs
COPY src/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 3) Tu código
COPY src    /app/src
COPY config /app/config
COPY config/.env /app/.env

# 4) Scripts de utilidad
COPY scripts /app/scripts
RUN chmod +x /app/scripts/*.sh

# 5) Python path
ENV PYTHONPATH=/app:/app/src

# 6) Red
EXPOSE 5000

# 7) Inicio
CMD ["python", "-m", "src.app"]

