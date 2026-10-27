
from flask import Flask, jsonify, request

from src.claim_service import process_claim, get_claims_for_review
app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "application": "Insurance Claims AI",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "process_claim": "/api/claims/<claim_id>/assess",
            "claims_for_review": "/api/claims/review",
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.get("/api/claims/review")
def claims_for_review_endpoint():
    result, status_code = get_claims_for_review()
    return jsonify(result), status_code
@app.get("/api/claims/<claim_id>/assess")
def assess_claim_endpoint(claim_id):
    result, status_code = process_claim(claim_id)
    return jsonify(result), status_code


@app.post("/api/claims/assess")
def assess_claim_from_body():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    claim_id = payload.get("claim_id")

    if not isinstance(claim_id, str) or not claim_id.strip():
        return jsonify({
            "error": "A non-empty claim_id is required"
        }), 400

    result, status_code = process_claim(claim_id.strip())
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
