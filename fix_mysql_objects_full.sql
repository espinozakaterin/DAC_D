-- Full script to fix ALL 'bart100' definers in global_security
-- Replaced with 'root'@'localhost' as requested

DELIMITER //

DROP PROCEDURE IF EXISTS `CRM_GET_ADMIN_IT` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CRM_GET_ADMIN_IT`(IN pkUsuario int(11))
BEGIN

  SELECT

    *

  FROM usuarios_admin_it uai

  WHERE uai.fkUsuario = pkUsuario

  AND uai.fkModulo = 13;

END //

DROP PROCEDURE IF EXISTS `CRM_GET_PERFIL` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CRM_GET_PERFIL`(IN pkUsuario int(11))
BEGIN

  SELECT

    *

  FROM usuarios_grupo ug

    INNER JOIN grupos g

      ON ug.fkGrupo = g.PKgrupo

  WHERE ug.fkUsuario = pkUsuario

  AND g.fkModulo = 13

  GROUP BY g.fkModulo;

END //

DROP PROCEDURE IF EXISTS `DAC_GRUPOS_X_USER` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `DAC_GRUPOS_X_USER`(IN userID int)
BEGIN



  SELECT

    ug.PKnuevo,

    g.Nombre

  FROM usuarios_grupo ug

    INNER JOIN grupos g

      ON ug.fkGrupo = g.PKgrupo

  WHERE g.fkModulo = 11

  AND ug.fkUsuario = userID;



END //

DROP PROCEDURE IF EXISTS `EVA_FILL_USERS_PER_DEPTO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_FILL_USERS_PER_DEPTO`(IN deptoPK int)
BEGIN

  SELECT

    u.pkUsuario AS pkUsuario,

    u.usuario AS usuario,

    u.Nombre AS userName

  FROM usuarios u

    INNER JOIN usuarios_modulo um

      ON u.pkUsuario = um.fkUsuario

    INNER JOIN usuarios_subgrupos us

      ON um.fkUsuario = us.fkUsuario

    INNER JOIN sub_grupos sg

      ON us.fkSubgrupo = sg.PKsubgrupo

    INNER JOIN grupos g

      ON sg.fkGrupo = g.PKgrupo

  WHERE g.PKgrupo = deptoPK

  AND um.fkModulo = 11

  GROUP BY pkUsuario

  ORDER BY usuario ASC;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_ADMIN_IT` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_ADMIN_IT`(IN pkUsuario int(11))
BEGIN

  SELECT

    *

  FROM usuarios_admin_it uai

  WHERE uai.fkUsuario = pkUsuario

  AND uai.fkModulo = 11;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_ALL_USERS` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_ALL_USERS`()
BEGIN



  SELECT

    *

  FROM usuarios u;



END //

DROP PROCEDURE IF EXISTS `EVA_GET_GROUP_OF_SUBGROUP` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_GROUP_OF_SUBGROUP`(IN fkSubGrupo int(11))
BEGIN

  SELECT

    *

  FROM grupos g

    INNER JOIN sub_grupos sg

      ON g.PKgrupo = sg.FKgrupo

  WHERE sg.PKsubgrupo = fkSubGrupo

  GROUP BY sg.PKsubgrupo;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_SUBGRUPOS_X_USUARIO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_SUBGRUPOS_X_USUARIO`(IN varUser int)
BEGIN



  SELECT

    us.PKnuevo,

    sg.sub_grupo

  FROM usuarios_subgrupos us

    INNER JOIN sub_grupos sg

      ON us.fkSubgrupo = sg.PKsubgrupo

  WHERE us.fkUsuario = varUser;



END //

DROP PROCEDURE IF EXISTS `EVA_GET_SUPERV_USERS_DEPTO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_SUPERV_USERS_DEPTO`(IN pkUser int(11))
BEGIN

  SELECT

    *

  FROM usuarios u

    INNER JOIN usuarios_grupo ug

      ON u.PKUsuario = ug.fkUsuario

    INNER JOIN grupos g

      ON ug.fkGrupo = g.PKgrupo

  WHERE u.PKUsuario = pkUser

  AND ug.fkGrupo NOT IN (SELECT

      ug1.fkGrupo

    FROM usuarios_grupo ug1

    WHERE ug1.fkGrupo IN (79, 82, 121, 151))

  AND g.fkModulo = 11;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_USERS_ACCESS` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_USERS_ACCESS`()
BEGIN

  SELECT

    *

  FROM grupos g

  WHERE g.PKgrupo IN (79, 82, 121, 151);

END //

