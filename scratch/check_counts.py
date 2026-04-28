
import pymysql

db_config = {
    'user': 'root',
    'password': 'hola123',
    'host': 'localhost',
    'database': 'global_security',
    'port': 3306
}

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    print("Checking counts:")
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE Estado = 1")
    print(f"Usuarios Activos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM modulos")
    print(f"Modulos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM acciones_usuario")
    print(f"Acciones Usuario (Authorizations): {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM errorlog")
    print(f"Error Log Count: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT * FROM errorlog ORDER BY FechaHora DESC LIMIT 5")
    errors = cursor.fetchall()
    if errors:
        print("\nRecent Error Logs:")
        for error in errors:
            print(error)
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
