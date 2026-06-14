import os
import psycopg2
from dotenv import load_dotenv

# טעינת המשתנים מתוך קובץ ה- .env של הפרויקט שלך
load_dotenv()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            # כאן אנחנו מושכים בדיוק את מה שהגדרת בקובץ הדוקר!
            database=os.getenv("DB_NAME_SECRET", "postgres"), 
            user=os.getenv("DB_USER_SECRET", "postgres"),
            password=os.getenv("DB_PASSWORD_SECRET"),
            port="5432"
        )
        return connection
    except Exception as e:
        print(f"שגיאה בהתחברות לבסיס הנתונים: {e}")
        return None