import MySQLdb

def recreate_view():
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="hola123", db="global_security", charset='utf8')
        cursor = db.cursor()
        
        # Set session charsets to UTF8
        cursor.execute("SET NAMES utf8")
        cursor.execute("SET character_set_client = utf8")
        cursor.execute("SET character_set_results = utf8")
        cursor.execute("SET character_set_connection = utf8")
        
        cursor.execute("DROP VIEW IF EXISTS view_paginas_menus")
        cursor.execute("""
            CREATE VIEW view_paginas_menus AS 
            select Pagina, Nombre, TipoMenu 
            from menus 
            where TipoMenu = 1 
            order by Pagina
        """)
        
        db.commit()
        print("View recreated with UTF8 client.")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    recreate_view()
