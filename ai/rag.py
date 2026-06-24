import os
from .embeddings import get_embedding
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import openai

# Retrieve context function
def retrieve_context(query: str, top_k: int, session_id: str, user_id: str):
    embedding = get_embedding(query)
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(Vector).filter_by(session_id=session_id, user_id=user_id).order_by(Vector.embedding.cosine_distance(embedding)).limit(top_k).all()
    return results

# Async function to answer questions
async def answer_question(query: str, session_id: str, user_id: str) -> dict:
    context_chunks = retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)
    context_text = "\n".join([chunk.metadata['chunk_text'] for chunk in context_chunks])
    sources = [{'filename': chunk.metadata['source_filename'], 'location': chunk.metadata['page_or_row']} for chunk in context_chunks]

    if not sources:
        sources = [{"filename": "No sources found", "location": "N/A"}]

    prompt = f"Context:\n{context_text}\n\nQuestion:\n{query}\n\nAnswer:"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content

    return {"answer": answer, "sources": sources}