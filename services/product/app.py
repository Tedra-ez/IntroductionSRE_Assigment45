import os
import time
from functools import wraps

from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "product-service"
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Headphones", "price": 149.99},
    {"id": 3, "name": "Keyboard", "price": 79.99},
]


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
    return jsonify({"status": "healthy", "service": SERVICE}), 200


@app.route("/metrics")
def metrics():
    return metrics_response()


@app.route("/api/v1/products")
@track("/api/v1/products")
def list_products():
    return jsonify({"products": PRODUCTS, "service": SERVICE}), 200


@app.route("/api/v1/products/<int:product_id>")
@track("/api/v1/products/<id>")
def get_product(product_id):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return jsonify(p), 200
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8002")))
