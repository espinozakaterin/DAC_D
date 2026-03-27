
import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def schema():
    with connections['ctrlSum'].cursor() as cursor:
        cursor.execute("DESCRIBE universal_data_core.suministros")
        rows = cursor.fetchall()
        for r in rows:
            print(f"FIELD: {r[0]} | TYPE: {r[1]}")

if __name__ == "__main__":
    schema()
