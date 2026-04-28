SET NAMES utf8mb4;
USE global_security;

-- Force database and tables to utf8mb4
ALTER DATABASE global_security CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE menus CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE modulos CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE grupos CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Recreate views one more time
DROP VIEW IF EXISTS view_paginas_menus;
CREATE VIEW view_paginas_menus AS 
select Pagina, Nombre, TipoMenu 
from menus 
where TipoMenu = 1 
order by Pagina;
