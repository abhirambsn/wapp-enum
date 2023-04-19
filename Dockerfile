FROM python:latest

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r ./requirements.txt
COPY ./src /app/

ENTRYPOINT [ "python3", "main.py" ]