CREATE DEFINER=`root`@`localhost` PROCEDURE `GET_DEVOLUCIONES`(IN varEstado int)
BEGIN
  SELECT
    dev.id_devolucion,
    a.id_adquisicion,
    s.id_suministros,
    s.nombre AS nombreSuministro,
    da.id_detalle_requisicion,
    dev.cantidad_devuelta,
    dev.precio_unitario,
    dev.total_devolucion,
    dev.fecha_devolucion,
    md.id_motivo_devolucion,
    md.nombre_motivo,
    dev.motivo_devolucion,
    cp.id_proveedor,
    cp.nombre_proveedor,
    dev.estado

  FROM devolucion dev
    INNER JOIN motivo_devolucion md
      ON dev.id_motivo_devolucion = md.id_motivo_devolucion
    INNER JOIN adquisicion a
      ON dev.id_adquisicion = a.id_adquisicion
    INNER JOIN ct_proveedores cp
      ON dev.id_proveedor = cp.id_proveedor
    INNER JOIN suministros s
      ON dev.id_suministros = s.id_suministros
    INNER JOIN detalle_adquisicion da
      ON dev.id_detalle_requisicion = da.id_detalle_requisicion
  WHERE (
  (varEstado = 0)
  OR (varEstado = 3
  AND dev.estado = 3)
  OR (varEstado = 1
  AND dev.estado != 3)
  )
  GROUP BY dev.id_devolucion;

END