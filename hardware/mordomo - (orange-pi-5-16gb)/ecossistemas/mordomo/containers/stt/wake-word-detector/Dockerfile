FROM python:3.11-slim

# Metadados
LABEL maintainer="Mordomo Team"
LABEL description="Wake Word Detector - OpenWakeWord-based wake word detection"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ ./src/

# Cria diretório para modelos (serão baixados em runtime)
RUN mkdir -p /app/models

# Porta de métricas
EXPOSE 8001

# Comando padrão
CMD ["python", "src/main.py"]
