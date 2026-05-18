FROM python:3.12-slim
WORKDIR /app
COPY common/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/metrics.py .
COPY order/app.py .
EXPOSE 8003
CMD ["gunicorn", "-b", "0.0.0.0:8003", "app:app", "--workers", "2"]
