"""
app_v1.py — Версия 1: Текстовый чат-бот
Провайдер: OpenRouter (gpt-4o-mini)
Безопасная версия без жестко прописанных ключей.
"""

import os
import sys
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# КОНФИГУРАЦИЯ
# API_KEY должен быть установлен в переменной окружения OPENROUTER_API_KEY
API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
CHAT_MODEL = "gpt-4o-mini"
PORT = 5001

app = Flask(__name__)

# Инициализация клиента (пустой ключ вызовет ошибку при первом запросе, что безопасно)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
history = []

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Чат-бот v1 - Текст</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; background: #f4f4f4; padding: 20px; }
    #chat { border: 1px solid #ccc; padding: 1rem; height: 350px; overflow-y: auto; background: #fff; margin-bottom: 1rem; border-radius: 4px; }
    .msg { margin-bottom: 0.8rem; padding: 0.8rem; border-radius: 4px; line-height: 1.4; }
    .user { background: #e0e0e0; text-align: right; margin-left: 20%; }
    .assistant { background: #d0d0d0; text-align: left; margin-right: 20%; }
    .error { background: #ffcccc; color: #cc0000; text-align: center; padding: 10px; border-radius: 4px; font-size: 0.9em; }
    form { display: flex; gap: 0.5rem; }
    input { flex: 1; padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; }
    button { padding: 0.8rem 1.5rem; cursor: pointer; background: #333; color: #fff; border: none; border-radius: 4px; }
  </style>
</head>
<body>
  <h2>Чат-бот v1</h2>
  <div id="chat"></div>
  <form id="form">
    <input type="text" id="message" placeholder="Введите сообщение..." autocomplete="off" required>
    <button type="submit">Отправить</button>
  </form>
  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');
    const input = document.getElementById('message');

    form.onsubmit = async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      chat.innerHTML += `<div class="msg user">${text}</div>`;
      input.value = '';
      try {
          const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
          });
          const data = await res.json();
          if (data.error) throw new Error(data.error);
          chat.innerHTML += `<div class="msg assistant">${data.reply}</div>`;
      } catch (err) {
          chat.innerHTML += `<div class="msg error">Ошибка: ${err.message}</div>`;
      }
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
        data = request.get_json()
        user_message = data.get('message', '').strip()
        history.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(model=CHAT_MODEL, messages=[{"role":"system","content":"Helpful assistant"}] + history)
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)