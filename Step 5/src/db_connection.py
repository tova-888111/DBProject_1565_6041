import os
import psycopg2
from dotenv import load_dotenv

# מחפש את קובץ ה- .env שנמצא בשורש הפרויקט (שתי תיקיות למעלה)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database=os.getenv("DB_NAME_SECRET", "postgres"), 
            user=os.getenv("DB_USER_SECRET", "postgres"),
            password=os.getenv("DB_PASSWORD_SECRET"),
            port="5432"
        )
        return connection
    except Exception as e:
        print(f"שגיאה בהתחברות לבסיס הנתונים: {e}")
        return None