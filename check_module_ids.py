import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def check_grupos_and_modulos():
    try:
        udcConn = connections['aws1_global']
        with udcConn.cursor() as cursor:
            print("--- Modules ---")
            cursor.execute("SELECT PKmodulo, Nombre FROM modulos LIMIT 10")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Name: {row[1]}")

            print("\n--- Groups (Sample) ---")
            cursor.execute("SELECT PKgrupo, Nombre, fkModulo FROM grupos LIMIT 10")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Name: {row[1]}, fkModulo: {row[2]}")
            
            print("\n--- Count by fkModulo ---")
            cursor.execute("SELECT fkModulo, COUNT(*) FROM grupos GROUP BY fkModulo")
            for row in cursor.fetchall():
                print(f"fkModulo ID: {row[0]}, Count: {row[1]}")

        udcConn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_grupos_and_modulos()
