SET NAMES utf8;
USE global_security;
DROP VIEW IF EXISTS view_paginas_menus;
CREATE VIEW view_paginas_menus AS 
select Pagina, Nombre, TipoMenu 
from menus 
where TipoMenu = 1 
order by Pagina;

-- Fix common mojibake characters if they exist
UPDATE menus SET Nombre = REPLACE(Nombre, '‘', 'Ñ');
UPDATE menus SET Nombre = REPLACE(Nombre, '¡', 'á');
UPDATE menus SET Nombre = REPLACE(Nombre, '©', 'é');
UPDATE menus SET Nombre = REPLACE(Nombre, '\xad', 'í');
UPDATE menus SET Nombre = REPLACE(Nombre, '³', 'ó');
UPDATE menus SET Nombre = REPLACE(Nombre, 'º', 'ú');
UPDATE menus SET Nombre = REPLACE(Nombre, '‘', 'Ñ');
