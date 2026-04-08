import mysql.connector
import sys

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # Assuming empty or handled by env
        database="universal_data_core"
    )
    cursor = conn.cursor(dictionary=True)
    
    id_adquisicion = 1
    id_detalle_requisicion = 127
    
    print(f"Checking data for Adquisicion {id_adquisicion}, DetalleRequisicion {id_detalle_requisicion}...")
    
    query = """
    SELECT * 
    FROM detalle_adquisicion 
    WHERE id_adquisicion = %s 
      AND id_detalle_requisicion = %s
    """
    cursor.execute(query, (id_adquisicion, id_detalle_requisicion))
    rows = cursor.fetchall()
    
    if not rows:
        print("No rows found!")
    else:
        print(f"Found {len(rows)} rows:")
        total_cantidad = 0
        for i, row in enumerate(rows):
            print(f"Row {i+1}: ID={row.get('id_detalle_adquisicion')}, Cant={row.get('cantidad')}, Suministro={row.get('id_suministros')}")
            total_cantidad += row.get('cantidad', 0)
        print(f"Total SUM(cantidad): {total_cantidad}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
