# Usar a imagem oficial Python como base
FROM python:3.10-slim

# Criar diretório de trabalho
WORKDIR /app

# Copiar o requirements.txt para a imagem
COPY requirements.txt .

# Instalar as dependências do projeto com log detalhado
RUN pip install --no-cache-dir -r requirements.txt --progress-bar=off --log /tmp/pip-verbose.log

# Copiar o resto do código do projeto para a imagem
COPY . .

# Expôr a porta para o serviço da aplicação
EXPOSE 8000

# Comando para rodar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projeto_tcc.wsgi:application"]
