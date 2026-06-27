from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

FAILURE_THRESHOLD = 3
RESET_TIMEOUT = 10

failure_count = 0
circuit_open = False
last_failure_time = None


def call_external_service():
    success = random.choice([True, False])

    if success:
        return {"message": "External service success"}

    raise Exception("External service failed")


@app.route("/service")
def service():
    global failure_count
    global circuit_open
    global last_failure_time

    # Check if circuit should close again
    if circuit_open:
        elapsed = time.time() - last_failure_time

        if elapsed >= RESET_TIMEOUT:
            circuit_open = False
            failure_count = 0
        else:
            return jsonify({
                "status": "Circuit OPEN",
                "message": "Service temporarily unavailable"
            }), 503

    try:
        result = call_external_service()

        failure_count = 0

        return jsonify(result)

    except Exception:

        failure_count += 1

        if failure_count >= FAILURE_THRESHOLD:
            circuit_open = True
            last_failure_time = time.time()

        return jsonify({
            "status": "Failure",
            "failure_count": failure_count
        }), 500


@app.route("/status")
def status():

    return jsonify({
        "circuit_open": circuit_open,
        "failure_count": failure_count
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(debug=True)
