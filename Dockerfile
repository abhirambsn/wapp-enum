FROM python:latest

WORKDIR /app
COPY . /app/
ENTRYPOINT [ "python3", "main.py" ]