import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Create a PostgreSQL connection using values from .env."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME_SECRET", os.getenv("DB_NAME", "postgres")),
            user=os.getenv("DB_USER_SECRET", os.getenv("DB_USER", "postgres")),
            password=os.getenv("DB_PASSWORD_SECRET", os.getenv("DB_PASSWORD", "")),
            port=os.getenv("DB_PORT", "5432"),
        )
    except Exception as error:
        print(f"Database connection error: {error}")
        return None
