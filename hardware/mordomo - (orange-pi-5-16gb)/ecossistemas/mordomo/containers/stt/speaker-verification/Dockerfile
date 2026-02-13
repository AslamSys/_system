FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ ./src/

# Cria diretórios para volumes (config e data serão montados)
RUN mkdir -p /app/config /app/data/embeddings /app/data/samples

# Expõe porta (para métricas futuras)
EXPOSE 8001

# Comando para iniciar serviço
CMD ["python", "src/main.py"]
