import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def list_tables():
    conn = connections['aws1_global']
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("TABLES IN aws1_global:")
        for t in tables:
            print(f"- {t[0]}")

if __name__ == "__main__":
    try:
        list_tables()
    except Exception as e:
        print(f"ERROR: {e}")
