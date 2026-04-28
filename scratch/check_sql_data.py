import re

def check_sql_data():
    sql_file = r'c:\Users\kathe\Documents\DAC_D\global_security.sql'
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Find menus for ID 21
    # INSERT INTO menus VALUES (PKMenu, fkModulo, ...)
    menus_matches = re.findall(r'\(\d+,\s*21,', content)
    
    # Find grupos for ID 21
    # INSERT INTO grupos VALUES (PKgrupo, Nombre, Descripcion, IsBuiltIn, fkModulo, ...)
    # Wait, let's see the insert statement for grupos
    # (232, 'APARTADO DE EMPLEADOS', 'USUARIOS CON ACCESO AL APARTADO DE EMPLEADOS DE TH', b'0', 19, b'0')
    grupos_matches = re.findall(r'\(.*?,.*?,.*?,.*?, 21,', content)
    
    print(f"Menus for ID 21: {len(menus_matches)}")
    print(f"Grupos for ID 21: {len(grupos_matches)}")

if __name__ == "__main__":
    check_sql_data()
