import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def list_all_tables():
    conn = connections['aws1_global']
    with conn.cursor() as cursor:
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        print("ALL TABLES IN aws1_global:")
        for t in sorted(tables):
            print(f"- {t}")

if __name__ == "__main__":
    list_all_tables()
