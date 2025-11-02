from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, json, os, base64
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)




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

Output your answer strictly in JSON with the following format:
{
  "object": "<chosen object>",
  "riddle": "<short, fun riddle that a player can guess>",
  "location_hint": "<chosen object's position>",
  "reason": "<1-sentence justification for why this object was chosen>"
}

Example:
{
  "object": "bicycle",
  "riddle": "I have two wheels but no engine roar, I wait by the tree and roll on the floor.",
  "location_hint": "bottom right",
  "reason": "The bicycle is colorful, centered, and easy for players to spot."
}
"""


@app.route("/processImage", methods=["POST"])
def processImage():
    data = request.get_json()
    #image_url = data.get("image")
    
    #if not image_url:
     #   return jsonify({"error": "No image received"}), 400

    # messages = [
    #     {
    #         "role": "user",
    #         "content": [
    #             # first send your text question/prompt
    #             {"type": "text", "text": prompt},
    #             # then the image
    #             {"type": "image_url", "image_url": {"url": image_url}}
    #         ]
    #     }
    # ]

    # payload = {
    #     "model": MODEL,
    #     "messages": messages,
    #     "temperature": 0.3,
    #     "max_tokens": 400
    # }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    #response = requests.post(URL, headers=headers, json=payload)

    #if response.status_code != 200:
     #   return jsonify({"error": "Failed to contact OpenRouter", "details": response.text}), 500
    
    #output = response.json()
    #print(output)
    output = {'id': 'gen-1762030485-5QW5870OssmkIxKfzjem', 'provider': 'Alibaba', 'model': 'qwen/qwen3-vl-8b-instruct', 'object': 'chat.completion', 'created': 1762030485, 'choices': [{'logprobs': None, 'finish_reason': 'stop', 'native_finish_reason': 'stop', 'index': 0, 'message': {'role': 'assistant', 'content': '{\n  "object": "water bottle",\n  "riddle": "I’m green with a cap, held tight in a hand, quenching thirst in this busy land.",\n  "reason": "The water bottle is distinct, colorful, and clearly visible, making it an ideal I Spy target."\n}', 'refusal': None, 'reasoning': None}}], 'system_fingerprint': None, 'usage': {'prompt_tokens': 1670, 'completion_tokens': 62, 'total_tokens': 1732}}
    result = output["choices"][0]["message"]["content"]
    parsed = json.loads(result)
    GAME_STATE["default"] = {
        "object": parsed["object"],
        "riddle": parsed["riddle"],
        "location_hint": "top right",
        "reason": parsed["reason"],
        "attempt": 0
    }
    print(GAME_STATE)
    return jsonify(GAME_STATE["default"])

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
    state["attempt"] += 1  # update attempts

    # forgiving match: "cup" == "red cup"
    correct = (target in guess) or (guess in target)

    if correct:
        msg = f"Yes! It was the {state['object']}."
    else:
        # escalate by attempt
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



    

if __name__ == '__main__':
    app.run(debug=True, port=5500)