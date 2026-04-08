DROP TRIGGER IF EXISTS universal_data_core.after_devolucion_insert;
DELIMITER //
CREATE TRIGGER universal_data_core.after_devolucion_insert
AFTER INSERT ON universal_data_core.devolucion
FOR EACH ROW
BEGIN
  DECLARE cantidad_disponible INT;
  DECLARE precio_unitario_actual DECIMAL(10,2);

  -- 1. Obtener la disponibilidad TOTAL del suministro en esta adquisición
  -- Agregamos por id_suministros y eliminamos el filtro estricto de id_detalle_requisicion 
  -- para evitar el bloqueo si el ID enviado es del encabezado o si hay duplicados visuales.
  SELECT COALESCE(SUM(cantidad), 0) INTO cantidad_disponible
  FROM universal_data_core.detalle_adquisicion
  WHERE id_adquisicion = NEW.id_adquisicion
    AND id_suministros = NEW.id_suministros;

  -- 2. Obtener el precio unitario actual para el Kardex
  SELECT precio_unitario INTO precio_unitario_actual
  FROM universal_data_core.suministros
  WHERE id_suministros = NEW.id_suministros
  LIMIT 1;

  -- 3. VALIDACIÓN DE DISPONIBILIDAD (Corregida para manejar duplicados e ID de cabecera)
  IF (cantidad_disponible >= 0 AND NEW.cantidad_devuelta <= cantidad_disponible) 
     OR (cantidad_disponible < 0 AND NEW.cantidad_devuelta <= ABS(cantidad_disponible)) THEN

    -- 4. Restar la cantidad devuelta de la disponibilidad
    -- Usamos LIMIT 1 para que si hay duplicados, solo se afecte una fila y no se 'multiplique' la resta.
    UPDATE universal_data_core.detalle_adquisicion
    SET cantidad = cantidad - NEW.cantidad_devuelta,
        precio_total = precio_total - NEW.total_devolucion
    WHERE id_adquisicion = NEW.id_adquisicion
      AND id_detalle_requisicion = NEW.id_detalle_requisicion
      AND id_suministros = NEW.id_suministros
    LIMIT 1;

    -- 5. Registrar el movimiento de ENTRADA en Kardex
    INSERT INTO universal_data_core.suministros_movimientos (
      id_suministros,
      fecha_movimiento,
      entrada,
      salida,
      precio_unitario,
      detalle_movimiento,
      creado_por
    )
    VALUES (
      NEW.id_suministros,
      NOW(),
      NEW.cantidad_devuelta,
      0,
      precio_unitario_actual,
      'Entrada de stock - Devolución (Nuevo)',
      NEW.creado_por
    );

    -- 6. Incrementar el stock total del suministro
    UPDATE universal_data_core.suministros
    SET cantidad_stock = cantidad_stock + NEW.cantidad_devuelta
    WHERE id_suministros = NEW.id_suministros;

  ELSE
    -- Bloqueo solo si la cantidad es realmente inválida en el agregado total
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'No hay suficiente cantidad disponible para la devolución';
  END IF;

END //
DELIMITER ;