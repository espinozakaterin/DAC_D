import pymysql
import os
from dotenv import load_dotenv

# Path to .env file
dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

def get_triggers():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST_CTRL_SUM"),
            user=os.getenv("DB_USER_CTRL_SUM"),
            password=os.getenv("DB_PASSWORD_CTRL_SUM"),
            db=os.getenv("DB_NAME_CTRL_SUM"),
            port=int(os.getenv("DB_PORT_CTRL_SUM", 3306))
        )
        with connection.cursor() as cursor:
            cursor.execute("SHOW TRIGGERS")
            rows = cursor.fetchall()
            if rows:
                print(f"--- TRIGGERS ---")
                for row in rows:
                    if 'devolucion' in str(row).lower():
                        print(f"Trigger: {row[0]}, Table: {row[2]}, Event: {row[1]}, Timing: {row[3]}")
                        print(f"Statement: {row[4]}")
                        print("-" * 50)
            else:
                print("No triggers found.")
        connection.close()
    except Exception as e:
        print(f"Error getting triggers: {str(e)}")

get_triggers()
