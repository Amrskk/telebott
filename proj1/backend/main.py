from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в проде замени на адрес сайта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = "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"
MODEL = "gpt-3.5-turbo"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://your-frontend.com",
    "X-Title": "Web GPT Bot"
}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message", "")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты полезный и дружелюбный AI-бот."},
            {"role": "user", "content": user_input}
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = res.json()
        return {"reply": data["choices"][0]["message"]["content"]}
