FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código do agente
COPY . .

# Diretórios persistentes (montar como volumes em produção)
RUN mkdir -p .memory skills/dynamic skills/user

ENV PYTHONUNBUFFERED=1

# Modo padrão: API server na porta 8080
# Override com: docker run ... python server.py schedule --interval 3600 --task "..."
CMD ["python", "server.py", "api", "--port", "8080"]
