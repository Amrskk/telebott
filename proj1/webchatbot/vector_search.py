from sentence_transformers import SentenceTransformer, util
from db_utils import load_chat_history_pg

THRESHOLD = 0.75
embedder = SentenceTransformer("all-MiniLM-L6-v2")

async def search_db_pg(question: str):
    db_data = await load_chat_history_pg()
    if not db_data:
        return None

    questions = [entry["question"] for entry in db_data]

    embeddings_db = embedder.encode(questions, convert_to_tensor=True)
    embedding_input = embedder.encode(question, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(embedding_input, embeddings_db)[0]
    best_score, best_idx = float(similarities.max()), int(similarities.argmax())

    if best_score >= THRESHOLD:
        return db_data[best_idx]["answer"]
    return None
