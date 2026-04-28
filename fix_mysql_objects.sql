-- Script to fix the 'definer does not exist' error by replacing 'bart100'@'%' with 'root'@'localhost'
-- Target Database: global_security

DELIMITER //

-- Procedures
DROP PROCEDURE IF EXISTS mySP_Select_Usuarios_NoExisten_Grupo //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Grupo`(IN p01_fkGrupo int(11))
BEGIN
  SELECT
    usuarios.PKUsuario AS fkUsuario,
    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,
    Usuario
  FROM usuarios
  WHERE NOT EXISTS (SELECT
      *
    FROM usuarios_grupo
    WHERE usuarios_grupo.fkGrupo = p01_fkGrupo
    AND usuarios.PKUsuario = usuarios_grupo.fkUsuario)
  AND Estado = 1
  ORDER BY Nombres;
END //

DROP PROCEDURE IF EXISTS mySP_Select_Usuarios_NoExisten_Kimb //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Kimb`(IN p01_fkKimberly int(11))
BEGIN
  SELECT
    u.PKUsuario AS fkUsuario,
    CONCAT(u.Nombre, ' ', u.Apellido) AS Nombres,
    u.Usuario
  FROM usuarios u
  WHERE NOT EXISTS (SELECT
      *
    FROM usuarios_kimberly uk
    WHERE u.PKUsuario = uk.fkUsuario)
  ORDER BY Nombres;
END //

DROP PROCEDURE IF EXISTS mySP_Select_Usuarios_NoExisten_Menu //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Menu`(IN p01_fkMenu int(11))
BEGIN
  SELECT
    usuarios.PKUsuario AS fkUsuario,
    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,
    Usuario
  FROM usuarios
  WHERE NOT EXISTS (SELECT
      *
    FROM menus_usuario
    WHERE menus_usuario.fkMenu = p01_fkMenu
    AND usuarios.PKUsuario = menus_usuario.fkUsuario)
  AND Estado = 1
  ORDER BY Nombres;
END //

DROP PROCEDURE IF EXISTS mySP_Select_Usuarios_NoExisten_Modulo //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Modulo`(IN p01_fkModulo int(11))
BEGIN
  SELECT
    usuarios.PKUsuario AS fkUsuario,
    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres
  FROM usuarios
  WHERE NOT EXISTS (SELECT
      *
    FROM usuarios_modulo
    WHERE usuarios_modulo.fkModulo = p01_fkModulo
    AND usuarios.PKUsuario = usuarios_modulo.fkUsuario)
  AND Estado = 1
  ORDER BY Nombres;
END //

DROP PROCEDURE IF EXISTS SDK_FILL_USERS_PER_DEPTO //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SDK_FILL_USERS_PER_DEPTO`(IN deptoPK int)
BEGIN
  SELECT
    u.pkUsuario AS pkUsuario,
    u.usuario AS usuario,
    u.Nombre AS userName,
    CONCAT(u.Nombre, ' ', Apellido) AS fullName
  FROM usuarios u
    INNER JOIN usuarios_modulo um
      ON u.pkUsuario = um.fkUsuario
    INNER JOIN usuarios_subgrupos us
      ON um.fkUsuario = us.fkUsuario
    INNER JOIN sub_groups sg
      ON us.fkSubgrupo = sg.PKsubgrupo
    INNER JOIN grupos g
      ON sg.fkGrupo = g.PKgrupo
  WHERE g.PKgrupo = deptoPK
  AND um.fkModulo = 11
  GROUP BY pkUsuario
  ORDER BY usuario ASC;
END //

DROP PROCEDURE IF EXISTS SDK_GET_ADMIN_IT //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SDK_GET_ADMIN_IT`(IN pkUsuario int(11))
BEGIN
  SELECT
    *
  FROM usuarios_admin_it uai
  WHERE uai.fkUsuario = pkUsuario
  AND uai.fkModulo = 16;
END //

DROP PROCEDURE IF EXISTS SDK_GET_PERFIL //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SDK_GET_PERFIL`(IN pkUsuario int(11))
BEGIN
  SELECT
    *
  FROM usuarios_grupo ug
    INNER JOIN grupos g
      ON ug.fkGrupo = g.PKgrupo
  WHERE ug.fkUsuario = pkUsuario
  AND g.fkModulo = 16
  AND g.PKgrupo IN (166, 167, 168, 169, 171)
  GROUP BY g.fkModulo;
END //

DROP PROCEDURE IF EXISTS SDK_GET_USERS_ON_MODULE //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SDK_GET_USERS_ON_MODULE`()
BEGIN
  SELECT
    u.PKUsuario,
    CONCAT(TRIM(u.Nombre), ' ', TRIM(u.Apellido)) AS fullName,
    u.Usuario AS userName,
    0 AS programado,
    0 AS value0,
    0 AS escala,
    COALESCE(CONCAT(TRIM(u.Nombre), ' ', TRIM(u.Apellido), ' - ', TRIM(g.Nombre)), 'NINGUNO') AS nombreCargo,
    COALESCE(g.Nombre, 'NINGUNO') AS cargoPerfil
  FROM usuarios u
    INNER JOIN usuarios_modulo um
      ON u.PKUsuario = um.fkUsuario
    LEFT JOIN usuarios_grupo ug
      ON um.fkUsuario = ug.fkUsuario
    LEFT JOIN grupos g
      ON ug.fkGrupo = g.PKgrupo
  WHERE um.fkModulo = 16
  AND g.PKgrupo IN (166, 167, 168, 171)
  GROUP BY u.PKUsuario;
END //

