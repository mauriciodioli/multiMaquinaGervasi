FROM python:3.12-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
 && mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
 && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
    | sed 's#deb \\[arch=amd64\\]#deb [signed-by=/etc/apt/keyrings/microsoft.gpg arch=amd64]#' \
    > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src    /app/src
COPY config /app/config
COPY config/.env /app/.env

COPY scripts/copiar_archivo.sh /scripts/copiar_archivo.sh
RUN chmod +x /scripts/copiar_archivo.sh

ENV PYTHONPATH=/app:/app/src

EXPOSE 5000

CMD ["python", "-m", "src.app"]