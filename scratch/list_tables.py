
import pymysql

# Try to get credentials from environment or use defaults from settings.py
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
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in global_security:")
    for (table_name,) in tables:
        print(f"- {table_name}")
    
    # Also check if there's any table related to logs or alerts
    print("\nSearching for log, alert, access related tables...")
    cursor.execute("SHOW TABLES WHERE `Tables_in_global_security` LIKE '%log%' OR `Tables_in_global_security` LIKE '%acceso%' OR `Tables_in_global_security` LIKE '%bitacora%' OR `Tables_in_global_security` LIKE '%alerta%'")
    results = cursor.fetchall()
    if results:
        for (table_name,) in results:
            print(f"- {table_name}")
    else:
        print("No specific log/access/alert tables found by name pattern.")

    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