DROP PROCEDURE IF EXISTS SDK_LIST_USERS //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SDK_LIST_USERS`()
BEGIN
  SELECT
    u.PKUsuario,
    CONCAT(TRIM(u.Nombre), ' ', TRIM(u.Apellido)) AS fullName,
    u.Usuario AS userName,
    0 AS programado,
    0 AS value0,
    0 AS escala,
    COALESCE(CONCAT(TRIM(u.Nombre), ' ', TRIM(u.Apellido), ' - ', TRIM(g.Nombre)), 'NINGUNO') AS nombreCargo,
    COALESCE(g.Nombre, 'NINGUNO') AS cargoPerfil
  FROM usuarios u
    INNER JOIN usuarios_modulo um
      ON u.PKUsuario = um.fkUsuario
    LEFT JOIN usuarios_grupo ug
      ON um.fkUsuario = ug.fkUsuario
    LEFT JOIN grupos g
      ON ug.fkGrupo = g.PKgrupo
  WHERE um.fkModulo = 16
  AND g.fkModulo = 16
  AND g.PKgrupo IN (166, 167, 168, 171, 182)
  GROUP BY u.PKUsuario;
END //

DROP PROCEDURE IF EXISTS sdk_procedure1 //
CREATE DEFINER=`root`@`localhost` PROCEDURE `sdk_procedure1`(IN varPass varchar(100), IN varUser int)
BEGIN
  UPDATE usuarios u
  SET u.Contrasena = varPass
  WHERE u.PKUsuario = varUser;
END //

DROP PROCEDURE IF EXISTS SEC_GET_ADMIN_IT_X_APP //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SEC_GET_ADMIN_IT_X_APP`(IN pkUsuario int, IN varModulo int)
BEGIN
  SELECT
    *
  FROM usuarios_admin_it uai
  WHERE uai.fkUsuario = pkUsuario
  AND uai.fkModulo = varModulo;
END //

DROP PROCEDURE IF EXISTS SEC_GET_ADMIN_IT_X_MODULO //
CREATE DEFINER=`root`@`localhost` PROCEDURE `SEC_GET_ADMIN_IT_X_MODULO`(IN pkUsuario int)
BEGIN
  SELECT
    *
  FROM usuarios_admin_it uai
  WHERE uai.fkUsuario = pkUsuario
  AND uai.fkModulo = 16;
END //

DROP PROCEDURE IF EXISTS WEB_GET_ADMIN_IT //
CREATE DEFINER=`root`@`localhost` PROCEDURE `WEB_GET_ADMIN_IT`(IN pkUsuario int, IN varModulo int)
BEGIN
  SELECT
    *
  FROM usuarios_admin_it uai
  WHERE uai.fkUsuario = pkUsuario
  AND uai.fkModulo = varModulo;
END //

DELIMITER ;

-- Views
DROP VIEW IF EXISTS view_acciones_usuario;
CREATE DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `view_acciones_usuario` AS select `acciones`.`PKaccion` AS `PKaccion`,`acciones`.`fkModulo` AS `fkModulo`,`acciones`.`Nombre` AS `NombreAccion`,`acciones`.`Descripcion` AS `Descripcion`,`acciones_usuario`.`PKpermisoUsuario` AS `PKpermisoUsuario`,`acciones_usuario`.`fkUsuario` AS `fkUsuario`,`acciones_usuario`.`fkAccion` AS `fkAccion`,`acciones_usuario`.`Permiso` AS `Permiso`,`acciones_usuario`.`Ver` AS `Ver`,`acciones_usuario`.`SoloLectura` AS `SoloLectura`,`acciones_usuario`.`VerTodas` AS `VerTodas`,`acciones_usuario`.`Crear` AS `Crear`,`acciones_usuario`.`Editar` AS `Editar`,`acciones_usuario`.`Borrar` AS `Borrar`,`acciones_usuario`.`Suspender` AS `Suspender`,`acciones_usuario`.`Anular` AS `Anular`,`acciones_usuario`.`Imprimir` AS `Imprimir`,`acciones_usuario`.`Eliminar` AS `Eliminar`,`acciones_usuario`.`Bloquear` AS `Bloquear`,`acciones_usuario`.`PE1` AS `PE1`,`acciones_usuario`.`PE2` AS `PE2`,`acciones_usuario`.`PE3` AS `PE3`,`acciones_usuario`.`PE4` AS `PE4`,`acciones_usuario`.`PE5` AS `PE5`,`acciones_usuario`.`Creado` AS `Creado`,`acciones_usuario`.`Editado` AS `Editado`,`acciones_usuario`.`UsuarioEdito` AS `UsuarioEdito`,`acciones_usuario`.`UsuarioCreo` AS `UsuarioCreo` from (`acciones` join `acciones_usuario` on((`acciones`.`PKaccion` = `acciones_usuario`.`fkAccion`)));

DROP VIEW IF EXISTS view_paginas_menus;
CREATE DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `view_paginas_menus` AS select `menus`.`Pagina` AS `Pagina`,`menus`.`Nombre` AS `Nombre`,`menus`.`TipoMenu` AS `TipoMenu` from `menus` where (`menus`.`TipoMenu` = 1) order by `menus`.`Pagina`;

DROP VIEW IF EXISTS view_usuarios_grupo;
CREATE DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `view_usuarios_grupo` AS select `usuarios`.`PKUsuario` AS `PKUsuario`,concat(`usuarios`.`Nombre`,' ',`usuarios`.`Apellido`) AS `Nombres`,`usuarios`.`Usuario` AS `Usuario`,`grupos`.`Nombre` AS `Grupo`,`usuarios_grupo`.`fkGrupo` AS `fkGrupo` from ((`usuarios` join `usuarios_grupo` on((`usuarios`.`PKUsuario` = `usuarios_grupo`.`fkUsuario`))) join `grupos` on((`grupos`.`PKgrupo` = `usuarios_grupo`.`fkGrupo`)));