DROP PROCEDURE IF EXISTS `EVA_GET_USERS_NOT_IN_DEPTO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_USERS_NOT_IN_DEPTO`(IN varDepto int(11))
BEGIN

  SELECT

    u.PKUsuario AS pkUsuario,

    u.Nombre AS userName

  FROM usuarios u

    INNER JOIN usuarios_modulo um

      ON u.PKUsuario = um.fkUsuario

    INNER JOIN usuarios_grupo ug

      ON u.PKUsuario = ug.fkUsuario

  WHERE u.PKUsuario NOT IN (SELECT

      ug.fkUsuario

    FROM usuarios_grupo ug

    WHERE ug.fkGrupo = varDepto)

  AND ug.fkGrupo = 151

  AND um.fkModulo = 11;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_USERS_ON_MODULE` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_USERS_ON_MODULE`(IN varGroup int(11))
BEGIN

  SELECT

    *

  FROM usuarios u

    INNER JOIN usuarios_modulo um

      ON u.PKUsuario = um.fkUsuario

  WHERE um.fkModulo = 11

  AND u.PKUsuario NOT IN (SELECT

      ug1.fkUsuario

    FROM usuarios_grupo ug1

    WHERE ug1.fkGrupo IN (79, 82, 121))
  GROUP BY u.PKUsuario;

END //

DROP PROCEDURE IF EXISTS `EVA_GET_USERS_X_DEPTO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_GET_USERS_X_DEPTO`(IN pkGrupo int)
BEGIN

  SELECT

    u.PKUsuario AS pkUsuario,

    u.Nombre AS userName

  FROM usuarios u

    INNER JOIN usuarios_modulo um

      ON u.PKUsuario = um.fkUsuario

    INNER JOIN usuarios_grupo ug

      ON u.PKUsuario = ug.fkUsuario

    INNER JOIN grupos g

      ON ug.fkGrupo = g.PKgrupo

  WHERE g.PKgrupo = pkGrupo

  #AND um.fkModulo = 11

  ;

END //

DROP PROCEDURE IF EXISTS `EVA_INSERT_USER_TO_GROUP` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_INSERT_USER_TO_GROUP`(IN pkUser int(11), IN pkDepto int(11))
BEGIN

  INSERT INTO usuarios_grupo (fkGrupo, fkUsuario)

    VALUES (pkDepto, pkUser);

END //

DROP PROCEDURE IF EXISTS `EVA_INSERT_USER_TO_TYPE` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_INSERT_USER_TO_TYPE`(IN pkGroup int(11), IN pkUsuario int(11))
BEGIN

  INSERT INTO usuarios_grupo (fkGrupo, fkUsuario)

    VALUES (pkGroup, pkUsuario);

END //

DROP PROCEDURE IF EXISTS `EVA_NOTIFICATION_GET_TESTERS` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_NOTIFICATION_GET_TESTERS`()
BEGIN

  SELECT

    *

  FROM eva_evaluaciones e

    INNER JOIN eva_configuracion_evaluaciones ce

      ON e.id_periodo = ce.id_periodo

    INNER JOIN usuarios_subgrupos us

      ON e.id_area = us.fkSubgrupo

    INNER JOIN usuarios u

      ON us.fkUsuario = u.PKUsuario

  WHERE ce.fecha_inicio = CURRENT_DATE()

  AND us.tipo_usuario = 2

  GROUP BY u.PKUsuario;

END //

DROP PROCEDURE IF EXISTS `EVA_REMOVE_USER_TO_TYPE` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_REMOVE_USER_TO_TYPE`(IN pkGroup int(11), IN pkUsuario int(11))
BEGIN

  DELETE

    FROM usuarios_grupo

  WHERE fkGrupo = pkGroup

    AND fkUsuario = pkUsuario;

END //

DROP PROCEDURE IF EXISTS `EVA_REMOVE_USER_X_DEPTO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_REMOVE_USER_X_DEPTO`(IN pkUser int(11), IN pkDepto int(11))
BEGIN

  DELETE

    FROM usuarios_grupo

  WHERE fkGrupo = pkDepto

    AND fkUsuario = pkUser;

END //

DROP PROCEDURE IF EXISTS `EVA_STATUS_TEST` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `EVA_STATUS_TEST`(IN test_status_value varchar(10), IN idEvaluacion int(11), IN modificado_por varchar(50), IN fecha_hora_modificado datetime)
BEGIN

  UPDATE eva_evaluaciones

  SET estado = test_status_value,

      modificado_por = modificado_por,

      fecha_hora_modificado = fecha_hora_modificado

  WHERE id_evaluacion = idEvaluacion;

END //

DROP PROCEDURE IF EXISTS `GS_LIST_MENUS_X_MODULO` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `GS_LIST_MENUS_X_MODULO`(IN varM int)
BEGIN



  SELECT

    m.Posicion,

    TRIM(m.Nombre) AS Menu

  FROM menus m

  WHERE m.fkModulo = varM

  ORDER BY m.Nombre ASC;



END //

DROP PROCEDURE IF EXISTS `GS_LIST_MODULOS` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `GS_LIST_MODULOS`()
BEGIN



  SELECT
    m.*
  FROM modulos m
  ORDER BY m.Nombre ASC;



