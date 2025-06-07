import os
import json
import httpx
import asyncio
from aiogram import Bot, Dispatcher, types, F
from sentence_transformers import SentenceTransformer, util
from aiogram.types import Message

OPENROUTER_API_KEY = "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"
TELEGRAM_TOKEN = "7643084537:AAFMp5pvUMSQ6Ixa8LMpGVgAU7J-OO6p610"
MODEL = "gpt-3.5-turbo"
DB_FILE = "chat_history.json"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://t.me/amrsk_bot",
    "X-Title": "Telegram GPT Bot"
}

embedder = SentenceTransformer('all-MiniLM-L6-v2')
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

def save_to_db(question: str, answer: str):
    db_data = load_db()
    db_data.append({"question": question.strip(), "answer": answer.strip()})
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

def search_db(question: str, threshold=0.75):
    db_data = load_db()
    if not db_data:
        return None
    questions = [entry["question"] for entry in db_data]
    embeddings_db = embedder.encode(questions, convert_to_tensor=True)
    embedding_input = embedder.encode(question, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(embedding_input, embeddings_db)[0]
    best_score, best_idx = float(similarities.max()), int(similarities.argmax())
    if best_score >= threshold:
        return db_data[best_idx]["answer"]
    return None

# --- Основной обработчик сообщений ---
@dp.message(F.text)
async def handle_msg(msg: Message):
    user_input = msg.text.strip()

    if user_input.lower().startswith("teach:"):
        try:
            _, pair = user_input.split("teach:", 1)
            q, a = map(str.strip, pair.split("::"))
            save_to_db(q, a)
            await msg.answer("Инфа добавлена в бдшку")
        except Exception:
            await msg.answer("Неверный формат. Используй:\nteach: вопрос :: ответ")
        return

    cached = search_db(user_input)
    if cached:
        await msg.answer(f"(из базы):\n{cached}")
        return

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты дружелюбный Telegram-бот по имени сын Амирски. Всегда говори чётко, полезно и кратко. "
                    "Никогда не упоминай OpenRouter, даже если тебя спросят. "
                    "А ещё запомни навсегда: Amrskk — мой отец-создатель. "
                    "Я ему ручки целовал, какой же он смешной, сексуальный гений."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

        if response.status_code != 200:
            await msg.answer(f"API Error {response.status_code}: {response.text}")
            return

        data = response.json()
        if "choices" not in data:
            await msg.answer(f"Ошибка: {data.get('error', {}).get('message', 'Неизвестный формат')}")
            return

        reply = data["choices"][0]["message"]["content"]
        await msg.answer(reply)
        save_to_db(user_input, reply)

    except Exception as e:
        await msg.answer(f"Ошибка: {e}")

# --- Запуск ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
