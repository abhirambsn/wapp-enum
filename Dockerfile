FROM kalilinux/kali-rolling as builder
RUN apt update && apt install -y --no-install-recommends nmap python3 python3-pip
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r ./requirements.txt
COPY ./src /app/
ENTRYPOINT [ "python3", "main.py" ]