import os
import django
from django.db import connections

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

def check_query():
    conn = connections['aws1_global']
    with conn.cursor() as cursor:
        # Check connection charset
        cursor.execute("SELECT @@character_set_connection, @@collation_connection")
        print("Connection status:", cursor.fetchone())
        
        # Run the problematic query
        sql = """
            SELECT 
                menus.Nombre, 
                view_paginas_menus.Nombre AS NombrePagina
            FROM 
                menus
            INNER JOIN 
                view_paginas_menus 
            ON 
                menus.Pagina = view_paginas_menus.Pagina
            WHERE 
                menus.Nombre LIKE '%PESTAÑA%' OR view_paginas_menus.Nombre LIKE '%PESTAÑA%'
                OR menus.Nombre LIKE '%PESTA%A%'
            LIMIT 5
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(f"Found {len(rows)} rows")
        for row in rows:
            print(f"Raw data: {row}")
            for item in row:
                if isinstance(item, str):
                    print(f"String: {item} | Hex: {item.encode('utf-8').hex()}")
                elif isinstance(item, bytes):
                    print(f"Bytes: {item} | Hex: {item.hex()}")

if __name__ == "__main__":
    check_query()
