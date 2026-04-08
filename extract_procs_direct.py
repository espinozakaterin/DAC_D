import pymysql
import os
from dotenv import load_dotenv

# Path to .env file
dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

def get_proc_definition(proc_name):
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST_CTRL_SUM"),
            user=os.getenv("DB_USER_CTRL_SUM"),
            password=os.getenv("DB_PASSWORD_CTRL_SUM"),
            db=os.getenv("DB_NAME_CTRL_SUM"),
            port=int(os.getenv("DB_PORT_CTRL_SUM", 3306))
        )
        with connection.cursor() as cursor:
            # Try with and without database prefix
            try:
                cursor.execute(f"SHOW CREATE PROCEDURE {proc_name}")
            except:
                cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc_name}")
            
            row = cursor.fetchone()
            if row:
                print(f"\n--- PROCEDURE: {proc_name} ---")
                print(row[2])
                print("-" * 50)
            else:
                print(f"\nProcedure {proc_name} not found.")
        connection.close()
    except Exception as e:
        print(f"\nError getting {proc_name}: {str(e)}")

procs = ['ACTUALIZAR_ESTADO_DEVOLUCION', 'SUM_INSERT_UPDATE_DEVOLUCION', 'GET_DEVOLUCIONES']
for p in procs:
    get_proc_definition(p)
