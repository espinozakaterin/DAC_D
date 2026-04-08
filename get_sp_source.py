from django.db import connections

def get_sp_code(proc_name):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute(f"SHOW CREATE PROCEDURE {proc_name}")
            result = cursor.fetchone()
            if result:
                print(f"--- SCRIPT DEL PROCEDIMIENTO {proc_name} ---")
                print(result[2])
            else:
                # Intentar con el prefijo
                cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc_name}")
                result = cursor.fetchone()
                if result:
                    print(f"--- SCRIPT DEL PROCEDIMIENTO universal_data_core.{proc_name} ---")
                    print(result[2])
                else:
                    print(f"No se encontró el procedimiento {proc_name}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

get_sp_code('OBTENER_HISTORIAL_KARDEX')
