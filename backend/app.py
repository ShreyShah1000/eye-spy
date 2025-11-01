# from flask import Flask, request, jsonify
# from flask_cors import CORS
import requests, json, os, base64
from dotenv import load_dotenv
# app = Flask(__name__)
# CORS(app)

load_dotenv()

API_KEY=os.getenv("OPENROUTER_API_KEY")
print(API_KEY)
# MODEL = "meta-llama/llama-3.2-11b-vision-instruct"
# URL = "https://openrouter.ai/api/v1/chat/completions"

# example_image = "https://pixabay.com/photos/nature-waters-lake-island-3082832/"

# messages = [
#     {
#         "role": "user",
#         "content": [
#             # first send your text question/prompt
#             {"type": "text", "text": "Treat this image as an eye spy game. Your job is to choose an object from the image. Difficulty is easy"},
#             # then the image
#             {"type": "image_url", "image_url": {"url": example_image}}
#         ]
#     }
# ]

# payload = {
#     "model": MODEL,
#     "messages": messages,
#     "temperature": 0.0,
#     "max_tokens": 300
# }

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# response = requests.post(URL, headers=headers, json=payload)
# response.raise_for_status()
# result = response.json()
# print(json.dumps(result, indent=2))

# # @app.route("/processImage", methods=["POST"])
# # def processImage():
# #     return 0

# # if __name__ == '__main__':
# #     app.run(debug=True)