END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Accion_Grupos_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Accion_Grupos_Usuario`(IN p01_fkAccion int(11), IN p02_fkUsuario int(11))
BEGIN



  SELECT

    acciones_grupo.fkAccion

  FROM usuarios_grupo

    INNER JOIN acciones_grupo

      ON usuarios_grupo.fkGrupo = acciones_grupo.fkGrupo

  WHERE usuarios_grupo.fkUsuario = p02_fkUsuario

  AND acciones_grupo.fkAccion = p01_fkAccion;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Accion_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Accion_Usuario`(IN p01_fkAccion int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    acciones_usuario.Permiso

  FROM acciones_usuario

  WHERE acciones_usuario.fkUsuario = p02_fkUsuario

  AND acciones_usuario.fkAccion = p01_fkAccion;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_FechaHora_Actual` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_FechaHora_Actual`()
BEGIN

  SELECT

    CURRENT_TIMESTAMP;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Fecha_Actual` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Fecha_Actual`()
BEGIN

  SELECT

    CURRENT_DATE

  ;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Nombre_Telefono_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Nombre_Telefono_Usuario`(IN p01_Usuario varchar(20))
BEGIN



  SELECT

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido, ' ', COALESCE(Telefono, "")) AS Telefono

  FROM usuarios

  WHERE Usuario = p01_Usuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Nombre_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Nombre_Usuario`(IN p01_Usuario varchar(20))
BEGIN



  SELECT

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido)



  FROM usuarios



  WHERE usuarios.Usuario = p01_Usuario;







END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Telefono_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Telefono_Usuario`(IN p01_Usuario varchar(20))
BEGIN



  SELECT

    COALESCE(Telefono, "") AS Telefono

  FROM usuarios

  WHERE Usuario = p01_Usuario;



END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Usuario_Admin` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Usuario_Admin`(IN p01_fkModulo int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    fkUsuario

  FROM usuarios_admin

  WHERE fkModulo = p01_fkModulo

  AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Usuario_Admin_it` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Usuario_Admin_it`(IN p01_fkModulo int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    fkUsuario

  FROM usuarios_admin_it

  WHERE fkModulo = p01_fkModulo

  AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Usuario_b` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Usuario_b`(IN p01_Usuario varchar(20))
BEGIN



  SELECT

    PKUsuario,

    Nombre,

    Apellido,

    CONCAT(nombre, " ", Apellido) NombreCompleto,

    Usuario,

    Descuento,

    Telefono,

    FkPuesto,

    Estado AS EstadoFK,

    CASE Estado WHEN 1 THEN 'VIGENTE' ELSE 'RETIRADO' END AS Estado



  FROM usuarios

  WHERE Usuario = p01_Usuario;







END //

DROP PROCEDURE IF EXISTS `mySP_Dar_Usuario_Modulo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dar_Usuario_Modulo`(IN p01_fkModulo int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    fkUsuario

  FROM usuarios_modulo

  WHERE fkModulo = p01_fkModulo

  AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Acciones_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Acciones_Grupo`(IN p01_fkGrupo int(11), IN p02_fkAccion integer(11))
BEGIN

  DELETE

    FROM acciones_grupo

  WHERE fkGrupo = p01_fkGrupo

    AND fkAccion = p02_fkAccion;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Acciones_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Acciones_Usuario`(IN p01_fkUsuario int(11), IN p02_fkAccion integer(11))
BEGIN

  DELETE

    FROM acciones_Usuario

  WHERE fkUsuario = p01_fkUsuario

    AND fkAccion = p02_fkAccion;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Menus_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Menus_Grupo`(IN p01_fkGrupo int(11), IN p02_fkMenu integer(11))
BEGIN

  DELETE

    FROM menus_grupo

  WHERE fkGrupo = p01_fkGrupo

    AND fkMenu = p02_fkMenu;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Menus_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Menus_Usuario`(IN p01_fkUsuario int(11), IN p02_fkMenu integer(11))
BEGIN

  DELETE

    FROM menus_usuario

  WHERE fkUsuario = p01_fkUsuario

    AND fkMenu = p02_fkMenu;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Todo_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Todo_Usuario`(IN p01_fkUsuario int(11))
BEGIN

  DELETE

    FROM menus_usuario

  WHERE fkUsuario = p01_fkUsuario;



  DELETE

    FROM usuarios_grupo

  WHERE fkUsuario = p01_fkUsuario;



  DELETE

    FROM usuarios_admin

  WHERE fkUsuario = p01_fkUsuario;



  DELETE

    FROM usuarios_admin_it

  WHERE fkUsuario = p01_fkUsuario;



  DELETE

    FROM usuarios_modulo

  WHERE fkUsuario = p01_fkUsuario;





