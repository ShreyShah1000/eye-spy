from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests, json, os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eyespy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)

# Initialize database tables
with app.app_context():
    db.create_all()

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "qwen/qwen3-vl-8b-instruct"
URL = "https://openrouter.ai/api/v1/chat/completions"

# Using a direct image URL (not a webpage)
GAME_STATE = {}
prompt = """You are an expert “I Spy” game master. Analyze the image carefully.

Step 1: Identify all visible objects.
Step 2: Pick ONE object that:
 - is distinct and clearly visible (not blurry or cropped),
 - can be easily described in one word (e.g., “apple”, “dog”, “car”),
 - is interesting or colorful enough for an I Spy clue.
Step 3: Create a clever, rhyming or playful riddle that hints at the object without naming it.
Step 4: Create an insightful, educational fact for curious young kids to learn, and if possible connect it to nature

Output your answer strictly in JSON with the following format:
{
  "object": "<chosen object>",
  "riddle": "<short, fun riddle that a player can guess>",
  "location_hint": "<chosen object's position>",
  "reason": "<1-sentence justification for why this object was chosen>",
  "fact": "<fun, educational fact related to nature if possible>
}

Example:
{
  "object": "bicycle",
  "riddle": "I have two wheels but no engine roar, I wait by the tree and roll on the floor.",
  "location_hint": "bottom right",
  "reason": "The bicycle is colorful, centered, and easy for players to spot."
  "fact": "A bicycle is a zero-emissions vehicle, which means it doesn't have a tailpipe and doesn't use gasoline or motor-oil. When you choose to ride your bike instead of taking a car, you help keep the air clean for all the birds, bees, butterflies, and trees! Since your bike is powered by your own legs, every time you pedal, you are choosing a silent, clean way to explore and protect the beautiful nature all around you."
}
"""


@app.route("/processImage", methods=["POST"])
def processImage():
    data = request.get_json()
    image_url = data.get("image")
    username = data.get("username")

    # Validate required fields
    if not image_url:
        return jsonify({"error": "No image received"}), 400
    
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Create user if doesn't exist
    user = User.query.filter_by(username=username).first()
    if not user:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()

    messages = [
        {
            "role": "user",
            "content": [
                # first send your text question/prompt
                {"type": "text", "text": prompt},
                # then the image
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 400
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=payload)

    if response.status_code != 200:
       return jsonify({"error": "Failed to contact OpenRouter", "details": response.text}), 500
    
    output = response.json()

    result = output["choices"][0]["message"]["content"]
    parsed = json.loads(result)
    GAME_STATE["default"] = {
        "object": parsed["object"],
        "riddle": parsed["riddle"],
        "location_hint": parsed["location_hint"],
        "reason": parsed["reason"],
        "fact": parsed["fact"],
        "username": username,
        "attempt": 0
    }
    return jsonify(GAME_STATE["default"])


# For voice mode
@app.route("/game/state", methods=["GET"])
def game_state():
    state = GAME_STATE.get("default")
    if not state:
        return jsonify({"error": "no round set"}), 404
    return jsonify(state)

@app.route("/game/check", methods=["POST"])
def game_check():
    body = request.get_json() or {}
    guess = (body.get("guess") or "").lower().strip()

    state = GAME_STATE.get("default")
    if not state:
        return jsonify({"error": "no round"}), 404

    target = state["object"].lower()
    state["attempt"] += 1

    correct = (target in guess) or (guess in target)

    if correct:
        msg = f"Yes! It was the {state['object']}."
    else:

        if state["attempt"] == 1:
            msg = f"Nice try, but not that. Hint: it’s {state['location_hint']}."
        else:
            msg = f"Still not it. Stronger hint: look {state['location_hint']} and think of a {state['object'].split()[0]}."

    return jsonify({
        "correct": correct,
        "attempt": state["attempt"],
        "hint_message": msg,
        "target": state["object"],
        "location_hint": state["location_hint"]
    })

@app.route("/game/check_score", methods=["GET"])
def check_score():
    state = GAME_STATE.get("default")
    user = User.query.filter_by(username=state["username"]).first()
    if state["attempt"] == 1:
        user.score += 15
        db.session.commit()
    elif state["attempt"] == 2:
        user.score += 10
        db.session.commit()
    elif state["attempt"] == 3:
        user.score += 5
        db.session.commit()

    msg = f"You have {user.score} points in total."

    return jsonify({
        "msg": msg
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500)