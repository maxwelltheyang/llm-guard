FROM python:3.9-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python -m pip install --no-cache-dir .

# Use a smaller base image for running the app
FROM python:3.9-alpine
WORKDIR /app
COPY --from=builder /app/* .
CMD ["python", "your_script.py"]
