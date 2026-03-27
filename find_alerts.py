
import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def find():
    with connections['ctrlSum'].cursor() as cursor:
        cursor.execute("""
            SELECT nombre, cantidad_stock, cantidad_minima, estado 
            FROM universal_data_core.suministros 
            WHERE cantidad_stock < cantidad_minima 
              AND cantidad_minima > 0 
              AND estado != 3
        """)
        rows = cursor.fetchall()
        print(f"ALERTA_COUNT: {len(rows)}")
        for r in rows:
            print(f"ALERT: {r[0]} (Stock: {r[1]}, Min: {r[2]})")

if __name__ == "__main__":
    find()
