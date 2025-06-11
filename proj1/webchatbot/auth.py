import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from database import database

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def register_user(username: str, password: str):
    hashed = hash_password(password)
    query = "INSERT INTO users (username, password_hash) VALUES (:u, :p)"
    await database.execute(query=query, values={"u": username, "p": hashed})

async def authenticate_user(username: str, password: str):
    query = "SELECT password_hash FROM users WHERE username = :u"
    row = await database.fetch_one(query=query, values={"u": username})
    if not row:
        return False
    return verify_password(password, row["password_hash"])

def verify_token(token: str):
    user = decode_token(token)
    return user
