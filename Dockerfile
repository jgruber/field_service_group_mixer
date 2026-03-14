FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY index.html .
COPY server.py .

RUN mkdir -p data

VOLUME ["/app/data"]

EXPOSE 3000

CMD ["python", "server.py"]
