# Stage 1: Build environment
FROM python:3.8.3-buster AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.8.3-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY . .

RUN chmod +x deploy_and_run.sh

CMD ["./deploy_and_run.sh"]
