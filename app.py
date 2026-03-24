# -------------------------
# Imports
# -------------------------
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import os

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# Load artifacts (model + tokenizer + config)
# -------------------------
MODEL_PATH = "sentiment_model.keras"
TOKENIZER_PATH = "tokenizer.pkl"
CONFIG_PATH = "config.pkl"

model = load_model(MODEL_PATH, compile=False)

with open(TOKENIZER_PATH, "rb") as f:
    tokenizer = pickle.load(f)

with open(CONFIG_PATH, "rb") as f:
    config = pickle.load(f)

MAX_LENGTH = config["max_length"]

# -------------------------
# Text preprocessing
# -------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

# -------------------------
# Sentiment prediction
# -------------------------
def predict_sentiment(text):
    text = clean_text(text)

    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, maxlen=MAX_LENGTH, padding="post")

    prediction = model.predict(padded)[0][0]

    if prediction >= 0.5:
        return "Positive"
    else:
        return "Negative"

# -------------------------
# Chatbot logic (Hybrid: rules + model)
# -------------------------
def chatbot_response(user_input):
    text = user_input.lower()

    # Rule-based keywords
    negative_words = ["hate", "bad", "terrible", "awful", "worst", "boring"]
    positive_words = ["love", "amazing", "great", "awesome", "fantastic"]

    # Rule-based override
    if any(word in text for word in negative_words):
        return "😅 That doesn’t sound great. What didn’t you like?"

    if any(word in text for word in positive_words):
        return "😊 Glad you liked it!"

    # Fallback to model
    sentiment = predict_sentiment(user_input)

    if sentiment == "Positive":
        return "😊 Glad you liked it!"
    else:
        return "😅 Sorry it wasn’t great. What went wrong?"

# -------------------------
# Routes
# -------------------------

# Serve UI
@app.route("/")
def home():
    return render_template("index.html")

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"]
    reply = chatbot_response(user_message)

    return jsonify({"reply": reply})

# -------------------------
# Run app (local + deploy)
# -------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )