# syntax=docker/dockerfile:1

FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
EXPOSE 8080
CMD ["python", "-m", "google.adk.cli", "api_server", "--port", "8080", "--host", "0.0.0.0"]
