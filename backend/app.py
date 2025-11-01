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
example_image = "https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg"
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
  "reason": "<1-sentence justification for why this object was chosen>"
}

Example:
{
  "object": "bicycle",
  "riddle": "I have two wheels but no engine roar, I wait by the tree and roll on the floor.",
  "reason": "The bicycle is colorful, centered, and easy for players to spot."
}
"""


@app.route("/processImage", methods=["POST"])
def processImage():
    data = request.get_json()
    image_url = data.get("image")
    
    if not image_url:
        return jsonify({"error": "No image received"}), 400

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
    print(output)
    result = output["choices"][0]["message"]["content"]
    
    return jsonify({"result":result})



    

if __name__ == '__main__':
    app.run(debug=True, port=8080)