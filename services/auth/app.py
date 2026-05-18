import os
import time
from functools import wraps

from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "auth-service"


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


@app.route("/api/v1/login", methods=["POST"])
@track("/api/v1/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    if not username:
        return jsonify({"error": "username required"}), 400
    return jsonify({"token": f"mock-jwt-{username}", "service": SERVICE}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
