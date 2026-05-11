"""
app_v4.py — Версия 4: Function Calling
Безопасная версия для GitHub.
"""

import os
import json
import urllib.parse
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
CHAT_MODEL = "gpt-4o-mini"
PORT = 5004

app = Flask(__name__)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

tools = [{
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Генерирует изображение по описанию",
        "parameters": {
            "type": "object",
            "properties": {"prompt": {"type": "string"}},
            "required": ["prompt"]
        }
    }
}]

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head><meta charset="UTF-8"><title>v4 - Агент</title></head>
    <body style="font-family:sans-serif; max-width:600px; margin:2rem auto;">
      <h2>Умный Агент v4</h2>
      <div id="chat" style="border:1px solid #ccc; height:300px; overflow-y:auto; padding:10px; margin-bottom:10px;"></div>
      <input type="text" id="msg" style="width:75%; padding:10px;">
      <button onclick="send()">Отправить</button>
      <script>
        async function send() {
          const input = document.getElementById('msg');
          const chat = document.getElementById('chat');
          const text = input.value;
          chat.innerHTML += `<div><b>Вы:</b> ${text}</div>`;
          const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
          });
          const data = await res.json();
          chat.innerHTML += `<div><b>Бот:</b> ${data.reply}</div>`;
          if(data.image_url) chat.innerHTML += `<img src="${data.image_url}" style="max-width:100%;">`;
          chat.scrollTop = chat.scrollHeight;
          input.value = '';
        }
      </script>
    </body>
    </html>
    """)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = [{"role": "user", "content": data['message']}]
        response = client.chat.completions.create(model=CHAT_MODEL, messages=messages, tools=tools)
        msg = response.choices[0].message
        if msg.tool_calls:
            prompt = json.loads(msg.tool_calls[0].function.arguments)['prompt']
            image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
            return jsonify({"reply": f"Создано изображение по запросу: {prompt}", "image_url": image_url})
        return jsonify({"reply": msg.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)