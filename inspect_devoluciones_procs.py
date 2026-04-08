from django.db import connections
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DAC.settings')
django.setup()

def get_proc_definition(proc_name):
    try:
        with connections['ctrlSum'].cursor() as cursor:
            cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc_name}")
            row = cursor.fetchone()
            if row:
                print(f"--- PROCEDURE: {proc_name} ---")
                print(row[2])
                print("-" * 50)
            else:
                print(f"Procedure {proc_name} not found.")
    except Exception as e:
        print(f"Error getting {proc_name}: {str(e)}")

procs = ['ACTUALIZAR_ESTADO_DEVOLUCION', 'SUM_INSERT_UPDATE_DEVOLUCION', 'GET_DEVOLUCIONES']
for p in procs:
    get_proc_definition(p)
