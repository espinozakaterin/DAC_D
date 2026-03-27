-- SQL Script to fix the 'definer does not exist' error for login procedures
-- This script recreates the procedures with the EXACT original logic from the remote server
-- but using SQL SECURITY INVOKER to avoid the invalid definer issue.

DELIMITER //

-- Recreating SDK_GET_USER_ACCESS with ORIGINAL REMOTE LOGIC
DROP PROCEDURE IF EXISTS SDK_GET_USER_ACCESS //

CREATE PROCEDURE SDK_GET_USER_ACCESS(IN varUSER varchar(50), IN varPass varchar(50))
SQL SECURITY INVOKER
BEGIN
  SELECT
    u.PKUsuario,
    u.Nombre,
    u.Usuario,
    u.Contrasena
  FROM usuarios u
  WHERE u.Usuario = varUSER
  AND (u.Contrasena = varPass
  OR Contrasena LIKE CONCAT('%', varPass, '%'))
  AND u.Estado = 1
  GROUP BY u.PKUsuario;
END //

-- Recreating SDK_GET_USER_MODULE_ACCESS with ORIGINAL REMOTE LOGIC
DROP PROCEDURE IF EXISTS SDK_GET_USER_MODULE_ACCESS //

CREATE PROCEDURE SDK_GET_USER_MODULE_ACCESS(IN varModulo int, IN varUser int)
SQL SECURITY INVOKER
BEGIN
  SELECT
    *
  FROM usuarios_modulo um
  WHERE um.fkModulo = varModulo
  AND um.fkUsuario = varUser;
END //

DELIMITER ;
