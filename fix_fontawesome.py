import os
import re

files_to_fix = [
    r'c:\Users\kathe\Documents\DAC_D\TICKETIT\templates\TICKETIT_MAIN.html',
    r'c:\Users\kathe\Documents\DAC_D\TALENTO\templates\menu_empleado.html',
    r'c:\Users\kathe\Documents\DAC_D\TALENTO\templates\lobby.html',
    r'c:\Users\kathe\Documents\DAC_D\KANBAN\templates\kanban\lobby.html',
    r'c:\Users\kathe\Documents\DAC_D\KANBAN\templates\kanban\menu.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\distribuciones_programaciones.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\modal_crear_programacion copy.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\plantilla.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\modal_ventas_perdidas.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\plantilla_nueva.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\programacion_modal.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\myapp\modal_crear_programacion.html',
    r'c:\Users\kathe\Documents\DAC_D\myapp\templates\modal_crear_programacion.html',
    r'c:\Users\kathe\Documents\DAC_D\DAC\templates\DAC_MAIN.html',
    r'c:\Users\kathe\Documents\DAC_D\CONTABLE\templates\componentes\menu_contable.html',
    r'c:\Users\kathe\Documents\DAC_D\CWS\templates\modulos.html'
]

old_script = '<script src="https://kit.fontawesome.com/e716b78aa6.js" crossorigin="anonymous"></script>'
new_link = '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" rel="stylesheet">'

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_script in content:
            new_content = content.replace(old_script, new_link)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed: {file_path}")
        else:
            print(f"Not found in: {file_path}")
    else:
        print(f"Missing: {file_path}")
