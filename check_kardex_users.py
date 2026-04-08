import pymysql
import os
from dotenv import load_dotenv

dotenv_path = r'c:\Users\kathe\Documents\DAC_D\dacd\.env'
load_dotenv(dotenv_path)

connection = pymysql.connect(
    host=os.getenv("DB_HOST_CTRL_SUM"),
    user=os.getenv("DB_USER_CTRL_SUM"),
    password=os.getenv("DB_PASSWORD_CTRL_SUM"),
    db=os.getenv("DB_NAME_CTRL_SUM"),
    port=int(os.getenv("DB_PORT_CTRL_SUM", 3306))
)

with connection.cursor() as cursor:
    # Check for null or empty creado_por in suministros_movimientos
    cursor.execute("SELECT id_suministros, detalle_movimiento, creado_por FROM universal_data_core.suministros_movimientos WHERE creado_por IS NULL OR creado_por = '' LIMIT 10")
    rows = cursor.fetchall()
    print("MOVEMENTS WITH NULL/EMPTY CREADO_POR:")
    for r in rows:
        print(r)

connection.close()
