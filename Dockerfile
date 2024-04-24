FROM python:3.11-slim

WORKDIR /app

RUN mkdir config

COPY . .

RUN pip install --no-cache-dir py-cord

VOLUME ["/app/config"]

CMD ["python", "main.py"]