END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Usuarios_Admin` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Usuarios_Admin`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  DELETE

    FROM usuarios_Admin

  WHERE fkModulo = p01_fkModulo

    AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Usuarios_Admin_it` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Usuarios_Admin_it`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  DELETE

    FROM usuarios_admin_it

  WHERE fkModulo = p01_fkModulo

    AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Usuarios_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Usuarios_Grupo`(IN p01_fkGrupo int(11), IN p02_fkUsuario integer(11))
BEGIN

  DELETE

    FROM usuarios_grupo

  WHERE fkGrupo = p01_fkGrupo

    AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Delete_Usuarios_Modulo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Delete_Usuarios_Modulo`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  DELETE

    FROM usuarios_Modulo

  WHERE fkModulo = p01_fkModulo

    AND fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Dispositivos_Autorizados` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Dispositivos_Autorizados`(IN pMacAddress nvarchar(100), IN pPIN nvarchar(100))
BEGIN

  SELECT

    *

  FROM movil_user mu

  WHERE mu.Dispositivo = pMacAddress

  AND mu.Pin = pPIN;

END //

DROP PROCEDURE IF EXISTS `mySP_Duplicar_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Duplicar_Usuario`(IN p01_Origen int(11), IN p02_Destino integer(11))
BEGIN





  DELETE

    FROM acciones_usuario

  WHERE fkUsuario = p02_Destino;

  DELETE

    FROM menus_usuario

  WHERE fkUsuario = p02_Destino;

  DELETE

    FROM usuarios_grupo

  WHERE fkUsuario = p02_Destino;



  -- meter las acciones del usuario

  INSERT INTO acciones_usuario (fkUsuario

  , fkAccion

  , Permiso)



    SELECT

      p02_Destino,

      fkAccion,

      Permiso

    FROM acciones_usuario

    WHERE fkUsuario = p01_Origen;



  -- meter los menus del usuario

  INSERT INTO menus_usuario (fkUsuario

  , fkMenu

  , Permiso)



    SELECT

      p02_Destino,

      fkMenu,

      Permiso

    FROM menus_usuario

    WHERE fkUsuario = p01_Origen;



  -- meter los grupos del usuario

  INSERT INTO usuarios_grupo (fkGrupo

  , fkUsuario)



    SELECT

      fkGrupo,

      p02_Destino

    FROM usuarios_grupo

    WHERE fkUsuario = p01_Origen;



END //

DROP PROCEDURE IF EXISTS `mySP_Fill_accion_usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_accion_usuario`(IN p01_fkAccion int, p02_fkUsuario int)
BEGIN



  SELECT

    PKaccion,

    fkModulo,

    NombreAccion,

    Descripcion,

    PKpermisoUsuario,

    fkUsuario,

    fkAccion,

    Permiso,

    Ver,

    VerTodas,

    SoloLectura,

    Crear,

    Editar,

    Borrar,

    Suspender,

    Anular,

    Imprimir,

    Eliminar,

    Bloquear,

    PE1,

    PE2,

    PE3,

    PE4,

    PE5,

    Creado,

    Editado,

    UsuarioEdito,

    UsuarioCreo

  FROM view_acciones_usuario

  WHERE fkAccion = p01_fkAccion

  AND fkUsuario = p02_fkUsuario;



END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Menus_GruposUsuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Menus_GruposUsuario`(IN p01_fkModulo int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    menus.Posicion

  FROM usuarios_grupo

    INNER JOIN menus_grupo

      ON usuarios_grupo.fkGrupo = menus_grupo.fkGrupo

    INNER JOIN menus

      ON menus.PKMenu = menus_grupo.fkMenu

  WHERE usuarios_grupo.fkUsuario = p02_fkUsuario

  AND menus.fkModulo = p01_fkModulo

  GROUP BY menus.Posicion,

           menus.Nombre;

END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Menus_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Menus_Usuario`(IN p01_fkModulo int(11), IN p02_fkUsuario int(11))
BEGIN

  SELECT

    menus.Posicion,

    menus_usuario.Permiso

  FROM menus

    INNER JOIN menus_usuario

      ON menus.PKMenu = menus_usuario.fkMenu

  WHERE menus.fkModulo = p01_fkModulo

  AND menus_usuario.fkUsuario = p02_fkUsuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Todos_Usuarios` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Todos_Usuarios`(IN Listar int)
