import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\kathe\Documents\DAC_D\DAC_D')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def debug_procedure():
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Try with a known ID if possible, or just 3 as seen in screenshot
            id_adquisicion = 3
            id_requisicion = 89 # from screenshot
            print(f"Calling universal_data_core.OBTENER_DETALLE_ADQUISICION({id_adquisicion}, {id_requisicion})...")
            cursor.callproc('universal_data_core.OBTENER_DETALLE_ADQUISICION', [id_adquisicion, id_requisicion])
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                print(f"Columns: {columns}")
                rows = cursor.fetchall()
                for i, row in enumerate(rows):
                    print(f"Row {i}: {dict(zip(columns, row))}")
            else:
                print("No description returned.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_procedure()
