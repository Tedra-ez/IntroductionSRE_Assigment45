FROM python:3.12-slim
WORKDIR /app
COPY common/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/metrics.py .
COPY notification/app.py .
EXPOSE 8005
CMD ["gunicorn", "-b", "0.0.0.0:8005", "app:app", "--workers", "2"]
