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

# ───────── 2. Dependencias Python ─────────
COPY src/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ───────── 3. Código ─────────
COPY src    /app/src
COPY config /app/config
COPY config/.env /app/.env

RUN set -o allexport \
    && source /app/.env \
    && set +o allexport
# Copia el script de copiado y da permisos de ejecución
COPY scripts/copiar_archivo.sh /scripts/copiar_archivo.sh
RUN chmod +x /scripts/copiar_archivo.sh

# ───────── 4. PYTHONPATH ─────────
ENV PYTHONPATH=/app:/app/src

# Puerto expuesto
EXPOSE 5000 

CMD ["python", "-m", "src.app"]
