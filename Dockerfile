FROM kalilinux/kali-rolling as builder
RUN apt update && apt install -y --no-install-recommends nmap python3 python3-pip nikto
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r ./requirements.txt
COPY ./src /app/
RUN mkdir -p /logs
ENV LOG_FILE_PATH=/logs
ENTRYPOINT [ "python3", "main.py" ]