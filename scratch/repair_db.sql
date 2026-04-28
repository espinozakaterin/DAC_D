SET NAMES utf8mb4;
USE global_security;

-- Repair known broken patterns in menus table
UPDATE menus SET Nombre = REPLACE(Nombre, 'PESTA??A', 'PESTAÑA');
UPDATE menus SET Nombre = REPLACE(Nombre, 'Gesti??n', 'Gestión');
UPDATE menus SET Nombre = REPLACE(Nombre, 'Configuraci??n', 'Configuración');
UPDATE menus SET Nombre = REPLACE(Nombre, 'Solicitud??', 'Solicitud');
UPDATE menus SET Nombre = REPLACE(Nombre, '??', 'Ñ') WHERE Nombre LIKE '%PESTA??A%';
UPDATE menus SET Nombre = REPLACE(Nombre, '??', 'ó') WHERE Nombre LIKE '%Gesti??n%';
UPDATE menus SET Nombre = REPLACE(Nombre, '??', 'ó') WHERE Nombre LIKE '%Configuraci??n%';

-- Also check modulos table
UPDATE modulos SET Nombre = REPLACE(Nombre, '??', 'Ñ') WHERE Nombre LIKE '%??%';

-- Final check on the view
DROP VIEW IF EXISTS view_paginas_menus;
CREATE VIEW view_paginas_menus AS 
select Pagina, Nombre, TipoMenu 
from menus 
where TipoMenu = 1 
order by Pagina;
