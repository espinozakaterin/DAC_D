import MySQLdb

try:
    conn = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="hola123",
        db="global_security"
    )
    cursor = conn.cursor()
    cursor.execute("DESCRIBE usuarios")
    print("COLUMNS IN usuarios:")
    for col in cursor.fetchall():
        print(f"- {col[0]} ({col[1]})")
    
    cursor.execute("SHOW TABLES")
    print("\nTABLES IN global_security:")
    for t in cursor.fetchall():
        print(f"- {t[0]}")
        
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
