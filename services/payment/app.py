import os
import time
from functools import wraps

from flask import Flask, jsonify, request

from metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response

app = Flask(__name__)
SERVICE = "payment-service"


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


@app.route("/api/v1/payments", methods=["POST"])
@track("/api/v1/payments")
def pay():
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    amount = data.get("amount")
    if not order_id or amount is None:
        return jsonify({"error": "order_id and amount required"}), 400
    return jsonify(
        {
            "payment_id": f"pay-{order_id}",
            "status": "completed",
            "amount": float(amount),
            "service": SERVICE,
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8004")))
