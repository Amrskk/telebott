import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

OPENROUTER_API_KEY = "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"
TELEGRAM_TOKEN = "7643084537:AAFMp5pvUMSQ6Ixa8LMpGVgAU7J-OO6p610"
MODEL = "gpt-3.5-turbo"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://t.me/amrsk_bot",
    "X-Title": "Telegram GPT Bot"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_input}]
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
            await update.message.reply_text(f" API Error {response.status_code}: {response.text}")
            return

        data = response.json()

        if "choices" not in data:
            if "error" in data:
                await update.message.reply_text(f" Error: {data['error'].get('message', 'Unknown error')}")
            else:
                await update.message.reply_text(" Unexpected response format from OpenRouter.")
            return

        reply = data["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f" Exception: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print(" Bot is running...")
    app.run_polling()
