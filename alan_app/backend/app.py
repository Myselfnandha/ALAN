# backend/app.py
from flask import Flask, request, jsonify
from alan_core.hrm import HRM

app = Flask(__name__)
hrm = HRM()

@app.route("/api/v1/alan", methods=["POST"])
def alan_endpoint():
    data = request.json or {}
    text = data.get("text","")
    processed = {"text": text, "intent": "general", "tokens": text.split()}
    results = hrm.run(processed)
    return jsonify({"input": text, "results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
