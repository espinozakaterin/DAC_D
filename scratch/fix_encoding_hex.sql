SET NAMES utf8;
USE global_security;

-- Fix common mojibake characters using HEX to be sure
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C291'), 'Ñ');
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8E28093'), 'ó'); -- Variant
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C2A1'), 'á');
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C2A9'), 'é');
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C2AD'), 'í');
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C2B3'), 'ó');
UPDATE menus SET Nombre = REPLACE(Nombre, UNHEX('EF9FB8C2BA'), 'ú');
