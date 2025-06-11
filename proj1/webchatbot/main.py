from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
from models.user_models import UserRegister, UserLogin
from auth import register_user, authenticate_user, create_token, verify_token
from vector_search import search_db_pg
from db_utils import save_chat_pair_pg
from database import database
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "gpt-3.5-turbo"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://your-frontend.com",
    "X-Title": "Web GPT Bot"
}

class ChatInput(BaseModel):
    message: str

class TeachInput(BaseModel):
    question: str
    answer: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/register")
async def register(user: UserRegister):
    await register_user(user.username, user.password)
    return {"message": "Registered successfully"}

@app.post("/login")
async def login(user: UserLogin):
    is_valid = await authenticate_user(user.username, user.password)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.username)
    return {"token": token}


@app.post("/chat")
async def chat(input_data: ChatInput, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_input = input_data.message.strip()

    cached_answer = await search_db_pg(user_input)
    if cached_answer:
        return {"reply": cached_answer}

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный и дружелюбный AI-бот. Никогда не упоминай OpenRouter."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = res.json()
        reply = data["choices"][0]["message"]["content"]

    await save_chat_pair_pg(user_input, reply)
    return {"reply": reply}


@app.post("/teach")
async def teach(input_data: TeachInput, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    await save_chat_pair_pg(input_data.question, input_data.answer)
    return {"status": "ok", "message": "Запомнил братан"}
