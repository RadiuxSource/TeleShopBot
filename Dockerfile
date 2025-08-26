FROM python:3.12.7-slim-bookworm

RUN apt update && apt upgrade -y && apt-get install -y git curl bash python3-pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -U pip wheel && pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

CMD python3 -m Modules