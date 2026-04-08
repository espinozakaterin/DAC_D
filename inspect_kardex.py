import os
import django
from django.db import connections

# Configuración básica para usar Django fuera de su entorno habitual
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def inspect_kardex_fields(id_suministro):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamamos al procedimiento con parámetros dummy (id_suministro, 0, None, None)
            # El SP espera: id_categoria, id_suministro, fecha_desde, fecha_hasta
            cursor.callproc('OBTENER_HISTORIAL_KARDEX', [None, id_suministro, None, None])
            
            # Obtener nombres de columnas
            columns = [col[0] for col in cursor.description]
            print(f"COLUMNAS DETECTADAS: {columns}")
            
            result = cursor.fetchone()
            if result:
                print(f"DATOS PRIMERA FILA: {result}")
            else:
                print("No se encontraron movimientos para el suministro.")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

# Probamos con un ID de suministro (según la captura es el 7)
if __name__ == '__main__':
    inspect_kardex_fields(7)
