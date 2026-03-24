from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# -------------------------
# Chatbot logic (simulation)
# -------------------------
def chatbot_response(user_input):
    text = user_input.lower()

    negative_words = ["hate", "bad", "terrible", "awful", "worst", "boring"]
    positive_words = ["love", "amazing", "great", "awesome", "fantastic"]

    if any(word in text for word in negative_words):
        return "😅 That doesn’t sound great. What didn’t you like?"

    if any(word in text for word in positive_words):
        return "😊 Glad you liked it!"

    return "🤔 Tell me more about the movie!"

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message required"}), 400

    user_message = data["message"]
    reply = chatbot_response(user_message)

    return jsonify({"reply": reply})

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
