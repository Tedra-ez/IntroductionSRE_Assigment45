import os
import time
from functools import wraps

import redis
from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "notification-service"


def redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


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
        redis_client().ping()
        return jsonify({"status": "healthy", "service": SERVICE}), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 503


@app.route("/metrics")
def metrics():
    return metrics_response()


@app.route("/api/v1/notify", methods=["POST"])
@track("/api/v1/notify")
def notify():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    message = data.get("message", "Order update")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    key = f"notifications:{user_id}"
    redis_client().lpush(key, message)
    return jsonify({"queued": True, "service": SERVICE}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8005")))
