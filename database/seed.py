import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    engine,
    SessionLocal,
    User,
    Session,
    Document,
    DocumentChunk,
    Query,
    QuerySource,
)

def seed_database():
    session = SessionLocal()
    try:
        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            hashed_password="hashed_password1",
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            hashed_password="hashed_password2",
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="user3@example.com",
            hashed_password="hashed_password3",
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Sessions
        session1 = Session(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            expires_at="2023-12-31 23:59:59",
        )
        session2 = Session(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            expires_at="2023-12-31 23:59:59",
        )
        session3 = Session(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            expires_at="2023-12-31 23:59:59",
        )
        session.add_all([session1, session2, session3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            session_id=session1.id,
            filename="doc1.txt",
            original_filename="original_doc1.txt",
            file_size=1024,
            mime_type="text/plain",
            status="processed",
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            session_id=session2.id,
            filename="doc2.txt",
            original_filename="original_doc2.txt",
            file_size=2048,
            mime_type="text/plain",
            status="processed",
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            session_id=session3.id,
            filename="doc3.txt",
            original_filename="original_doc3.txt",
            file_size=4096,
            mime_type="text/plain",
            status="processed",
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            user_id=user1.id,
            session_id=session1.id,
            chunk_index=0,
            chunk_text="This is the first chunk of document 1.",
            embedding=[0.1] * 1536,
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            user_id=user2.id,
            session_id=session2.id,
            chunk_index=0,
            chunk_text="This is the first chunk of document 2.",
            embedding=[0.2] * 1536,
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document3.id,
            user_id=user3.id,
            session_id=session3.id,
            chunk_index=0,
            chunk_text="This is the first chunk of document 3.",
            embedding=[0.3] * 1536,
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed Queries
        query1 = Query(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            session_id=session1.id,
            question="What is the content of document 1?",
            answer="This is the first chunk of document 1.",
        )
        query2 = Query(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            session_id=session2.id,
            question="What is the content of document 2?",
            answer="This is the first chunk of document 2.",
        )
        query3 = Query(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            session_id=session3.id,
            question="What is the content of document 3?",
            answer="This is the first chunk of document 3.",
        )
        session.add_all([query1, query2, query3])
        session.commit()

        # Seed QuerySources
        query_source1 = QuerySource(
            id=str(uuid.uuid4()),
            query_id=query1.id,
            chunk_id=chunk1.id,
            similarity_score=0.95,
        )
        query_source2 = QuerySource(
            id=str(uuid.uuid4()),
            query_id=query2.id,
            chunk_id=chunk2.id,
            similarity_score=0.90,
        )
        query_source3 = QuerySource(
            id=str(uuid.uuid4()),
            query_id=query3.id,
            chunk_id=chunk3.id,
            similarity_score=0.85,
        )
        session.add_all([query_source1, query_source2, query_source3])
        session.commit()

        print("Database seeded successfully!")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()