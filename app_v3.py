"""
app_v3.py — Версия 3: Генерация изображений
Безопасная версия для GitHub.
"""

import os
import urllib.parse
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
CHAT_MODEL = "gpt-4o-mini"
PORT = 5003

app = Flask(__name__)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Чат-бот v3 - Генерация</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
    #chat { border: 1px solid #ccc; padding: 1rem; height: 350px; overflow-y: auto; background: #fff; margin-bottom: 1rem; }
    .msg { margin-bottom: 0.8rem; padding: 0.8rem; border-radius: 4px; }
    img { max-width: 100%; border-radius: 4px; }
  </style>
</head>
<body>
  <h2>Чат-бот v3 (Генерация)</h2>
  <div id="chat"></div>
  <input type="text" id="prompt" style="width:70%" placeholder="Что нарисовать?">
  <button onclick="generate()">Нарисуй</button>
  <script>
    async function generate() {
      const p = document.getElementById('prompt');
      const chat = document.getElementById('chat');
      chat.innerHTML += `<div class="msg">Рисую: ${p.value}...</div>`;
      const res = await fetch('/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: p.value})
      });
      const data = await res.json();
      if(data.image_url) chat.innerHTML += `<img src="${data.image_url}">`;
      chat.scrollTop = chat.scrollHeight;
    }
  </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', 'cat')
        image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)