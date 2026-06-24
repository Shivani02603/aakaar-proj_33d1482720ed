import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Read DATABASE_URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Configure SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Configure sessionmaker
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Dependency for FastAPI to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize the database (create all tables)
def init_db(Base):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize the database: {e}")

# Health check function to test the database connection
def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except OperationalError as e:
        raise RuntimeError(f"Database connection failed: {e}")