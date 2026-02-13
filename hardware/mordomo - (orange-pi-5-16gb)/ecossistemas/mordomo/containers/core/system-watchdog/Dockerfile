FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# O Watchdog precisa rodar como root para acessar /sys/class/thermal e Docker Socket
USER root

CMD ["python", "src/main.py"]
