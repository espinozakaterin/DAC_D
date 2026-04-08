CREATE DEFINER=`root`@`localhost` PROCEDURE `SUM_INSERT_UPDATE_DEVOLUCION`(IN p_id_devolucion int,
IN p_id_adquisicion int,
IN p_id_detalle_requisicion int,
IN p_id_suministros int,
IN p_cantidad_devuelta int,
IN p_precio_unitario decimal(10, 2),
IN p_total_devolucion decimal(10, 2),
IN p_fecha_devolucion date,
IN p_id_motivo_devolucion int,
IN p_motivo_devolucion varchar(255),
IN p_id_proveedor int,
IN p_estado int,
OUT guardado int,
IN userName varchar(30))
BEGIN
  -- Verificar si se debe insertar (cuando p_id_devolucion es NULL, 0 o no existe en la tabla)
  IF p_id_devolucion IS NULL
    OR p_id_devolucion = 0
    OR NOT EXISTS (SELECT
        1
      FROM universal_data_core.devolucion
      WHERE id_devolucion = p_id_devolucion) THEN

    -- Insertar nueva devolución
    INSERT INTO universal_data_core.devolucion (id_adquisicion,
    id_suministros,
    id_detalle_requisicion,
    cantidad_devuelta,
    precio_unitario,
    total_devolucion,
    fecha_devolucion,
    id_motivo_devolucion,
    motivo_devolucion,
    id_proveedor,
    estado,
    creado_por)
      VALUES (p_id_adquisicion, p_id_suministros, p_id_detalle_requisicion, p_cantidad_devuelta, p_precio_unitario, p_total_devolucion, p_fecha_devolucion, p_id_motivo_devolucion, p_motivo_devolucion, p_id_proveedor, p_estado, userName);

    SET guardado = 1;  -- Indica que el registro fue insertado

  ELSE
    -- Actualizar devolución existente
    UPDATE universal_data_core.devolucion
    SET id_adquisicion = p_id_adquisicion,
        id_suministros = p_id_suministros,
        cantidad_devuelta = p_cantidad_devuelta,
        precio_unitario = p_precio_unitario,
        total_devolucion = p_total_devolucion,
        fecha_devolucion = p_fecha_devolucion,
        id_motivo_devolucion = p_id_motivo_devolucion,
        motivo_devolucion = p_motivo_devolucion,
        id_proveedor = p_id_proveedor,
        estado = p_estado,
        fecha_hora_modificado = CURRENT_TIMESTAMP,  -- Actualizamos la fecha de modificación
        modificado_por = userName
    WHERE id_devolucion = p_id_devolucion;

    SET guardado = 2;  -- Indica que el registro fue actualizado
  END IF;
END