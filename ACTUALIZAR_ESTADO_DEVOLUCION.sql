CREATE DEFINER=`root`@`localhost` PROCEDURE `ACTUALIZAR_ESTADO_DEVOLUCION`(IN devolucion_id int,
IN nuevo_estado int)
BEGIN
  -- Caso cuando se elige editar (estado 2 - Editado)
  IF nuevo_estado = 2 THEN
    UPDATE devolucion
    SET estado = 2  -- Cambiar el estado a "Editado"
    WHERE id_devolucion = devolucion_id;

  -- Caso cuando se elige eliminar (estado 3 - Anulado)
  ELSEIF nuevo_estado = 3 THEN
    UPDATE devolucion
    SET estado = 3 -- Cambiar el estado a "Anulado"
    WHERE id_devolucion = devolucion_id;

  -- Caso cuando el estado es "Creado" por defecto
  ELSE
    UPDATE devolucion
    SET estado = 1  -- Devolver el estado a "Creado"
    WHERE id_devolucion = devolucion_id;
  END IF;
END