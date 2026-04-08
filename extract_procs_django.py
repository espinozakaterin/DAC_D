import os
import sys
import django

# Set up Django environment
sys.path.append(r'c:\Users\kathe\Documents\DAC_D')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def save_proc_definition(proc_name):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            try:
                cursor.execute(f"SHOW CREATE PROCEDURE {proc_name}")
            except:
                try:
                    cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{proc_name}")
                except:
                    print(f"Procedure {proc_name} not found.")
                    return
            
            row = cursor.fetchone()
            if row:
                filename = f"{proc_name}.sql"
                with open(filename, "w", encoding='utf-8') as f:
                    # row index might be 2 or 3 depending on MySQL version and driver
                    # SHOW CREATE PROCEDURE returns Procedure, sql_mode, Create Procedure, character_set_client, ...
                    f.write(row[2])
                print(f"Saved {proc_name} to {filename}")
            else:
                print(f"Procedure {proc_name} not found.")
    except Exception as e:
        print(f"Error getting {proc_name}: {str(e)}")

procs = ['SUM_INSERT_UPDATE_ASIGNACION', 'OBTENER_HISTORIAL_KARDEX', 'SUM_GET_ASIGNACIONES']
for p in procs:
    save_proc_definition(p)
