import json
import os
from database import database

DB_FILE = "chat_history.json"

async def load_chat_history_pg():
    query = "SELECT question, answer FROM chat_memory"
    return await database.fetch_all(query=query)

async def save_chat_pair_pg(question: str, answer: str):
    query = "INSERT INTO chat_memory (question, answer) VALUES (:question, :answer)"
    await database.execute(query=query, values={"question": question.strip(), "answer": answer.strip()})

