FROM python:3.12-slim
WORKDIR /app
COPY common/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/metrics.py .
COPY auth/app.py .
ENV PORT=8001
EXPOSE 8001
CMD ["gunicorn", "-b", "0.0.0.0:8001", "app:app", "--workers", "2"]
