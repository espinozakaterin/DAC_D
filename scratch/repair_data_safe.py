import MySQLdb

def repair_data():
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="hola123", db="global_security", charset='utf8mb4')
        cursor = db.cursor()
        
        # Search for broken strings
        cursor.execute("SELECT PKMenu, Nombre FROM menus WHERE Nombre LIKE '%?%'")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} potentially broken rows")
        
        for pk, nombre in rows:
            new_nombre = nombre.replace('??', 'Ñ').replace('?', 'ñ') # Simple heuristic
            # Better: specific replacements
            new_nombre = nombre.replace('PESTA??A', 'PESTAÑA')
            new_nombre = new_nombre.replace('Gesti??n', 'Gestión')
            new_nombre = new_nombre.replace('Configuraci??n', 'Configuración')
            
            if new_nombre != nombre:
                cursor.execute("UPDATE menus SET Nombre = %s WHERE PKMenu = %s", (new_nombre, pk))
        
        db.commit()
        print("Data repaired.")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    repair_data()
