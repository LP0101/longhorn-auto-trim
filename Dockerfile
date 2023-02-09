FROM python:3.10-slim

RUN mkdir /app
COPY * /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT["python3", "auto_trim_api.py"]