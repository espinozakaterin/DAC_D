import os
import django
import sys

# Setup django
sys.path.append(r'c:\Users\kathe\Documents\DAC_D')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacd.settings')
django.setup()

from django.db import connections

def check_data():
    try:
        udcConn = connections['aws1_global']
        with udcConn.cursor() as cursor:
            # 1. Get Modulo ID for TALENTO_HUMANO
            cursor.execute("SELECT PKModulo, Nombre FROM modulos WHERE Nombre = 'TALENTO_HUMANO'")
            modulo = cursor.fetchone()
            if not modulo:
                print("Modulo TALENTO_HUMANO not found")
                return
            pk_modulo = modulo[0]
            print(f"Modulo: {modulo[1]} (ID: {pk_modulo})")

            # 2. Get Grupo ID for APARTADO DE EMPLEADOS
            cursor.execute("SELECT PKgrupo, Nombre FROM grupos WHERE Nombre = 'APARTADO DE EMPLEADOS' AND fkModulo = %s", [pk_modulo])
            grupo = cursor.fetchone()
            if not grupo:
                print("Grupo APARTADO DE EMPLEADOS not found in this module")
                return
            pk_grupo = grupo[0]
            print(f"Grupo: {grupo[1]} (ID: {pk_grupo})")

            # 3. Check Asignadas (simulating mySP_Select_Acciones_Grupo)
            # mySP_Select_Acciones_Grupo [varGrupo, varModulo]
            cursor.callproc("mySP_Select_Acciones_Grupo", [pk_grupo, pk_modulo])
            asignadas = cursor.fetchall()
            print(f"Acciones Asignadas: {len(asignadas)}")
            for a in asignadas:
                print(f"  - {a}")

            # 4. Check Disponibles (simulating mySP_Select_Acciones_NoExisten_Grupo)
            # mySP_Select_Acciones_NoExisten_Grupo [varGrupo, varModulo]
            cursor.callproc("mySP_Select_Acciones_NoExisten_Grupo", [pk_grupo, pk_modulo])
            disponibles = cursor.fetchall()
            print(f"Acciones Disponibles: {len(disponibles)}")
            for d in disponibles:
                print(f"  - {d}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
