from django.db import connections

def inspect_alternate_kardex(id_suministro):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamamos al procedimiento alternativo
            cursor.callproc('universal_data_core.OBTENER_MOVIMIENTO_X_SUMINISTRO', [id_suministro])
            
            # Obtener nombres de columnas
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                print(f"COLUMNAS DETECTADAS (ALT): {columns}")
                
                result = cursor.fetchone()
                if result:
                    print(f"DATOS PRIMERA FILA (ALT): {dict(zip(columns, result))}")
            else:
                print("El SP no devolvió un conjunto de resultados.")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

# Probar con suministro 7
inspect_alternate_kardex(7)
exit()