BEGIN



  IF Listar = 1 THEN

  BEGIN



    SELECT

      usuarios.PKUsuario AS PKUsuario,

      usuarios.Usuario,

      CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombre,

      usuarios.Descuento,

      COALESCE(usuarios.Telefono, "") AS Telefono,

      usuarios.PKUsuario AS PK,

      (CASE usuarios.Estado WHEN 1 THEN 'HABILITADO' WHEN 2 THEN 'RETIRADO' WHEN 3 THEN 'BLOQUEADO' ELSE 'INDEFINIDO' END) AS Estado,

      IsBuiltIn,

      PassRequerido,

      Estado AS fkEstado,

      FkPuesto

    FROM usuarios

    WHERE usuarios.Estado = 1

    AND IsBuiltIn = 0

    ORDER BY usuarios.Usuario;

  END;



  ELSEIF Listar = 2 THEN

  BEGIN



    SELECT

      usuarios.PKUsuario AS PKUsuario,

      usuarios.Usuario,

      CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombre,

      usuarios.Descuento,

      COALESCE(usuarios.Telefono, "") AS Telefono,

      usuarios.PKUsuario AS PK,

      (CASE usuarios.Estado WHEN 1 THEN 'HABILITADO' WHEN 2 THEN 'RETIRADO' WHEN 3 THEN 'BLOQUEADO' ELSE 'INDEFINIDO' END) AS Estado,

      IsBuiltIn,

      PassRequerido,

      Estado AS fkEstado



    FROM usuarios

    WHERE usuarios.Estado = 2

    ORDER BY usuarios.Usuario;

  END;



  ELSE

  BEGIN



    SELECT

      usuarios.PKUsuario AS PKUsuario,

      usuarios.Usuario,

      CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombre,

      usuarios.Descuento,

      COALESCE(usuarios.Telefono, "") AS Telefono,

      usuarios.PKUsuario AS PK,

      (CASE usuarios.Estado WHEN 1 THEN 'HABILITADO' WHEN 2 THEN 'RETIRADO' WHEN 3 THEN 'BLOQUEADO' ELSE 'INDEFINIDO' END) AS Estado,

      IsBuiltIn,

      PassRequerido,

      Estado AS fkEstado



    FROM usuarios





    ORDER BY usuarios.Usuario;

  END;

  END IF;



END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Usuarios_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Usuarios_Grupo`(IN p01_Grupo varchar(50))
BEGIN

  SELECT

    usuarios.PKUsuario AS PK,

    usuarios.PKUsuario,

    usuarios.Usuario,

    CONCAT(usuarios.Nombre, " ", usuarios.Apellido) AS Nombre,

    Descuento,

    COALESCE(Telefono, "") AS Telefono,

    (CASE usuarios.Estado WHEN 1 THEN 'HABILITADO' WHEN 2 THEN 'RETIRADO' WHEN 3 THEN 'BLOQUEADO' ELSE 'INDEFINIDO' END) AS Estado



  FROM usuarios

    INNER JOIN usuarios_grupo

      ON usuarios.PKUsuario = usuarios_grupo.fkUsuario

    INNER JOIN grupos

      ON grupos.PKgrupo = usuarios_grupo.fkGrupo

  WHERE grupos.Nombre = p01_Grupo

  AND usuarios.Estado = 1

  ORDER BY usuarios.Nombre;



END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Validar_Autorizacion` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Validar_Autorizacion`(IN p01_Usuario varchar(20), IN p02_Clave varchar(20), IN p03_Tipo varchar(40))
BEGIN

  SELECT

    *

  FROM usuarios_autorizaciones ua

  WHERE ua.Usuario = p01_Usuario

  AND ua.Clave = p02_Clave

  AND ua.Tipo = p03_Tipo

  AND ua.Vigente = 1;

END //

DROP PROCEDURE IF EXISTS `mySP_Fill_Vendedores` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Fill_Vendedores`()
BEGIN

  SELECT

    PKUsuario AS PKusuario,

    Usuario,

    CONCAT(Nombre, ' ', Apellido) AS Nombre,

    Descuento,

    Telefono

  FROM usuarios

  WHERE Ventas = 1

  AND Estado = 1

  ORDER BY Usuario;

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Acciones_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Acciones_Grupo`(IN p01_fkGrupo int(11), IN p02_fkAccion integer(11))
BEGIN

  INSERT INTO Acciones_grupo (fkGrupo, fkAccion)

    VALUES (p01_fkGrupo, p02_fkAccion);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Acciones_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Acciones_Usuario`(IN p01_fkUsuario int(11), IN p02_fkAccion integer(11), IN p03_Permiso integer(1))
BEGIN

  INSERT INTO Acciones_Usuario (fkUsuario,

  fkAccion,

  Permiso)

    VALUES (p01_fkUsuario, p02_fkAccion, p03_Permiso);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_AuditLog` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_AuditLog`(IN p01_Accion varchar(40),

IN p02_Modulo integer,

IN p03_Descripcion char(255),

IN p04_Usuario char(20),

IN p05_LaTabla varchar(40))
BEGIN



  INSERT INTO auditlog (Accion

  , Modulo

  , Descripcion

  , Usuario

  , Tabla)

    VALUES (p01_Accion, p02_Modulo, p03_Descripcion, p04_Usuario, p05_LaTabla);



END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Menus_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Menus_Grupo`(IN p01_fkGrupo int(11), IN p02_fkMenu integer(11))
BEGIN

  INSERT INTO Menus_grupo (fkGrupo,

  fkMenu)

    VALUES (p01_fkGrupo, p02_fkMenu);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Menus_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Menus_Usuario`(IN p01_fkUsuario int(11), IN p02_fkMenu integer(11), IN p03_Permiso integer(1))
