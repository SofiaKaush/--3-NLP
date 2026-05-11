"""
app_v2.py — Версия 2: Мультимодальный чат (Текст + Картинка)
Провайдер: OpenRouter (Бесплатная Vision-модель Llama-3.2-11B)
"""

import os
import base64
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# ═══════════════════════════════════════════════════════════════
API_KEY  = os.environ.get("OPENROUTER_API_KEY", "вставьте_ваш_ключ_openrouter_сюда")
BASE_URL = "https://openrouter.ai/api/v1"

CHAT_MODEL    = "meta-llama/llama-3.2-11b-vision-instruct:free"
SYSTEM_PROMPT = "Ты — полезный ИИ. Подробно описывай изображения, если пользователь их отправляет."
PORT          = 5002
# ═══════════════════════════════════════════════════════════════

app     = Flask(__name__)
client  = OpenAI(api_key=API_KEY, base_url=BASE_URL)
history = []

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Чат-бот v2 (Vision)</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
    #chat { border: 1px solid #ccc; padding: 1rem; height: 400px; overflow-y: auto; margin-bottom: 1rem; border-radius: 8px;}
    .msg { margin-bottom: 0.5rem; padding: 0.5rem; border-radius: 4px; }
    .user { background: #e3f2fd; text-align: right; }
    .assistant { background: #f1f8e9; text-align: left; }
    form { display: flex; flex-direction: column; gap: 0.5rem; }
    .inputs { display: flex; gap: 0.5rem; }
    input[type="text"] { flex: 1; padding: 0.5rem; }
    button { padding: 0.5rem; cursor: pointer; }
    img.preview { max-width: 200px; max-height: 200px; display: block; margin-top: 5px; border-radius: 4px;}
  </style>
</head>
<body>
  <h2>Чат-бот v2 (Текст + Фото | OpenRouter)</h2>
  <div id="chat"></div>
  <form id="form">
    <input type="file" id="imageFile" accept="image/*">
    <div class="inputs">
      <input type="text" id="message" placeholder="Спроси что-нибудь о картинке..." autocomplete="off">
      <button type="submit">Отправить</button>
    </div>
  </form>
  <br><button id="resetBtn">Сбросить историю</button>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');

    form.onsubmit = async (e) => {
      e.preventDefault();
      const fileInput = document.getElementById('imageFile');
      const textInput = document.getElementById('message');
      const text = textInput.value.trim();
      const file = fileInput.files[0];

      if (!text && !file) return;

      const formData = new FormData();
      formData.append('message', text);
      
      let userHtml = `<div class="msg user"><b>Вы:</b> ${text}`;
      if (file) {
        formData.append('image', file);
        const objectUrl = URL.createObjectURL(file);
        userHtml += `<br><img src="${objectUrl}" class="preview">`;
      }
      userHtml += `</div>`;
      chat.innerHTML += userHtml;
      
      textInput.value = '';
      fileInput.value = '';
      chat.scrollTop = chat.scrollHeight;

      try {
          const res = await fetch('/chat', { method: 'POST', body: formData });
          const data = await res.json();
          if (data.error) throw new Error(data.error);
          chat.innerHTML += `<div class="msg assistant"><b>ИИ:</b> ${data.reply}</div>`;
      } catch (err) {
          chat.innerHTML += `<div class="msg" style="color:red;">Ошибка: ${err.message}</div>`;
      }
      chat.scrollTop = chat.scrollHeight;
    };

    document.getElementById('resetBtn').onclick = async () => {
      await fetch('/reset', { method: 'POST' });
      chat.innerHTML = '<div>История очищена.</div>';
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
        user_message = request.form.get('message', '').strip()
        image_file   = request.files.get('image')

        if image_file:
            mime_type  = image_file.mimetype
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            content = [
                {"type": "text", "text": user_message if user_message else "Что изображено на этой картинке?"},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
            ]
            history_text = f"[Картинка] {user_message}"
        else:
            if not user_message:
                return jsonify({"error": "Пустое сообщение"}), 400
            content      = user_message
            history_text = user_message

        history.append({"role": "user", "content": content})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
        reply = response.choices[0].message.content

        history[-1] = {"role": "user", "content": history_text}
        history.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    history.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print(f"Чат-бот v2  |  http://localhost:{PORT}")
    app.run(port=PORT, debug=True)