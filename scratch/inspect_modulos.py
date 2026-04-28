from django.db import connections
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def inspect_modulos():
    try:
        with connections['aws1_global'].cursor() as cursor:
            cursor.execute("SELECT * FROM modulos LIMIT 1")
            column_names = [desc[0] for desc in cursor.description]
            print(f"Columns in modulos table: {column_names}")
    except Exception as e:
        print(f"Error inspecting modulos: {e}")

if __name__ == "__main__":
    inspect_modulos()
