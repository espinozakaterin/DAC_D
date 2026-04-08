import pymysql
import os
from dotenv import load_dotenv

# Path to .env file
dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

def save_proc_definition(proc_name):
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST_CTRL_SUM"),
            user=os.getenv("DB_USER_CTRL_SUM"),
            password=os.getenv("DB_PASSWORD_CTRL_SUM"),
            db=os.getenv("DB_NAME_CTRL_SUM"),
            port=int(os.getenv("DB_PORT_CTRL_SUM", 3306))
        )
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"SHOW CREATE PROCEDURE {proc_name}")
            except:
                try:
                    cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc_name}")
                except:
                    print(f"Procedure {proc_name} not found in default or universal_data_core.")
                    return
            
            row = cursor.fetchone()
            if row:
                filename = f"{proc_name}.sql"
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(row[2])
                print(f"Saved {proc_name} to {filename}")
            else:
                print(f"Procedure {proc_name} not found.")
        connection.close()
    except Exception as e:
        print(f"Error getting {proc_name}: {str(e)}")

procs = ['SUM_INSERT_UPDATE_ASIGNACION', 'OBTENER_HISTORIAL_KARDEX', 'SUM_GET_ASIGNACIONES']
for p in procs:
    save_proc_definition(p)
