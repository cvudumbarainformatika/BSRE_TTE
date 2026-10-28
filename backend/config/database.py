from sqlmodel import SQLModel, create_engine, Session, text
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Postgres Engine
# Handles standard SQL queries and pgvector
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

def init_db():
    """Inisialisasi tabel dan extension pgvector"""
    with engine.begin() as conn:
        try:
            # Aktifkan ekstensi vector jika menggunakan postgres
            if "postgresql" in settings.DATABASE_URL:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("Extension 'vector' enabled successfully.")
        except Exception as e:
            logger.warning(f"Note on vector extension: {e}")
        
        # Create all tables
        SQLModel.metadata.create_all(conn)
        logger.info("All database tables registered.")

def get_session():
    """Dependency injection session database"""
    with Session(engine) as session:
        yield session
