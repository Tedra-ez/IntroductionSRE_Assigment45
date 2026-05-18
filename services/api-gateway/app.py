import os
import time
from functools import wraps

import requests
from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "api-gateway"

UPSTREAMS = {
    "auth": os.getenv("AUTH_URL", "http://auth-service:8001"),
    "products": os.getenv("PRODUCT_URL", "http://product-service:8002"),
    "orders": os.getenv("ORDER_URL", "http://order-service:8003"),
    "payments": os.getenv("PAYMENT_URL", "http://payment-service:8004"),
    "notifications": os.getenv("NOTIFICATION_URL", "http://notification-service:8005"),
    "profiles": os.getenv("USER_PROFILE_URL", "http://user-profile-service:8006"),
}


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


def proxy(base, path, method="GET", json_body=None):
    url = f"{base.rstrip('/')}{path}"
    resp = requests.request(method, url, json=json_body, timeout=5)
    return jsonify(resp.json() if resp.content else {}), resp.status_code


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": SERVICE}), 200


@app.route("/metrics")
def metrics():
    return metrics_response()


@app.route("/api/v1/login", methods=["POST"])
@track("/api/v1/login")
def login():
    return proxy(UPSTREAMS["auth"], "/api/v1/login", "POST", request.get_json())


@app.route("/api/v1/products")
@track("/api/v1/products")
def products():
    return proxy(UPSTREAMS["products"], "/api/v1/products")


@app.route("/api/v1/orders", methods=["GET", "POST"])
@track("/api/v1/orders")
def orders():
    if request.method == "POST":
        return proxy(UPSTREAMS["orders"], "/api/v1/orders", "POST", request.get_json())
    return proxy(UPSTREAMS["orders"], "/api/v1/orders")


@app.route("/api/v1/payments", methods=["POST"])
@track("/api/v1/payments")
def payments():
    return proxy(UPSTREAMS["payments"], "/api/v1/payments", "POST", request.get_json())


@app.route("/api/v1/notify", methods=["POST"])
@track("/api/v1/notify")
def notify():
    return proxy(UPSTREAMS["notifications"], "/api/v1/notify", "POST", request.get_json())


@app.route("/api/v1/users/<user_id>")
@track("/api/v1/users/<id>")
def users(user_id):
    return proxy(UPSTREAMS["profiles"], f"/api/v1/users/{user_id}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
