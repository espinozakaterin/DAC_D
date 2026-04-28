import os
import django
from django.db import connections

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def inspect_modulos_content():
    try:
        conn = connections['aws1_global']
        with conn.cursor() as cursor:
            # Get all modules
            cursor.execute("SELECT PKModulo, Nombre FROM modulos ORDER BY Nombre")
            modulos = cursor.fetchall()
            
            print(f"{'ID':<5} | {'Nombre':<30} | {'Menus':<6} | {'Grupos':<6}")
            print("-" * 55)
            
            for pk, nombre in modulos:
                # Count menus
                cursor.execute("SELECT COUNT(*) FROM menus WHERE fkModulo = %s", [pk])
                menu_count = cursor.fetchone()[0]
                
                # Count groups
                cursor.execute("SELECT COUNT(*) FROM grupos WHERE fkModulo = %s", [pk])
                grupo_count = cursor.fetchone()[0]
                
                print(f"{pk:<5} | {nombre:<30} | {menu_count:<6} | {grupo_count:<6}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_modulos_content()
