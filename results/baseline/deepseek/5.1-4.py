# Example Dockerfile with multi-stage build
FROM python:3.9 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/pip /usr/local/bin/pip
COPY . .
CMD ["python", "app.py"]
