import pymysql
import os
from dotenv import load_dotenv

# Path to .env file
dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

def save_trigger_definition(name):
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST_CTRL_SUM"),
            user=os.getenv("DB_USER_CTRL_SUM"),
            password=os.getenv("DB_PASSWORD_CTRL_SUM"),
            db=os.getenv("DB_NAME_CTRL_SUM"),
            port=int(os.getenv("DB_PORT_CTRL_SUM", 3306))
        )
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW CREATE TRIGGER {name}")
            row = cursor.fetchone()
            if row:
                filename = f"TRIGGER_{name}.sql"
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(row[2])
                print(f"Saved trigger {name} to {filename}")
        connection.close()
    except Exception as e:
        print(f"Error getting trigger {name}: {str(e)}")

def get_trigger_names():
    names = []
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
                    names.append(row[0])
        connection.close()
    except Exception as e:
        print(f"Error listing triggers: {str(e)}")
    return names

for name in get_trigger_names():
    save_trigger_definition(name)
