from django.db import connections
def get_sp_info():
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Intentar obtener el script de creación
            cursor.execute("SHOW CREATE PROCEDURE universal_data_core.OBTENER_HISTORIAL_KARDEX")
            result = cursor.fetchone()
            if result:
                print("--- SCRIPT DEL PROCEDIMIENTO ---")
                print(result[2])
            else:
                print("No se encontró el procedimiento en universal_data_core")
    except Exception as e:
        print(f"ERROR: {str(e)}")

get_sp_info()
