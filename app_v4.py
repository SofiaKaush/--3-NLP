"""
app_v4.py — Версия 4: Function Calling (Умный Агент)
Модель: google/gemini-2.5-flash:free (идеально работает с инструментами)
"""

import os
import json
import urllib.parse
import random
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

API_KEY  = os.environ.get("OPENROUTER_API_KEY", "вставьте_ваш_ключ_openrouter_сюда")
BASE_URL = "https://openrouter.ai/api/v1"

CHAT_MODEL = "google/gemini-2.5-flash:free"
SYSTEM_PROMPT = "Ты — полезный ассистент. У тебя есть инструменты для рисования и проверки погоды. Используй их, когда пользователь просит картинку или погоду."
PORT = 5004

app = Flask(__name__)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
history = []

def generate_free_image(prompt):
    safe_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"

def get_current_weather(city):
    weather_states = ["Солнечно", "Идет дождь", "Снег", "Облачно", "Гроза"]
    temp = random.randint(-15, 35)
    return json.dumps({
        "city": city,
        "temperature": f"{temp}°C",
        "condition": random.choice(weather_states)
    }, ensure_ascii=False)

tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Генерирует изображение или фотографию по текстовому описанию.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Описание изображения, переведенное на английский язык."
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Узнать текущую погоду в определенном городе.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города, например, Москва или Лондон."}
                },
                "required": ["city"]
            }
        }
    }
]

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Чат-бот v4 (Function Calling)</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
    #chat { border: 1px solid #ccc; padding: 1rem; height: 400px; overflow-y: auto; margin-bottom: 1rem; border-radius: 8px;}
    .msg { margin-bottom: 0.5rem; padding: 0.8rem; border-radius: 4px; }
    .user { background: #e3f2fd; text-align: right; margin-left: 20%;}
    .assistant { background: #f5f5f5; text-align: left; margin-right: 10%;}
    .tool { font-size: 0.8em; color: #555; background: #fffde7; padding: 5px; border-radius: 4px; display: inline-block; margin-bottom: 5px;}
    input { width: 75%; padding: 0.5rem; }
    button { width: 20%; padding: 0.5rem; cursor: pointer; }
    img { max-width: 100%; border-radius: 8px; margin-top: 10px; }
  </style>
</head>
<body>
  <h2>Умный Агент (Рисование + Погода)</h2>
  <div id="chat"></div>
  <form id="form">
    <input type="text" id="message" placeholder="Спроси погоду или попроси нарисовать кота..." autocomplete="off">
    <button type="submit">Отправить</button>
  </form>
  <br><button id="resetBtn">Сбросить</button>

  <script>
    const chat = document.getElementById('chat');
    const input = document.getElementById('message');

    document.getElementById('form').onsubmit = async (e) => {
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
        
        let replyHtml = `<div class="msg assistant">`;
        if (data.tool_called) {
            replyHtml += `<div class="tool">⚙️ Вызвана функция: <b>${data.tool_called}</b></div><br>`;
        }
        if (data.image_url) {
            replyHtml += `<img src="${data.image_url}"><br><br>`;
        }
        replyHtml += `${data.reply}</div>`;
        
        chat.innerHTML += replyHtml;
      } catch (err) {
        chat.innerHTML += `<div class="msg" style="color:red">Ошибка: ${err.message}</div>`;
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
        user_message = request.json.get('message', '').strip()
        history.append({"role": "user", "content": user_message})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        tool_called = None
        image_url = None

        if msg.tool_calls:
            tc = msg.tool_calls[0]
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            
            tool_called = func_name
            tool_result_str = ""

            if func_name == "generate_image":
                image_url = generate_free_image(args.get("prompt", "abstract art"))
                tool_result_str = "Изображение успешно сгенерировано и показано пользователю."
            elif func_name == "get_current_weather":
                tool_result_str = get_current_weather(args.get("city", "Неизвестно"))

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result_str
            })

            resp2 = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
            reply = resp2.choices[0].message.content
        else:
            reply = msg.content

        history.append({"role": "assistant", "content": reply})
        
        result = {"reply": reply, "tool_called": tool_called}
        if image_url:
            result["image_url"] = image_url
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    history.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print(f"Умный Агент v4  |  http://localhost:{PORT}")
    app.run(port=PORT, debug=True)