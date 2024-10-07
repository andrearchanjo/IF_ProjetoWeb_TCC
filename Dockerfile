# Usar a imagem oficial Python como base
FROM python:3.10-slim

# Instalar o Rust e ferramentas necessárias (se necessário)
RUN apt-get update && apt-get install -y \
    rustc \
    cargo \
    build-essential

# Instalar o gunicorn e django diretamente
RUN pip install gunicorn Django==5.1.1

# Criar diretório de trabalho
WORKDIR /app

# Copiar o requirements.txt para a imagem
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt --progress-bar=off -v

# Copiar o resto do código do projeto para a imagem
COPY . .

# Expôr a porta para o serviço da aplicação
EXPOSE 8000

# Comando para rodar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projeto_tcc.wsgi:application"]
