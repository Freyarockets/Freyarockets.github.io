# Stardust Avatar Flask app

from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configuration via environment variables
LMSTUDIO_API_URL = os.environ.get("LMSTUDIO_API_URL", "http://localhost:8080")
LMSTUDIO_API_KEY = os.environ.get("LMSTUDIO_API_KEY")
LMSTUDIO_MODEL = os.environ.get("LMSTUDIO_MODEL", "gpt-4o")
LMSTUDIO_TEMPERATURE = float(os.environ.get("LMSTUDIO_TEMPERATURE", "0.8"))


def query_lmstudio(message: str) -> str:
    """Try common LMStudio endpoints (OpenAI-compatible /v1/chat/completions or a simple /api/v1/generate).
    Returns the generated text or raises an exception on error.
    """
    headers = {"Content-Type": "application/json"}
    if LMSTUDIO_API_KEY:
        headers["Authorization"] = f"Bearer {LMSTUDIO_API_KEY}"

    # First try OpenAI-compatible chat completions (many local servers support this)
    try:
        url = LMSTUDIO_API_URL.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": LMSTUDIO_MODEL,
            "messages": [{"role": "user", "content": message}],
            "temperature": LMSTUDIO_TEMPERATURE,
            "max_tokens": 1024,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.ok:
            data = resp.json()
            # Try to extract assistant text from common shapes
            if "choices" in data and len(data["choices"]) > 0:
                out = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
                if out:
                    return out
            # OpenAI-style 'result' key sometimes used
            if "result" in data and isinstance(data["result"], dict):
                return data["result"].get("content", "")
    except Exception:
        pass

    # Fallback: some LMStudio endpoints use /api/v1/generate with a prompt
    try:
        url = LMSTUDIO_API_URL.rstrip("/") + "/api/v1/generate"
        payload = {"prompt": message, "max_new_tokens": 512, "temperature": LMSTUDIO_TEMPERATURE}
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.ok:
            data = resp.json()
            # Common shapes: {"results":[{"text": "..."}]}
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0].get("text", "")
            # Or direct 'text'
            if "text" in data:
                return data["text"]
    except Exception:
        pass

    # If we got here, return a clear error message
    raise RuntimeError("Could not get a response from LMStudio. Check LMSTUDIO_API_URL, key, and model.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True)
    message = payload.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        reply = query_lmstudio(message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # For local development only. Use a proper WSGI server in production.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
