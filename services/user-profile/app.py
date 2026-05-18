import os
import time
from functools import wraps

from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "user-profile-service"
PROFILES = {}


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


@app.route("/api/v1/users/<user_id>")
@track("/api/v1/users/<id>")
def get_profile(user_id):
    profile = PROFILES.get(user_id, {"user_id": user_id, "name": f"User {user_id}", "email": f"{user_id}@example.com"})
    return jsonify(profile), 200


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
@track("/api/v1/users/<id>")
def upsert_profile(user_id):
    data = request.get_json(silent=True) or {}
    PROFILES[user_id] = {"user_id": user_id, **data}
    return jsonify(PROFILES[user_id]), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8006")))
