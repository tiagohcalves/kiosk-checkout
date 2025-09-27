from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from checkout.utils.logging_config import get_logger
from checkout.models.models import Base

logger = get_logger(__name__)

DATABASE_URL = "sqlite:///./mashgin.db"

logger.info(f"Initializing database connection to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Database engine and session factory created successfully")


# Dependency to get DB session
def get_db():
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Closing database session")
        db.close()


# Create tables
def create_tables():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
