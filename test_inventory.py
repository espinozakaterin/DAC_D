
import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def audit():
    print("--- AUDITORIA DE STOCK REAL ---")
    with connections['ctrlSum'].cursor() as cursor:
        cursor.execute("SELECT nombre, cantidad_stock, cantidad_minima, estado FROM universal_data_core.suministros")
        rows = cursor.fetchall()
        
        print(f"Total de registros: {len(rows)}")
        print(f"{'Nombre':<30} | {'Stock':<6} | {'Min':<6} | {'Estado':<6} | {'¿BAJO?':<6}")
        print("-" * 65)
        
        count_bajo = 0
        for r in rows:
            is_bajo = r[1] < r[2] and r[2] > 0 and r[3] != 3
            if is_bajo:
                count_bajo += 1
            status = "SI" if is_bajo else "NO"
            print(f"{r[0][:30]:<30} | {r[1]:<6} | {r[2]:<6} | {r[3]:<6} | {status:<6}")
            
    print("-" * 65)
    print(f"RESUMEN: Se encontraron {count_bajo} productos con STOCK < MIN (y habilitados).")

if __name__ == "__main__":
    audit()
