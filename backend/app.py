from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, json, os, base64
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "qwen/qwen-2.5-vl-7b-instruct"
URL = "https://openrouter.ai/api/v1/chat/completions"

# Using a direct image URL (not a webpage)
example_image = "https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg"



@app.route("/processImage", methods=["POST"])
def processImage():
    image = request.files["file"]
    image_b64 = base64.b64encode(image.read()).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{image_b64}"
    
    if not image:
        return jsonify({"error": "No image received"}), 400

    messages = [
        {
            "role": "user",
            "content": [
                # first send your text question/prompt
                {"type": "text", "text": "Treat this image as an eye spy game. Your job is to choose an object from the image. Difficulty is hard. Respond with two parts: 1) An 'I spy' riddle (start with 'I spy something...'), and 2) The answer. Format your response clearly with 'Riddle:' and 'Answer:' labels."},
                # then the image
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        }
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 300
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
    
    # Parse the riddle and answer from the response
    riddle = ""
    answer = ""
    
    if "Riddle:" in result and "Answer:" in result:
        parts = result.split("Answer:")
        riddle = parts[0].replace("Riddle:", "").strip()
        answer = parts[1].strip()
    else:
        # Fallback if format isn't followed
        riddle = result
        answer = "See riddle for details"
    
    return jsonify({"riddle": riddle, "answer": answer})



    

if __name__ == '__main__':
    app.run(debug=True)