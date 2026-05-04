import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def get_sp_definition(sp_name):
    try:
        with connections['ctrlSum'].cursor() as cursor:
            cursor.execute(f"SHOW CREATE PROCEDURE universal_data_core.{sp_name}")
            row = cursor.fetchone()
            if row:
                print(f"--- Definition of {sp_name} ---")
                print(row[2])
            else:
                print(f"Procedure {sp_name} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_sp_definition('GET_REQUISICIONES')
