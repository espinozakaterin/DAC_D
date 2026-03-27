from django.db import connections

def check_stock():
    udcConn = connections['ctrlSum']
    with udcConn.cursor() as cursor:
        cursor.execute("""
            SELECT id_suministro, nombre, cantidad_stock, cantidad_minima
            FROM universal_data_core.suministros
        """)
        all_items = cursor.fetchall()
        
        print("Total Suministros:", len(all_items))
        low_stock_count = 0
        for item in all_items:
            id_sum, nombre, stock, min_stock = item
            if stock is not None and min_stock is not None and stock <= min_stock and min_stock > 0:
                low_stock_count += 1
                print(f"LOW STOCK MATCH -> ID: {id_sum}, Nombre: {nombre.encode('utf-8')}, Stock: {stock}, Minimo: {min_stock}")
                
        print(f"\nItems where stock <= min_stock AND min_stock > 0: {low_stock_count}")

check_stock()