BEGIN

  INSERT INTO Menus_Usuario (fkUsuario,

  fkMenu,

  Permiso)

    VALUES (p01_fkUsuario, p02_fkMenu, p03_Permiso);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Usuarios_Admin` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Usuarios_Admin`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  INSERT INTO usuarios_Admin (fkModulo,

  fkUsuario)

    VALUES (p01_fkModulo, p02_fkUsuario);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Usuarios_Admin_it` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Usuarios_Admin_it`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  INSERT INTO usuarios_admin_it (fkModulo,

  fkUsuario)

    VALUES (p01_fkModulo, p02_fkUsuario);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Usuarios_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Usuarios_Grupo`(IN p01_fkGrupo int(11), IN p02_fkUsuario integer(11))
BEGIN

  INSERT INTO usuarios_grupo (fkGrupo,

  fkUsuario)

    VALUES (p01_fkGrupo, p02_fkUsuario);

END //

DROP PROCEDURE IF EXISTS `mySP_Insert_Usuarios_Modulo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Insert_Usuarios_Modulo`(IN p01_fkModulo int(11), IN p02_fkUsuario integer(11))
BEGIN

  INSERT INTO usuarios_Modulo (fkModulo,

  fkUsuario)

    VALUES (p01_fkModulo, p02_fkUsuario);

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Acciones_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Acciones_Grupo`(IN p01_fkGrupo int(11), IN p02_fkModulo int(11))
BEGIN

  SELECT

    Acciones_grupo.fkAccion,

    Acciones.Nombre AS Nombres,

    Acciones.Descripcion

  FROM Acciones

    INNER JOIN Acciones_grupo

      ON Acciones.PKaccion = Acciones_grupo.fkAccion

  WHERE Acciones_grupo.fkGrupo = p01_fkGrupo

  AND fkModulo = p02_fkModulo

  ORDER BY Acciones.Nombre;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Acciones_NoExisten_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Acciones_NoExisten_Grupo`(IN p01_fkGrupo int(11), IN p02_fkModulo integer(11))
BEGIN



  SELECT

    Acciones.PKAccion AS fkAccion,

    Acciones.Nombre AS Nombres,

    Acciones.Descripcion

  FROM Acciones

  WHERE fkModulo = p02_fkModulo

  AND NOT EXISTS (SELECT

      *

    FROM Acciones_grupo

    WHERE Acciones_grupo.fkGrupo = p01_fkGrupo

    AND Acciones.PKAccion = Acciones_grupo.fkAccion)
  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Acciones_NoExisten_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Acciones_NoExisten_Usuario`(IN p01_fkUsuario int(11), IN p02_fkModulo integer(11))
BEGIN



  SELECT

    Acciones.PKAccion AS fkAccion,

    Acciones.Nombre AS Nombres,

    0 AS Permiso

  FROM Acciones

  WHERE fkModulo = p02_fkModulo

  AND NOT EXISTS (SELECT

      *

    FROM Acciones_Usuario

    WHERE Acciones_Usuario.fkUsuario = p01_fkUsuario

    AND Acciones.PKAccion = Acciones_Usuario.fkAccion)
  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Acciones_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Acciones_Usuario`(IN p01_fkUsuario int(11), IN p02_fkModulo int(11))
BEGIN

  SELECT

    acciones_usuario.fkAccion,

    acciones.Nombre AS Nombres,

    acciones_usuario.Permiso

  FROM acciones

    INNER JOIN acciones_usuario

      ON acciones.PKaccion = acciones_usuario.fkAccion

    INNER JOIN usuarios u

      ON u.PKUsuario = acciones_usuario.fkUsuario

  WHERE acciones_usuario.fkUsuario = p01_fkUsuario

  AND fkModulo = p02_fkModulo

  AND u.Estado = 1

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_Menu` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_Menu`(IN p01_fkMenu int(11))
BEGIN

  SELECT

    menus_grupo.fkGrupo,

    CONCAT(grupos.Nombre) AS Nombres

  FROM Grupos

    INNER JOIN menus_grupo

      ON Grupos.PKGrupo = menus_Grupo.fkGrupo

  WHERE menus_grupo.fkMenu = p01_fkMenu

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_NoExisten_Menu` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_NoExisten_Menu`(IN p01_fkMenu int(11))
BEGIN

  SELECT

    Grupos.PKGrupo AS fkGrupo,

    CONCAT(Grupos.Nombre) AS Nombres

  FROM Grupos

  WHERE NOT EXISTS (SELECT

      *

    FROM menus_grupo

    WHERE menus_grupo.fkMenu = p01_fkMenu

    AND Grupos.PKGrupo = menus_grupo.fkGrupo)
  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_NoExisten_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_NoExisten_Usuario`(IN p01_fkUsuario int(11), p02_fkModulo integer)
