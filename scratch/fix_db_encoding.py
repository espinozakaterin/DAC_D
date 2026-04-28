import MySQLdb

def fix_db():
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="hola123", db="global_security", charset='utf8')
        cursor = db.cursor()
        
        # Recreate view with UTF8 connection
        cursor.execute("DROP VIEW IF EXISTS view_paginas_menus")
        cursor.execute("""
            CREATE VIEW view_paginas_menus AS 
            select Pagina, Nombre, TipoMenu 
            from menus 
            where TipoMenu = 1 
            order by Pagina
        """)
        
        # Check current data
        cursor.execute("SELECT Nombre FROM menus WHERE Nombre LIKE '%PESTA%A%' LIMIT 1")
        row = cursor.fetchone()
        print(f"Current Nombre: {row[0]}")
        
        # If it's broken, try to fix it
        # This is a risky operation, but if it's already broken...
        # We replace the common broken patterns
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '‘', 'Ñ')")
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '–', 'ó')") # Common variants
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '³', 'ó')")
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '¡', 'á')")
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '©', 'é')")
        cursor.execute("UPDATE menus SET Nombre = REPLACE(Nombre, '\xad', 'í')")
        
        db.commit()
        print("DB Fixed.")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
