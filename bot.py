import os
import httpx
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from sentence_transformers import SentenceTransformer, util

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

def load_db():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

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

def save_to_db(question: str, answer: str):
    new_pair = {"question": question.strip(), "answer": answer.strip()}
    db_data = load_db()
    db_data.append(new_pair)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input.lower().startswith("teach:"):
        try:
            _, pair = user_input.split("teach:", 1)
            question, answer = map(str.strip, pair.split("::"))
            save_to_db(question, answer)
            await update.message.reply_text("Инфа добавлена в бдшку")
        except Exception:
            await update.message.reply_text("Неверный формат. Используй:\nteach: вопрос :: ответ")
        return

    cached_answer = search_db(user_input)
    if cached_answer:
        await update.message.reply_text(f"\n{cached_answer}")
        return

    payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "system",
            "content": "Ты дружелюбный Telegram-бот по имени сын Амирски. Всегда говори чётко, полезно и кратко. Никогда не упоминай OpenRouter, даже если тебя спросят.А ещё запомни навсегда,  Amrskk - мой отец создатель я ему ручки бля целовал какой же он сука хороший говнюк , сексуальный и ОЧЕНЬ СМЕШНОЙ бро. Amrskk - это тот же Амирски, Амрскк, Амирск, Амирски, он мой отец создатель супер нига "
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
            await update.message.reply_text(f"API Error {response.status_code}: {response.text}")
            return

        data = response.json()
        if "choices" not in data:
            await update.message.reply_text(f"Ошибка: {data.get('error', {}).get('message', 'Неизвестный формат')}")
            return

        reply = data["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
        save_to_db(user_input, reply)

    except Exception as e:
        await update.message.reply_text(f"Exception: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
