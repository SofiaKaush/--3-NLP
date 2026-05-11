"""
app_v2.py — Версия 2: Зрение (Vision)
Безопасная версия для GitHub.
"""

import os
import base64
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
CHAT_MODEL = "gpt-4o-mini"
PORT = 5002

app = Flask(__name__)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
history = []

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Чат-бот v2 - Зрение</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
    #chat { border: 1px solid #ccc; padding: 1rem; height: 350px; overflow-y: auto; background: #fff; margin-bottom: 1rem; }
    .msg { margin-bottom: 0.8rem; padding: 0.8rem; border-radius: 4px; }
    .user { background: #e0e0e0; text-align: right; }
    .assistant { background: #d0d0d0; text-align: left; }
  </style>
</head>
<body>
  <h2>Чат-бот v2 (Зрение)</h2>
  <div id="chat"></div>
  <form id="form">
    <input type="file" id="fileInput" accept="image/*"><br><br>
    <input type="text" id="message" style="width:70%" placeholder="Опиши картинку...">
    <button type="submit">Отправить</button>
  </form>
  <script>
    const form = document.getElementById('form');
    form.onsubmit = async (e) => {
      e.preventDefault();
      const text = document.getElementById('message').value;
      const file = document.getElementById('fileInput').files[0];
      const formData = new FormData();
      formData.append('message', text);
      if (file) formData.append('image', file);
      
      const chat = document.getElementById('chat');
      chat.innerHTML += `<div class="msg user">${text || "Картинка"}</div>`;
      
      const res = await fetch('/chat', { method: 'POST', body: formData });
      const data = await res.json();
      chat.innerHTML += `<div class="msg assistant">${data.reply || data.error}</div>`;
      chat.scrollTop = chat.scrollHeight;
    };
  </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('message', '')
        image_file = request.files.get('image')
        if image_file:
            img_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            content = [
                {"type": "text", "text": user_message or "Опиши изображение"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        else:
            content = user_message

        history.append({"role": "user", "content": content})
        response = client.chat.completions.create(model=CHAT_MODEL, messages=history)
        reply = response.choices[0].message.content
        history[-1] = {"role": "user", "content": user_message or "[Изображение]"}
        history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)