from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import DATABASE_URL

# Set up connection pool settings (SQLite supports basic configuration)
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initializes the database schema by creating all registered tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Context manager helper for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
