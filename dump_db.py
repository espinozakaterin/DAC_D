
import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def dump():
    with connections['ctrlSum'].cursor() as cursor:
        cursor.execute("SELECT nombre, cantidad_stock, cantidad_minima FROM universal_data_core.suministros WHERE estado != 3")
        rows = cursor.fetchall()
        for r in rows:
            print(f"PRODUCTO: {r[0]} | STOCK: {r[1]} | MIN: {r[2]}")

if __name__ == "__main__":
    dump()
