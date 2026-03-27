import os
import django
from django.db import connections

def dump():
    with open('full_diag.txt', 'a', encoding='utf-8') as f:
        c = connections['ctrlSum']
        with c.cursor() as cur:
            f.write("\n--- PROCEDURES ---\n")
            
            procs = ['SUM_GET_SUMINISTROS', 'SUM_GET_CATEGORIAS', 'SUM_GET_ALMACENES']
            for proc in procs:
                try:
                    cur.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc}")
                    row = cur.fetchone()
                    f.write(f"\nPROCEDURE: {proc}\n")
                    f.write(str(row[2]) + "\n")
                except Exception as e:
                    f.write(f"Error getting {proc}: {str(e)}\n")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
    django.setup()
    dump()
