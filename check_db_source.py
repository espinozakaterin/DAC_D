from django.db import connections

def check_db_source_data(id_suministro):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Consultamos los últimos movimientos con su usuario real
            query = """
                SELECT 
                    id_movimiento, 
                    fecha_movimiento, 
                    detalle_movimiento, 
                    creado_por 
                FROM universal_data_core.suministros_movimientos 
                WHERE id_suministros = %s 
                ORDER BY fecha_movimiento DESC
            """
            cursor.execute(query, [id_suministro])
            rows = cursor.fetchall()
            
            print(f"--- REPORTE DE BASE DE DATOS (Suministro #{id_suministro}) ---")
            print(f"Total registros encontrados: {len(rows)}")
            print("-" * 60)
            print(f"{'ID':<6} | {'FECHA':<12} | {'USUARIO EN BD':<15} | {'DETALLE'}")
            print("-" * 60)
            
            # Verificamos los primeros 10 para no saturar
            for row in rows[:10]:
                id_m, fecha, detalle, usuario = row
                fecha_str = str(fecha).split(' ')[0]
                # Representación clara de vacíos/nulos
                user_display = f"[{usuario}]" if usuario else "(!) VACIO/NULL"
                print(f"{id_m:<6} | {fecha_str:<12} | {user_display:<15} | {detalle}")
            
            if len(rows) > 10:
                print("... (más registros)")
                
    except Exception as e:
        print(f"ERROR DE CONEXION/CONSULTA: {str(e)}")

if __name__ == "__main__":
    check_db_source_data(7)
