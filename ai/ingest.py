import os
import tempfile
from fastapi import UploadFile
from pypdf import PdfReader
import tiktoken
from .embeddings import get_embedding
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

# Chunking function
def chunk(document: str):
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(document)
    chunk_size = 1000
    overlap = 200
    chunks = []
    total_tokens = len(tokens)
    start = 0

    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap

    return chunks

# Async ingestion function for PDF files
async def ingest_pdf(file: UploadFile, session_id: str, user_id: str):
    contents = await file.read()
    original_filename = file.filename or "unknown.pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1])
    tmp.write(contents)
    tmp.flush()
    file_path = tmp.name

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        chunks = chunk(text)
        metadata_list = []
        for i, chunk_text in enumerate(chunks):
            metadata = {
                'source_filename': original_filename,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'page_or_row': f"Page {i + 1}"
            }
            embedding = get_embedding(chunk_text)
            metadata_list.append((embedding, metadata))

        # Store embeddings and metadata in pgvector
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        for embedding, metadata in metadata_list:
            vector_entry = Vector(
                embedding=embedding,
                metadata=metadata,
                session_id=session_id,
                user_id=user_id
            )
            session.add(vector_entry)

        session.commit()
    finally:
        os.unlink(file_path)