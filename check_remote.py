
import os
import django
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def check_remote():
    # Use 'dac' or 'control_total' as they point to the remote 3.230.160.184
    conn_name = 'dac' 
    print(f"--- CHEQUEANDO BASE REMOTA ({conn_name}) ---")
    try:
        with connections[conn_name].cursor() as cursor:
            cursor.execute("""
                SELECT nombre, cantidad_stock, cantidad_minima, estado 
                FROM universal_data_core.suministros 
                WHERE cantidad_stock < cantidad_minima 
                  AND cantidad_minima > 0 
                  AND estado != 3
            """)
            rows = cursor.fetchall()
            print(f"REMOTE_ALERTA_COUNT: {len(rows)}")
            for r in rows:
                print(f"REMOTE_ALERT: {r[0]} (Stock: {r[1]}, Min: {r[2]})")
    except Exception as e:
        print(f"Error connecting to {conn_name}: {e}")

if __name__ == "__main__":
    check_remote()