BEGIN



  SELECT

    grupos.PKgrupo AS fkgrupo,

    grupos.Nombre AS Nombres,

    grupos.Descripcion,

    grupos.fkModulo

  FROM grupos

  WHERE NOT EXISTS (SELECT

      *

    FROM usuarios_grupo

    WHERE usuarios_grupo.fkUsuario = p01_fkUsuario

    AND grupos.PKgrupo = usuarios_grupo.fkgrupo)

  AND grupos.fkModulo = p02_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_NoExisten_Usuario_gs` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_NoExisten_Usuario_gs`(IN p01_fkUsuario int(11), p02_fkModulo integer)
BEGIN



  SELECT

    grupos.PKgrupo AS fkgrupo,

    grupos.Nombre AS Nombres,

    grupos.Descripcion,

    grupos.fkModulo

  FROM grupos

  WHERE NOT EXISTS (SELECT

      *

    FROM usuarios_grupo

    WHERE usuarios_grupo.fkUsuario = p01_fkUsuario

    AND grupos.PKgrupo = usuarios_grupo.fkgrupo)

  AND grupos.fkModulo = p02_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_Usuario`(IN p01_fkUsuario int(11), p02_fkModulo integer)
BEGIN

  SELECT

    usuarios_grupo.fkgrupo,

    grupos.Nombre AS Nombres,

    grupos.Descripcion

  FROM grupos

    INNER JOIN usuarios_grupo

      ON grupos.PKgrupo = usuarios_grupo.fkgrupo

    INNER JOIN usuarios u

      ON fkUsuario = u.PKUsuario

  WHERE usuarios_grupo.fkUsuario = p01_fkUsuario

  AND u.Estado = 1

  AND grupos.fkModulo = p02_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Grupos_Usuario_gs` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Grupos_Usuario_gs`(IN p01_fkUsuario int(11), IN p02_fkModulo integer)
BEGIN

  SELECT

    usuarios_grupo.fkgrupo,

    grupos.Nombre AS Nombres,

    grupos.Descripcion

  FROM grupos

    INNER JOIN usuarios_grupo

      ON grupos.PKgrupo = usuarios_grupo.fkgrupo

    INNER JOIN usuarios u

      ON fkUsuario = u.PKUsuario

  WHERE usuarios_grupo.fkUsuario = p01_fkUsuario

  AND u.Estado = 1

  AND grupos.fkModulo = p02_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Menus_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Menus_Grupo`(IN p01_fkGrupo int(11), IN p02_fkModulo int(11))
BEGIN

  SELECT

    menus_grupo.fkMenu,

    menus.Nombre AS Nombres,

    menus.Posicion

  FROM menus

    INNER JOIN menus_grupo

      ON menus.PKMenu = menus_grupo.fkMenu

  WHERE menus_grupo.fkGrupo = p01_fkGrupo

  AND fkModulo = p02_fkModulo

  ORDER BY menus.NoOrden;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Menus_NoExisten_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Menus_NoExisten_Grupo`(IN p01_fkGrupo int(11), IN p02_fkModulo integer(11))
BEGIN



  SELECT

    menus.PKmenu AS fkMenu,

    menus.Nombre AS Nombres,

    menus.Posicion

  FROM menus

  WHERE fkModulo = p02_fkModulo

  AND NOT EXISTS (SELECT

      *

    FROM menus_grupo

    WHERE menus_grupo.fkGrupo = p01_fkGrupo

    AND menus.PKmenu = menus_grupo.fkMenu)
  ORDER BY NoOrden;



END //

DROP PROCEDURE IF EXISTS `mySP_Select_Menus_NoExisten_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Menus_NoExisten_Usuario`(IN p01_fkUsuario int(11), IN p02_fkModulo integer(11))
BEGIN



  SELECT

    menus.PKmenu AS fkMenu,

    menus.Nombre AS Nombres,

    menus.Posicion,

    0 AS Permiso

  FROM menus

  WHERE fkModulo = p02_fkModulo

  AND NOT EXISTS (SELECT

      *

    FROM menus_Usuario

    WHERE menus_Usuario.fkUsuario = p01_fkUsuario

    AND menus.PKmenu = menus_Usuario.fkMenu)
  ORDER BY NoOrden;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Menus_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Menus_Usuario`(IN p01_fkUsuario int(11), IN p02_fkModulo int(11))
