from django.db import connections

def check():
    c = connections['ctrlSum']
    with c.cursor() as cur:
        # Check table structure
        cur.execute("DESCRIBE universal_data_core.suministros")
        print("TABLE STRUCTURE:")
        for row in cur.fetchall():
            print(row)
            
        # Check all data
        cur.execute("SELECT nombre, cantidad_stock, cantidad_minima FROM universal_data_core.suministros")
        print("\nALL SUPPLIES:")
        for row in cur.fetchall():
            print(row)
            
        # Check the exact query from views
        query = """
            SELECT s.nombre, s.cantidad_stock, s.cantidad_minima
            FROM universal_data_core.suministros s
            WHERE s.cantidad_stock <= s.cantidad_minima
              AND s.cantidad_minima > 0
            ORDER BY s.cantidad_stock ASC
        """
        cur.execute(query)
        print("\nQUERY RESULTS (stock <= min_stock AND min_stock > 0):")
        results = cur.fetchall()
        for row in results:
            print(row)
        print(f"Total found: {len(results)}")

if __name__ == '__main__':
    check()
