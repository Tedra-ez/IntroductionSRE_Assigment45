import os
import time
from functools import wraps

import psycopg2
from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "order-service"


def db_config():
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "sre_shop"),
        "user": os.getenv("POSTGRES_USER", "sre"),
        "password": os.getenv("POSTGRES_PASSWORD", "sre_password"),
    }


def get_conn():
    return psycopg2.connect(**db_config())


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(64) NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 1,
                    status VARCHAR(32) NOT NULL DEFAULT 'created'
                );
                """
            )
        conn.commit()


def track(endpoint):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = 500
            try:
                resp = fn(*args, **kwargs)
                status = resp[1] if isinstance(resp, tuple) else 200
                return resp
            finally:
                REQUEST_LATENCY.labels(request.method, endpoint).observe(
                    time.perf_counter() - start
                )
                REQUEST_COUNT.labels(request.method, endpoint, str(status)).inc()

        return wrapper

    return decorator


@app.route("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return jsonify({"status": "healthy", "service": SERVICE}), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc), "service": SERVICE}), 503


@app.route("/metrics")
def metrics():
    return metrics_response()


@app.route("/api/v1/orders", methods=["GET"])
@track("/api/v1/orders")
def list_orders():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, user_id, product_id, quantity, status FROM orders ORDER BY id DESC LIMIT 50;")
            rows = cur.fetchall()
    orders = [
        {"id": r[0], "user_id": r[1], "product_id": r[2], "quantity": r[3], "status": r[4]}
        for r in rows
    ]
    return jsonify({"orders": orders, "service": SERVICE}), 200


@app.route("/api/v1/orders", methods=["POST"])
@track("/api/v1/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    if not user_id or not product_id:
        return jsonify({"error": "user_id and product_id required"}), 400
    quantity = int(data.get("quantity", 1))
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id, status;",
                (user_id, product_id, quantity),
            )
            row = cur.fetchone()
        conn.commit()
    return jsonify({"id": row[0], "status": row[1], "service": SERVICE}), 201


try:
    init_db()
except Exception:
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8003")))
