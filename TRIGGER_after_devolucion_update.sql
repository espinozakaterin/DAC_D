DROP TRIGGER IF EXISTS universal_data_core.after_devolucion_update;
DELIMITER //
CREATE TRIGGER universal_data_core.after_devolucion_update
AFTER UPDATE ON universal_data_core.devolucion
FOR EACH ROW
BEGIN
  -- Declarar la variable para la cantidad disponible
  DECLARE cantidad_disponible int;
  DECLARE precio_unitario_actual decimal(10, 2);

  -- 1. Obtener la disponibilidad TOTAL del suministro en esta adquisición
  -- Agregamos por id_suministros y eliminamos el filtro estricto de id_detalle_requisicion 
  -- para evitar el bloqueo si el ID enviado es del encabezado o si hay duplicados visuales.
  SELECT COALESCE(SUM(cantidad), 0) INTO cantidad_disponible
  FROM universal_data_core.detalle_adquisicion
  WHERE id_adquisicion = NEW.id_adquisicion
    AND id_suministros = NEW.id_suministros;

  -- 2. Obtener el precio unitario del suministro
  SELECT precio_unitario INTO precio_unitario_actual
  FROM universal_data_core.suministros
  WHERE id_suministros = NEW.id_suministros
  LIMIT 1;

  -- 3. VALIDACIÓN DE CAMBIO EN CANTIDAD (Si es el mismo valor, ignorar stock y kardex)
  -- Esto permite actualizar motivo o descripción sin disparar validación de stock
  IF CAST(OLD.cantidad_devuelta AS SIGNED) <> CAST(NEW.cantidad_devuelta AS SIGNED) THEN
    
    -- CASO A: Si la cantidad devuelta ha aumentado (NEW > OLD)
    IF NEW.cantidad_devuelta > OLD.cantidad_devuelta THEN
      -- Validar disponibilidad de la DIFERENCIA (Misma regla segura: stock positivo o absoluto del negativo histórico)
      IF ( (NEW.cantidad_devuelta - OLD.cantidad_devuelta) <= cantidad_disponible ) 
         OR ( cantidad_disponible < 0 AND (NEW.cantidad_devuelta - OLD.cantidad_devuelta) <= ABS(cantidad_disponible) ) THEN
        
        -- Restar la diferencia de la cantidad en detalle_adquisicion
        -- LIMIT 1 para consistencia con duplicados
        UPDATE universal_data_core.detalle_adquisicion
        SET cantidad = cantidad - (NEW.cantidad_devuelta - OLD.cantidad_devuelta),
            precio_total = precio_total - (NEW.total_devolucion - OLD.total_devolucion)
        WHERE id_adquisicion = NEW.id_adquisicion
          AND id_detalle_requisicion = NEW.id_detalle_requisicion
          AND id_suministros = NEW.id_suministros
        LIMIT 1;

        -- Registrar en Kardex (entrada de stock)
        INSERT INTO universal_data_core.suministros_movimientos (id_suministros,
        fecha_movimiento,
        entrada,
        salida,
        precio_unitario,
        detalle_movimiento,
        creado_por)
          VALUES (NEW.id_suministros, NOW(), NEW.cantidad_devuelta - OLD.cantidad_devuelta, 
          0, precio_unitario_actual, 'Entrada de stock - Devolución (Actualización)', NEW.creado_por);

        -- Actualizar el stock en suministros
        UPDATE universal_data_core.suministros
        SET cantidad_stock = cantidad_stock + (NEW.cantidad_devuelta - OLD.cantidad_devuelta)
        WHERE id_suministros = NEW.id_suministros;
      ELSE
        -- Bloqueo si no hay disponibilidad real en el agregado
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay suficiente cantidad disponible para la devolución';
      END IF;
      
    -- CASO B: Si la cantidad devuelta ha disminuido (NEW < OLD)
    ELSE
      -- Sumar la diferencia ("liberar" stock) a la disponibilidad
      -- LIMIT 1 para consistencia
      UPDATE universal_data_core.detalle_adquisicion
      SET cantidad = cantidad + (OLD.cantidad_devuelta - NEW.cantidad_devuelta),
          precio_total = precio_total + (OLD.total_devolucion - NEW.total_devolucion)
      WHERE id_adquisicion = NEW.id_adquisicion
        AND id_detalle_requisicion = NEW.id_detalle_requisicion
        AND id_suministros = NEW.id_suministros
      LIMIT 1;

      -- Registrar en Kardex (salida de stock)
      INSERT INTO universal_data_core.suministros_movimientos (id_suministros,
      fecha_movimiento,
      entrada,
      salida,
      precio_unitario,
      detalle_movimiento,
      creado_por)
        VALUES (NEW.id_suministros, NOW(), 0, OLD.cantidad_devuelta - NEW.cantidad_devuelta, 
        precio_unitario_actual, 'Salida de stock - Devolución (Actualización)', NEW.creado_por);

      -- Actualizar the stock en suministros
      UPDATE universal_data_core.suministros
      SET cantidad_stock = cantidad_stock - (OLD.cantidad_devuelta - NEW.cantidad_devuelta)
      WHERE id_suministros = NEW.id_suministros;
    END IF;
  END IF;

END //
DELIMITER ;