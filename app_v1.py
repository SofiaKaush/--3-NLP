"""
app_v1.py — Версия 1: Текстовый чат-бот
Провайдер: OpenRouter (Бесплатная модель Llama-3)
"""

import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# ═══════════════════════════════════════════════════════════════
#  КОНФИГУРАЦИЯ — OpenRouter API
# ═══════════════════════════════════════════════════════════════
API_KEY  = os.environ.get("OPENROUTER_API_KEY", "вставьте_ваш_ключ_openrouter_сюда")
BASE_URL = "https://openrouter.ai/api/v1"

CHAT_MODEL    = "meta-llama/llama-3-8b-instruct:free"
SYSTEM_PROMPT = "Ты — полезный ассистент. Отвечай кратко, понятно и на русском языке."
PORT          = 5001
# ═══════════════════════════════════════════════════════════════

app     = Flask(__name__)
client  = OpenAI(api_key=API_KEY, base_url=BASE_URL)
history = []

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Чат-бот v1 (Текст)</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; background: #f9f9f9; }
    #chat { border: 1px solid #ddd; padding: 1rem; height: 400px; overflow-y: auto; background: #fff; margin-bottom: 1rem; border-radius: 8px; }
    .msg { margin-bottom: 0.8rem; padding: 0.8rem; border-radius: 8px; line-height: 1.4; }
    .user { background: #e3f2fd; text-align: right; margin-left: 20%; }
    .assistant { background: #f1f8e9; text-align: left; margin-right: 20%; }
    .system { background: #fff3e0; font-size: 0.9em; text-align: center; color: #e65100; margin: 0 10%; }
    form { display: flex; gap: 0.5rem; }
    input { flex: 1; padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; }
    button { padding: 0.8rem 1.5rem; cursor: pointer; background: #1976d2; color: #fff; border: none; border-radius: 4px; }
    button:hover { background: #1565c0; }
    #resetBtn { background: #d32f2f; width: 100%; margin-top: 0.5rem; }
    #resetBtn:hover { background: #c62828; }
  </style>
</head>
<body>
  <h2>Чат-бот v1 (Текст | OpenRouter)</h2>
  <div id="chat"></div>
  <form id="form">
    <input type="text" id="message" placeholder="Введите сообщение..." autocomplete="off" required>
    <button type="submit">Отправить</button>
  </form>
  <button id="resetBtn">Сбросить контекст</button>

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
      chat.scrollTop = chat.scrollHeight;

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
          chat.innerHTML += `<div class="msg system">Ошибка: ${err.message}</div>`;
      }
      chat.scrollTop = chat.scrollHeight;
    };

    document.getElementById('resetBtn').onclick = async () => {
      await fetch('/reset', { method: 'POST' });
      chat.innerHTML = '<div class="msg system">История сброшена. Начните новый разговор.</div>';
    };
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Пустое сообщение"}), 400

        history.append({"role": "user", "content": user_message})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model=CHAT_MODEL, 
            messages=messages,
            extra_headers={ "HTTP-Referer": "http://localhost:5001", "X-Title": "LocalBot" }
        )
        reply = response.choices[0].message.content

        history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply, "history_len": len(history)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    history.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("=" * 50)
    print(f"Чат-бот v1  |  http://localhost:{PORT}")
    print("=" * 50)
    app.run(port=PORT, debug=True)