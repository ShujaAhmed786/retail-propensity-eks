import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

def get_db_engine():
    """
    Creates and returns a SQLAlchemy database engine using environment variables.
    Provides graceful error handling if credentials or database connections fail.
    """
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "customer_behaviour")

    # Construct connection string dynamically
    connection_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    try:
        engine = create_engine(connection_uri)
        # Verify connection handshake immediately
        with engine.connect() as conn:
            pass
        return engine
    except SQLAlchemyError as e:
        print(f"Database Engine Connection Failed: {e}")
        return None
