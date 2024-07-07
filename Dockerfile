FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Basic DB healthcheck
COPY ./scripts/healthcheck.sh /app/healthcheck.sh
RUN chmod +x /app/healthcheck.sh
HEALTHCHECK --interval=120s --timeout=10s --start-period=5s --retries=3 CMD /app/healthcheck.sh

ENTRYPOINT ["python", "main.py"]
