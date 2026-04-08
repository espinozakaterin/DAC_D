import pymysql
import os
from dotenv import load_dotenv

# Path to .env file
dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

def get_triggers_full():
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
            for row in rows:
                if 'devolucion' in str(row).lower():
                    # row[0] is Trigger Name, row[2] is Table
                    # We can use SHOW CREATE TRIGGER name
                    name = row[0]
                    cursor.execute(f"SHOW CREATE TRIGGER {name}")
                    trigger_create = cursor.fetchone()
                    print(f"--- TRIGGER: {name} ---")
                    print(trigger_create[2])
                    print("-" * 50)
        connection.close()
    except Exception as e:
        print(f"Error getting triggers: {str(e)}")

get_triggers_full()
