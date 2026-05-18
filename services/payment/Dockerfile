FROM python:3.12-slim
WORKDIR /app
COPY common/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/metrics.py .
COPY payment/app.py .
EXPOSE 8004
CMD ["gunicorn", "-b", "0.0.0.0:8004", "app:app", "--workers", "2"]
