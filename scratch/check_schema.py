import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def check_tables():
    conn = connections['aws1_global']
    with conn.cursor() as cursor:
        # Get tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables in aws1_global:")
        for t in tables:
            print(f"- {t}")
        
        # Check for specific interesting tables
        for t in ['usuarios', 'acciones_usuario', 'log_accesos', 'bitacora']:
            if t in tables:
                print(f"\nSchema for {t}:")
                cursor.execute(f"SELECT TOP 1 * FROM {t}")
                print([d[0] for d in cursor.description])

if __name__ == "__main__":
    check_tables()