BEGIN

  SELECT

    menus_Usuario.fkMenu,

    menus.Nombre AS Nombres,

    menus.Posicion,

    menus_Usuario.Permiso

  FROM menus

    INNER JOIN menus_Usuario

      ON menus.PKMenu = menus_Usuario.fkMenu

  WHERE menus_Usuario.fkUsuario = p01_fkUsuario

  AND fkModulo = p02_fkModulo

  ORDER BY menus.NoOrden;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Modulos_NoExisten_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Modulos_NoExisten_Usuario`(IN p01_fkUsuario int(11))
BEGIN



  SELECT

    Modulos.PKModulo AS fkModulo,

    Modulos.Nombre AS Nombres,

    Modulos.Descripcion

  FROM Modulos

  WHERE NOT EXISTS (SELECT

      *

    FROM usuarios_Modulo

    WHERE usuarios_Modulo.fkUsuario = p01_fkUsuario

    AND Modulos.PKModulo = usuarios_Modulo.fkModulo)
  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Modulos_Usuario` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Modulos_Usuario`(IN p01_fkUsuario int(11))
BEGIN

  SELECT

    usuarios_modulo.fkModulo,

    modulos.Nombre AS Nombres,

    modulos.Descripcion

  FROM modulos

    INNER JOIN usuarios_modulo

      ON modulos.PKModulo = usuarios_modulo.fkModulo

  WHERE usuarios_modulo.fkUsuario = p01_fkUsuario

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Admin` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Admin`(IN p01_fkModulo int(11))
BEGIN

  SELECT

    usuarios_Admin.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN usuarios_admin

      ON usuarios.PKUsuario = usuarios_admin.fkUsuario

  WHERE usuarios_admin.fkModulo = p01_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Admin_it` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Admin_it`(IN p01_fkModulo int(11))
BEGIN

  SELECT

    usuarios_admin_it.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN usuarios_admin_it

      ON usuarios.PKUsuario = usuarios_admin_it.fkUsuario

  WHERE usuarios_admin_it.fkModulo = p01_fkModulo

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Departamento` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Departamento`(IN p01_fkDepto int(11))
BEGIN

  SELECT

    uk.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    usuarios.Usuario

  FROM usuarios

    INNER JOIN usuarios_departamento uk

      ON uk.fkUsuario = PKUsuario

  WHERE uk.fkDepto = p01_fkDepto

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Grupo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Grupo`(IN p01_fkGrupo int(11))
BEGIN

  SELECT

    usuarios_grupo.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN usuarios_grupo

      ON usuarios.PKUsuario = usuarios_grupo.fkUsuario

  WHERE usuarios_grupo.fkGrupo = p01_fkGrupo

  AND Estado = 1

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Kimberly` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Kimberly`(IN p01_fkVendedor int(11))
BEGIN

  SELECT

    uk.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN usuarios_kimberly uk

      ON uk.fkUsuario = PKUsuario

  WHERE uk.fkVendedor = p01_fkVendedor

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Menu` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Menu`(IN p01_fkMenu int(11))
BEGIN

  SELECT

    menus_usuario.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN menus_usuario

      ON usuarios.PKUsuario = menus_usuario.fkUsuario

  WHERE menus_usuario.fkMenu = p01_fkMenu

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_Modulo` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_Modulo`(IN p01_fkModulo int(11))
BEGIN

  SELECT

    usuarios_modulo.fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

    INNER JOIN usuarios_modulo

      ON usuarios.PKUsuario = usuarios_modulo.fkUsuario

  WHERE usuarios_modulo.fkModulo = p01_fkModulo

  AND usuarios.Estado = 1

  ORDER BY Nombres;

END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_NoExisten_Admin` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Admin`(IN p01_fkModulo int(11))
BEGIN



  SELECT

    usuarios.PKUsuario AS fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

  WHERE NOT EXISTS (SELECT

      *

    FROM usuarios_admin

    WHERE usuarios_admin.fkModulo = p01_fkModulo

    AND usuarios.PKUsuario = usuarios_admin.fkUsuario)

  AND Estado = 1

  ORDER BY Nombres;





END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_NoExisten_Admin_it` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Admin_it`(IN p01_fkModulo int(11))
BEGIN



  SELECT

    usuarios.PKUsuario AS fkUsuario,

    CONCAT(usuarios.Nombre, ' ', usuarios.Apellido) AS Nombres,

    Usuario

  FROM usuarios

  WHERE NOT EXISTS (SELECT

      *

    FROM usuarios_admin_it

    WHERE usuarios_admin_it.fkModulo = p01_fkModulo

    AND usuarios.PKUsuario = usuarios_admin_it.fkUsuario)

  AND Estado = 1

  ORDER BY Nombres;





END //

DROP PROCEDURE IF EXISTS `mySP_Select_Usuarios_NoExisten_Depto` //
CREATE DEFINER=`root`@`localhost` PROCEDURE `mySP_Select_Usuarios_NoExisten_Depto`(IN p01_fkDepto int(11))
BEGIN

  SELECT

    u.PKUsuario AS fkUsuario,

    CONCAT(u.Nombre, ' ', u.Apellido) AS Nombres,

    u.Usuario

  FROM usuarios u

  WHERE u.Estado = 1

  AND NOT EXISTS (SELECT

      *

    FROM usuarios_departamento uk

    WHERE -- uk.fkdepto = p01_fkDepto AND 

    u.PKUsuario = uk.fkUsuario)
  ORDER BY Nombres;

END //

DELIMITER ;

