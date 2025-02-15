from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import langdetect

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Enable CORS for all routes
CORS(app)

@app.after_request
def apply_cors(response):
    """ ✅ Manually add CORS headers for every response """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

@app.route("/", methods=["GET"])
def home():
    """ ✅ Health check route to verify API is running """
    return jsonify({"message": "🚀 Flask API is running with full CORS support!"})

@app.route("/ask", methods=["POST", "OPTIONS"])
def ask_question():
    """ ✅ Handle API requests and preflight OPTIONS requests """
    
    if request.method == "OPTIONS":
        return apply_cors(jsonify({"message": "CORS preflight passed"})), 200

    data = request.get_json()
    user_question = data.get("question", "").strip()

    if not user_question:
        return apply_cors(jsonify({"error": "❌ No question provided."})), 400

    # ✅ Detect language using langdetect
    try:
        detected_lang = langdetect.detect(user_question)
    except:
        detected_lang = "vi"  # Default to Vietnamese if detection fails

    # ✅ Set AI response language
    system_message = "You are a helpful assistant. Answer in English."
    if detected_lang != "en":
        system_message = "Bạn là một trợ lý AI hữu ích. Hãy trả lời bằng tiếng Việt."

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_question}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        answer = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return apply_cors(jsonify({"error": f"⚠️ ERROR: OpenAI request failed: {str(e)}"})), 500

    return apply_cors(jsonify({"answer": answer}))

# ✅ Run Flask app for Railway deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
