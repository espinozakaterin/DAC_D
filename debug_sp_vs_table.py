from django.db import connections

def debug_data_match(id_suministro):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # 1. Datos del SP
            cursor.callproc('OBTENER_HISTORIAL_KARDEX', [None, id_suministro, None, None])
            cols_sp = [col[0] for col in cursor.description]
            row_sp = cursor.fetchone()
            
            print(f"SP COLUMNS: {cols_sp}")
            if row_sp:
                print(f"SP FIRST ROW: {dict(zip(cols_sp, row_sp))}")
            
            # 2. Datos de la Tabla
            cursor.execute("SELECT * FROM universal_data_core.suministros_movimientos WHERE id_suministros = %s ORDER BY fecha_movimiento DESC LIMIT 1", [id_suministro])
            cols_tbl = [col[0] for col in cursor.description]
            row_tbl = cursor.fetchone()
            
            print(f"TABLE COLUMNS: {cols_tbl}")
            if row_tbl:
                print(f"TABLE FIRST ROW: {dict(zip(cols_tbl, row_tbl))}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

debug_data_match(7)
