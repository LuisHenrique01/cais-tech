FROM python:3.10

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências
RUN pip install -r requirements.txt

# Copia todos os arquivos do diretório atual para o diretório de trabalho no contêiner
COPY . .

# Expõe a porta em que a aplicação estará escutando
EXPOSE 8000

# Define o comando para iniciar o servidor da aplicação
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
