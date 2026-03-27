import os
import sys
import django

sys.path.append(r"c:\Users\kathe\Documents\DAC_D\DAC_D")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dacd.settings")
django.setup()

from django.db import connections

def check():
    try:
        with connections['global_nube'].cursor() as cursor:
            cursor.execute("SHOW CREATE PROCEDURE SDK_GET_USER_ACCESS")
            print("\n=== PROCEDURE ===")
            for row in cursor.fetchall():
                print(row[2])
                
            cursor.execute("SELECT * FROM usuarios WHERE userName = 'PASANTEIT'")
            print("\n=== USER PASANTEIT ===")
            cols = [col[0] for col in cursor.description]
            print("\t".join(cols))
            for row in cursor.fetchall():
                print("\t".join(str(r) for r in row))
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check()
