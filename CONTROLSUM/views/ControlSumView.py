from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
import json
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

# Create your views here.
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Suministro, Categoria, Proveedor, Almacen

from django.core.files.storage import default_storage
from urllib.parse import urlparse
import os


class SuministroForm(forms.ModelForm):
    class Meta:
        model = Suministro
        fields = [
            'nombre', 
            'descripcion', 
            'categoria', 
            'cantidad_inicial', 
            'cantidad_stock', 
            'precio_unitario', 
            'fecha_adquisicion', 
            'proveedor', 
            'almacen'
        ]
        widgets = {
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date'}),
        }

# --------------------------------- LOGIN -----------------------------------------------#

def logoutRequest(request):
    request.session.flush()

    token = ''

    return HttpResponseRedirect(reverse('login'))

# --------------------------------- DASHBOARD -----------------------------------------------#

## Panel de Acceso
def panel_controlsuministros(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    userName = request.session.get('userName', 'USUARIO')

    return render(request, 'panel_control_suministros.html', {
        'userName': userName
    })

    
# -------------------------------------------------------------------------------------------- #

def dashboard(request):
    id_usuario = request.session.get('user_id')

    if not id_usuario:
        return JsonResponse({'error': 'No se recibió el ID del usuario'}, status=400)

    udcConn = connections['ctrlSum']
    with udcConn.cursor() as cursor:
        # 1. Total de suministros
        cursor.execute("SELECT COUNT(*) FROM universal_data_core.suministros")
        total_suministros = cursor.fetchone()[0] or 0

        # 2. Categorias con conteo de suministros
        cursor.execute("""
            SELECT c.nombre_categoria, COUNT(s.id_suministros)
            FROM universal_data_core.categorias c
            LEFT JOIN universal_data_core.suministros s ON s.id_categoria = c.id_categoria
            GROUP BY c.id_categoria, c.nombre_categoria
        """)
        categorias = [{'categoria': r[0], 'count': r[1]} for r in cursor.fetchall()]

        # 3. Almacenes con conteo de suministros
        cursor.execute("""
            SELECT a.nombre_almacen, COUNT(s.id_suministros)
            FROM universal_data_core.almacen a
            LEFT JOIN universal_data_core.suministros s ON s.id_almacen = a.id_almacen
            GROUP BY a.id_almacen, a.nombre_almacen
        """)
        almacenes = [{'almacen': r[0], 'count': r[1]} for r in cursor.fetchall()]

        # 4. Suministros por mes (Filtro por rango)
        range_type = request.GET.get('range', 'this_year')
        where_clause = "YEAR(fecha_adquisicion) = YEAR(CURDATE())"
        
        if range_type == 'last_year':
            where_clause = "YEAR(fecha_adquisicion) = YEAR(CURDATE()) - 1"
        elif range_type == 'last_6_months':
            where_clause = "fecha_adquisicion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
        elif range_type == 'all':
            where_clause = "1=1"

        cursor.execute(f"""
            SELECT MONTH(fecha_adquisicion) AS mes, COUNT(*) AS cantidad
            FROM universal_data_core.suministros
            WHERE {where_clause}
            GROUP BY MONTH(fecha_adquisicion)
            ORDER BY MONTH(fecha_adquisicion)
        """)
        suministros_mes = [{'mes': r[0], 'cantidad': r[1]} for r in cursor.fetchall()]

        # --- High Frequency Analysis Indicators ---
        
        # 1. Top Used (Asignaciones)
        cursor.execute("""
            SELECT MAX(s.nombre) as display_name, SUM(a.cantidad_asignacion) as total 
            FROM universal_data_core.asignacion a 
            JOIN universal_data_core.suministros s ON a.id_suministros = s.id_suministros 
            GROUP BY TRIM(UPPER(s.nombre)) 
            ORDER BY total DESC 
            LIMIT 5
        """)
        top_productos = [{'nombre': r[0], 'cantidad': r[1]} for r in cursor.fetchall()]

        # 2. No Movement (Not in Asignaciones)
        cursor.execute("""
            SELECT MAX(nombre) as display_name 
            FROM universal_data_core.suministros 
            WHERE id_suministros NOT IN (SELECT DISTINCT id_suministros FROM universal_data_core.asignacion) 
            GROUP BY TRIM(UPPER(nombre))
            LIMIT 5
        """)
        sin_movimiento = [{'nombre': r[0]} for r in cursor.fetchall()]

        # 3. Rotation Frequency
        cursor.execute("""
            SELECT MAX(s.nombre) as display_name, COUNT(a.id_asignacion) as freq 
            FROM universal_data_core.suministros s 
            LEFT JOIN universal_data_core.asignacion a ON s.id_suministros = a.id_suministros 
            GROUP BY TRIM(UPPER(s.nombre)) 
            ORDER BY freq DESC 
            LIMIT 5
        """)
        rotacion = []
        for r in cursor.fetchall():
            f = r[1]
            lbl = 'Alta' if f > 10 else 'Media' if f > 4 else 'Baja'
            rotacion.append({'nombre': r[0], 'status': lbl, 'freq': f})

        # 4. Total Inventory Value (Stock * Price)
        cursor.execute("SELECT SUM(cantidad_stock * precio_unitario) FROM universal_data_core.suministros")
        valor_inventario = cursor.fetchone()[0] or 0

    return JsonResponse({
        'total_suministros': total_suministros,
        'categorias': categorias,
        'almacenes': almacenes,
        'suministros_mes': suministros_mes,
        'top_productos': top_productos,
        'sin_movimiento': sin_movimiento,
        'rotacion': rotacion,
        'valor_inventario': float(valor_inventario)
    })


# --------------------------------- SECCION DE SUMINISTROS -----------------------------------------------#

def listar_suministros(request):
    suministros = Suministro.objects.all()
    return render(request, 'suministros/listarsum.html', {'suministros': suministros})

# -------------------------- Gestion de Suministros ---------------------------------------#

# LISTADO DE SUMINISTROS 
def listado_suministro_data(request):
    
    suministros_data = ""
    categorias_data = ""
    acreedores_data = ""
    almacenes_data = ""

    try:
        
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_SUMINISTROS", [0, 0])
            column_names = [desc[0] for desc in cursor.description]
            suministros_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

        # TOMA LOS DATOS DE LA TABLA CATEGORIAS PARA EL SELECT CATEGORIAS DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_CATEGORIAS", [])
            column_names = [desc[0] for desc in cursor.description]
            categorias_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

        # Cierra la conexión
        udcConn.close()


        # TOMA LOS DATOS DE LA TABLA ALMACEN PARA EL SELECT ALMACEN DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ALMACENES", [0,0])
            column_names = [desc[0] for desc in cursor.description]
            almacenes_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Esto enviará el mensaje de error real a la ventana de alerta de la web
        return JsonResponse({'error': f"ERROR DE BASE DE DATOS: {str(e)}"}, status=500)
    
    context = {
        "suministros": suministros_data,
        "categorias": categorias_data,
        "acreedores": acreedores_data,
        "almacenes": almacenes_data,
        "user_id": request.user.id,  # Pasar el ID del usuario autenticado
    }
    
    return render(request, 'suministros/listarsum.html', context)

# ------------------------------------------------------------------------------------------#

@staticmethod
def obtener_precio_suministro_data(request):
    id_sum = request.GET.get('id') or request.GET.get('id_suministro')

    print("GET COMPLETO:", dict(request.GET))  
    print(f"ID RECIBIDO EN SERVIDOR: {id_sum}")

    try:
        if not id_sum:
            return JsonResponse({'success': False, 'message': 'No se recibió el ID en el servidor'})

        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT precio_unitario 
                FROM universal_data_core.suministros 
                WHERE id_suministros = %s 
                LIMIT 1;
            """, [id_sum])

            row = cursor.fetchone()

            if row:
                return JsonResponse({'success': True, 'precio': float(row[0])})
            else:
                return JsonResponse({'success': False, 'message': 'No se encontró el suministro'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
# ------------------------------------------------------------------------------------------------------------#
def insertar_actualizar_suministro(request):
    try:
        # Recibir datos
        id_suministros = request.POST.get('id_suministros')
        nombre = request.POST.get('nombre_sum')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        cantidad_inicial = request.POST.get('cantidad_inicial')
        cantidad_stock = request.POST.get('cantidad_stock')
        cantidad_minima = request.POST.get('cantidad_minima')
        precio = request.POST.get('precio_unitario')
        fecha = request.POST.get('fecha_adquisicion')
        almacen = request.POST.get('almacen')

        imagen_suministro = request.FILES.get('imagen_suministro')
        imagen_actual = request.POST.get('imagen_actual')

        userName = request.session.get('userName', '')
        fkgrupo = request.POST.get('fkgrupo')
        acreedor = request.POST.get('id_proveedor')
        
        # Validación de cantidad mínima (no puede ser 0 o vacío)
        try:
            val_minima = int(cantidad_minima or 0)
            if val_minima <= 0:
                return JsonResponse({
                    'save': 0,
                    'mensaje': 'La cantidad mínima debe ser mayor a 0.'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'save': 0,
                'mensaje': 'La cantidad mínima debe ser un valor numérico válido mayor a 0.'
            })

        # Manejo de imagen
        if imagen_suministro:
            imagen_path = default_storage.save(f'suministros/{imagen_suministro.name}', imagen_suministro)
            imagen_url = default_storage.url(imagen_path)

        elif imagen_actual:
            ruta_media = urlparse(imagen_actual).path
            imagen_path = os.path.relpath(ruta_media, '/media')
            imagen_url = default_storage.url(imagen_path)

        else:
            imagen_url = None

        udcConn = connections['ctrlSum']

        with udcConn.cursor() as cursor:

            # Validar si ya existe el suministro
            if id_suministros:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM universal_data_core.suministros
                    WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s))
                    AND id_suministros <> %s
                """, [nombre, id_suministros])
            else:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM universal_data_core.suministros
                    WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s))
                """, [nombre])

            existe = cursor.fetchone()[0]

            if existe > 0:
                udcConn.close()
                return JsonResponse({
                    'save': 0,
                    'existe': 1,
                    'mensaje': 'Este producto ya existe.'
                })

            # Guardar usando procedimiento
            cursor.callproc('SUM_INSERT_UPDATE_SUMINISTRO', [
                id_suministros,
                nombre,
                descripcion,
                categoria,
                cantidad_inicial,
                cantidad_stock,
                cantidad_minima,
                precio,
                fecha,
                almacen,
                imagen_url,
                0,
                userName,
                fkgrupo,
                acreedor
            ])

            try:
                cursor.fetchall()
            except:
                pass

            cursor.execute('SELECT @_SUM_INSERT_UPDATE_SUMINISTRO_12')
            guardado = cursor.fetchone()[0]

        udcConn.close()

        if guardado == 1:
            mensaje = "Producto guardado con éxito"
        else:
            mensaje = "Suministro actualizado exitosamente."

        return JsonResponse({
            'save': 1,
            'mensaje': mensaje
        })

    except Exception as e:
        return JsonResponse({
            'save': 0,
            'mensaje': f'Error: {str(e)}',
            'error': str(e)
        })

#-----------------------------------------------------------------------------------------------------#

def actualizar_estado_sum(request):
    if request.method == "POST":
        suministro_id = request.POST.get('id_suministros')
        estadoS = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not suministro_id or not estadoS:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_SUMINISTRO', [suministro_id, estadoS])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# ------------------------------------------------------------------------------------------------------------ #

# Obtiene los suministros bajos en stock
def obtener_stock_bajo_data(request):
    stock_bajo = []

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Consulta directa con alias que coinciden con lo que espera el frontend
            cursor.execute("""
                SELECT s.nombre AS nombre,
                       s.cantidad_stock AS stock,
                       s.cantidad_minima AS stockMinimo
                FROM universal_data_core.suministros s
                WHERE s.cantidad_stock < s.cantidad_minima
                ORDER BY s.cantidad_stock ASC
            """)
            column_names = [desc[0] for desc in cursor.description]
            stock_bajo = [dict(zip(column_names, row)) for row in cursor.fetchall()]

        # Si no se encontraron resultados, se devuelve un mensaje adecuado
        if not stock_bajo:
            return JsonResponse({'message': 'No se encontraron suministros con stock bajo.'}, status=404)
        
        # Devolver los resultados en formato JSON
        return JsonResponse({'suministros_bajos': stock_bajo}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
# -------------------------------------------------------------------------------------- #

def obtener_acreedores(request):
    try:
        # Conexión a la base de datos usando el alias 'ctrlSum' (puedes usar el alias que necesites)
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Ejecutamos la consulta SQL para obtener los acreedores
            cursor.execute("""
                SELECT * 
                FROM universal_data_core.ct_proveedores cp
                WHERE cp.acreedor = 1;
            """)
            
            # Obtener los nombres de las columnas
            column_names = [desc[0] for desc in cursor.description]
            
            # Obtener los resultados y convertirlos a un diccionario
            acreedores_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]
            
            # Si hay datos, devolverlos como un JsonResponse
            return JsonResponse({'acreedores': acreedores_data})
    
    except Exception as e:
        # Manejo de excepciones y errores en la ejecución
        print(f"Error en la ejecución de la consulta o conexión: {str(e)}")
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})
    
# -------------------------------------------------------------------------------------- #

# LISTADO DE ASIGNACIONES
def listado_asignaciones_data(request):
    
    asignaciones_data = ""
    categorias_data = ""
    usuarios_data = ""

    try:
        # TOMA LOS LOS DATOS DE LA TABLA SUMINISTROS
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ASIGNACIONES", [0])
            column_names = [desc[0] for desc in cursor.description]
            asignaciones_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

        # TOMA LOS DATOS DE LA TABLA CATEGORIAS PARA EL SELECT CATEGORIAS DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_CATEGORIAS", [])
            column_names = [desc[0] for desc in cursor.description]
            categorias_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

        # Cierra la conexión
        udcConn.close()

        # TOMA LOS DATOS DE LA TABLA USUARIOS PARA EL SELECT USUARIOS DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_USUARIOS", [])
            column_names = [desc[0] for desc in cursor.description]
            usuarios_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "asignaciones": asignaciones_data,
        "categorias": categorias_data,
        "usuarios": usuarios_data
    }
    
    return render(request, 'suministros/listar_asignaciones.html', context)

#--------------------------------------------------------------------------------------------------------------#

# -------------- Insertar y Actualizacion Asignacion ------------------ #
def insertar_actualizar_asignacion(request):
    try:
        existe = 0

        id_asignacion = request.POST.get('id_asignacion')
        pk_usuario = request.POST.get('nombre_completo')   # este select trae el PKUsuario
        nombre_usuario = request.POST.get('usuario')       # este campo trae ADMIN
        grupos = request.POST.get('grupos')
        categoria = request.POST.get('categoria')
        suministro = request.POST.get('suministro')
        cantidad = request.POST.get('cantidad')
        comentario = request.POST.get('comentario')

        # Si la sesión no trae userName, usar el usuario del formulario
        userName = request.session.get('userName') or nombre_usuario or 'SISTEMA'

        if not id_asignacion or str(id_asignacion).strip() == "":
            id_asignacion = 0
        else:
            id_asignacion = int(id_asignacion)

        if not pk_usuario or str(pk_usuario).strip() == "":
            return JsonResponse({'save': 0, 'error': 'PKUsuario vacío'})

        # --- VALIDACIÓN DE STOCK PARA EVITAR NEGATIVOS EN KARDEX ---
        try:
            val_cantidad = float(cantidad or 0)
            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                # 1. Obtener stock actual del suministro
                cursor.execute("""
                    SELECT nombre, cantidad_stock 
                    FROM universal_data_core.suministros 
                    WHERE id_suministros = %s
                """, [suministro])
                row_sum = cursor.fetchone()
                
                if not row_sum:
                    return JsonResponse({'save': 0, 'error': '⚠️ Suministro no encontrado.'})
                
                nombre_sum = row_sum[0]
                stock_actual = float(row_sum[1] or 0)

                # 2. Validar disponibilidad según sea Nuevo o Edición
                if id_asignacion == 0:
                    # Caso Nuevo: La cantidad no debe superar el stock actual
                    if val_cantidad > stock_actual:
                        return JsonResponse({
                            'save': 0, 
                            'error': f'⚠️ Stock insuficiente para "{nombre_sum}". Disponible: {stock_actual}'
                        })
                else:
                    # Caso Edición: Debemos recuperar la cantidad previa asignada
                    cursor.execute("""
                        SELECT cantidad_asignacion 
                        FROM universal_data_core.asignacion 
                        WHERE id_asignacion = %s
                    """, [id_asignacion])
                    row_old = cursor.fetchone()
                    cant_previa = float(row_old[0] or 0) if row_old else 0
                    
                    # La cantidad disponible real es el stock actual + lo que ya habíamos "tomado" antes
                    disponible_total = stock_actual + cant_previa
                    
                    if val_cantidad > disponible_total:
                        return JsonResponse({
                            'save': 0, 
                            'error': f'⚠️ Stock insuficiente para "{nombre_sum}". Máximo permitido (incluyendo lo ya asignado): {disponible_total:.2f}'
                        })
        except Exception as e_stock:
            return JsonResponse({'save': 0, 'error': f'Error validando stock: {str(e_stock)}'})

        with udcConn.cursor() as cursor:
            cursor.callproc('SUM_INSERT_UPDATE_ASIGNACION', [
                id_asignacion,    # p_id_asignacion
                nombre_usuario,   # p_Nombre
                pk_usuario,       # p_PKUsuario
                grupos,           # p_PKgrupo
                categoria,        # p_id_categoria
                suministro,       # p_id_suministros
                cantidad,         # p_cantidad_asignacion
                comentario,       # p_comentario
                0,                # OUT guardado
                userName          # userName / creado_por
            ])

            cursor.execute('SELECT @_SUM_INSERT_UPDATE_ASIGNACION_8')
            guardado = cursor.fetchone()[0]

            if guardado == 1:
                existe = 0
            else:
                existe = 2

        datos = {'save': 1, 'existe': existe}

    except Exception as e:
        datos = {'save': 0, 'error': str(e)}

    return JsonResponse(datos)
# ----------------------------------------------------------------------------------------------------- #

# Obtiene los datos de la tabla Suministro


# ----------------------------------------------------------------------------------------------------- #

# Obtiene los grupos depende el usuario


# ----------------------------------------------------------------------------------------------------- #

def get_suministros_data(request):
    varEstado = request.POST.get('varEstado') or request.GET.get('varEstado') or 0

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            sql = """
                SELECT
                    s.id_suministros AS id,
                    s.id_suministros AS id_suministros,
                    s.nombre AS nombre,
                    s.descripcion AS descripcion,
                    c.nombre_categoria AS nombre_categoria,
                    s.cantidad_inicial AS cantidad_inicial,
                    s.cantidad_stock   AS cantidad_stock,
                    s.cantidad_minima  AS cantidad_minima,
                    s.precio_unitario AS precio_unitario,
                    s.fecha_adquisicion AS fecha_adquisicion,
                    p.nombre_proveedor AS nombre_proveedor,
                    a.nombre_almacen   AS nombre_almacen,
                    a.ubicacion_almacen AS ubicacion_almacen,

                    s.id_categoria AS id_categoria,
                    s.id_almacen AS id_almacen,
                    s.id_proveedor AS id_proveedor,
                    s.fkgrupo AS PKgrupo,
                    s.imagen_url AS imagen_url,

                    --  AQUÍ EL NOMBRE DEL GRUPO
                    g.nombre_grupo AS nombre_grupo,

                    s.estado AS estado
                FROM universal_data_core.suministros s
                INNER JOIN universal_data_core.categorias c ON c.id_categoria = s.id_categoria
                INNER JOIN universal_data_core.almacen a ON a.id_almacen = s.id_almacen
                INNER JOIN universal_data_core.ct_proveedores p ON p.id_proveedor = s.id_proveedor

                --  ESTE JOIN ES EL QUE TE FALTA
                LEFT JOIN universal_data_core.grupos g ON g.id_grupo = s.fkgrupo
            """

            where_clauses = []
            params = []

            if str(varEstado) not in ("0", "", "None"):
                where_clauses.append("s.estado = %s")
                params.append(int(varEstado))

            # Filtro Real de Stock Bajo
            stock_bajo = request.POST.get('stock_bajo') or request.GET.get('stock_bajo')
            if stock_bajo == '1':
                where_clauses.append("s.cantidad_stock < s.cantidad_minima")

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(sql, params)

            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({'data': data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# ----------------------------------------------------------------------------------------------------- #
def obtener_suministros_por_categoria_data(request):
    try:
        categoria_id = request.POST.get('categoria_id') or request.GET.get('categoria_id')

        if not categoria_id or categoria_id in ('', '#'):
            return JsonResponse({"suministros": []})

        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            sql = """
                SELECT id_suministros, nombre, id_categoria
                FROM universal_data_core.suministros
                WHERE id_categoria = %s AND estado != 3
                ORDER BY nombre ASC
            """
            cursor.execute(sql, [categoria_id])
            filas = cursor.fetchall()

        suministros = []
        for row in filas:
            suministros.append({
                "id_suministros": row[0],
                "nombre": row[1]
            })

        return JsonResponse({"suministros": suministros})

    except Exception as e:
        return JsonResponse({"suministros": [], "error": str(e)}, status=500)
# ----------------------------------------------------------------------------------------------------- #
#--------NUEVA Asignacion - SUMINISTROS----------#
def obtener_todos_suministros_data(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT id_suministros, nombre
                FROM universal_data_core.suministros
                ORDER BY nombre
            """)
            rows = cursor.fetchall()

        data = [{"id": r[0], "nombre": r[1]} for r in rows]

        return JsonResponse({"data": data})

    except Exception as e:
        return JsonResponse({"data": [], "error": str(e)}, status=500)


 #----------------------------------------------------------------------3

def obtener_asignacion_data(request):
    id_asignacion = request.GET.get('id_asignacion')

    if not id_asignacion:
        return JsonResponse({'error': 'ID de asignación no proporcionado'}, status=400)

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc('SUM_GET_ASIGNACIONES', [0])  # Ajusta el filtro según lo necesario
            resultado = cursor.fetchall()

        # Buscar la asignación específica en los resultados
        asignacion = next(({
            'id_asignacion': row[0],
            'PKUsuario': row[1],
            'Nombre': row[2],
            'Usuario': row[3],
            'PKgrupo': row[4],
            'GrupoNombre': row[5],
            'id_categoria': row[6],
            'nombre_categoria': row[7],
            'id_suministros': row[8],
            'nombre': row[9],
            'cantidad_asignacion': row[10],
            'comentario': row[11],
            'fecha_asignacion': str(row[12]),
            'estado': row[13],
            'fecha_hora_creacion': str(row[14]),
            'fecha_hora_modificado': str(row[15]),
            'creado_por': str(row[16]),
        } for row in resultado if row[0] == int(id_asignacion)), None)

        if asignacion:
            return JsonResponse({'asignacion': asignacion})
        else:
            return JsonResponse({'error': 'No se encontró la asignación'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# -------------------------------------------------------------------------------------- #

# def proveedores_por_categoria_data(request):
#     categoria_id = request.POST.get('id_categoria')
#     #print(f"Categoria ID recibido: {categoria_id}")  //Depuración

#     # Verificar que el id de la categoría no esté vacío
#     if categoria_id:
#         try:
#             # Convertimos el id a entero para evitar posibles problemas de tipo
#             categoria_id = int(categoria_id)
#             # Conexión a la base de datos
#             udcConn = connections['ctrlSum']
#             with udcConn.cursor() as cursor:
#                 # Llamar al procedimiento almacenado con el id de la categoría
#                 cursor.callproc("SUM_GET_PROVEEDORES_CATEGORIAS", [categoria_id])
#                 column_names = [desc[0] for desc in cursor.description]
#                 proveedores_data = [
#                     dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
#                 ]

#             # Cierra la conexión
#             udcConn.close()

#             # Devolver los proveedores en formato JSON
#             return JsonResponse({'proveedores': proveedores_data})

#         except Exception as e:
#             # Manejo de excepciones
#             return JsonResponse({'error': str(e)})

#     # Si no se recibió un ID de categoría válido
#     return JsonResponse({'error': 'No se recibió un id de categoría válido.'})

# ---------------------------------------------------------------------------------------------------------#
# --------------------------------- SECCION DE ASIGNACIONES -----------------------------------------------#

def listar_asignaciones(request):
    asignaciones = asignaciones.objects.all()
    return render(request, 'suministros/listar_asignaciones.html', {'asignaciones': asignaciones})

# --------------------------------- GESTION DE ASIGNACIONES -----------------------------------------------#

# Obtiene los datos de la tabla Asignaciones
def get_asignaciones_data (request):
    varEstado = int(request.POST.get('varEstado'))  # Convertir a entero, por defecto es 0
    asignaciones_data = ''

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ASIGNACIONES", [varEstado])
            column_names = [desc[0] for desc in cursor.description]
            asignaciones_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        udcConn.close()
        
        return JsonResponse({'data': asignaciones_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})

#----------------------------------------------------------------------------------------------------#

def obtener_usuario_por_nombre_data(request):
    pk_usuario = request.POST.get('PKUsuario')  # Obtener el PKUsuario desde el request
    print(f"PKUsuario recibido en el backend: {pk_usuario}")  # Depuración

    # Verificar si se recibió un PKUsuario válido
    if not pk_usuario or not pk_usuario.isdigit():
        return JsonResponse({'error': 'No se recibió un PKUsuario válido.'})

    try:
        # Convertir pk_usuario a entero
        pk_usuario = int(pk_usuario)

        # Conexión a la base de datos usando el alias 'ctrlSum'
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamamos al procedimiento almacenado con el PKUsuario como parámetro
            cursor.callproc("SUM_GET_NOMBREC_USUARIOS", [pk_usuario])

            # Obtener los resultados del procedimiento almacenado
            column_names = [desc[0] for desc in cursor.description]
            usuario_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]

            # Depuración: Ver qué datos se obtienen
            print(f"Datos recibidos del procedimiento almacenado: {usuario_data}")

            # Si hay datos, extraemos el nombre de usuario
            if usuario_data:
                usuario = usuario_data[0].get('Usuario')  # Suponiendo que 'Usuario' es el nombre de la columna
            else:
                usuario = None

        # Si se encontró el usuario, lo devolvemos; si no, retornamos un error
        if usuario:
            return JsonResponse({'usuario': usuario})
        else:
            return JsonResponse({'error': 'Usuario no encontrado.'})

    except Exception as e:
        # Manejo de excepciones y errores en la ejecución
        print(f"Error en la ejecución del procedimiento o conexión: {str(e)}")
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})

# ---------------------------------------------------------------------------------------------------- #

def actualizar_estado_asignacion(request):
    if request.method == "POST":
        asignacion_id = request.POST.get('id_asignacion')
        estadoA = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not asignacion_id or not estadoA:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_ASIGNACION', [asignacion_id, estadoA])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

# ------------------------------------- SECCION DE REQUISICIONES --------------------------------------------------- #   

def listado_requisicion_data(request):

    requisicion_data = ""
    categorias_data = ""
    acreedores_data = ""
    usuarios_data = ""

    try:
        # TOMA LOS LOS DATOS DE LA TABLA REQUISICION
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("GET_REQUISICIONES", [0])
            column_names = [desc[0] for desc in cursor.description]
            requisicion_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

        # TOMA LOS DATOS DE LA TABLA CATEGORIAS PARA EL SELECT CATEGORIAS DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_CATEGORIAS", [])
            column_names = [desc[0] for desc in cursor.description]
            categorias_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

        # Cierra la conexión
        udcConn.close()

        # TOMA LOS DATOS DE LOS ACREEDORES
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT * 
                FROM universal_data_core.ct_proveedores cp
                WHERE cp.acreedor = 1;
            """)
            column_names = [desc[0] for desc in cursor.description]
            acreedores_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        udcConn.close()

        # TOMA LOS DATOS DE LOS USUARIOS
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_USUARIOS", [])
            column_names = [desc[0] for desc in cursor.description]
            usuarios_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "requisicion": requisicion_data,
        "categorias": categorias_data,
        "acreedores": acreedores_data,
        "usuarios": usuarios_data
    }
    return render(request, 'suministros/listado_requisiciones.html', context)
  

# ----------------------------------------------------------------------------------------------------------------------------- #

def obtener_detalles_requisicion_data(request):
    # Obtener el ID de la requisición desde la solicitud
    id_requisicion = request.GET.get('id_requisicion')

    if not id_requisicion:
        return JsonResponse({'error': 'No se proporcionó un ID de requisición válido.'})

    try:
        # Conectar a la base de datos y ejecutar el procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc('GET_DETALLES_REQUISICION', [id_requisicion])
            
            # Obtener los resultados
            column_names = [desc[0] for desc in cursor.description]
            detalles_requisicion = [
                dict(zip(column_names, row)) for row in cursor.fetchall()
            ]
        
        # Retornar la respuesta en formato JSON
        return JsonResponse({'detalles': detalles_requisicion})

    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})


# ----------------------------------------------------------------------------------------------------------------------------- #
def obtener_requisicion_y_detalle_data(request):
    # Obtener el ID de la requisición desde la solicitud
    id_requisicion = request.GET.get('id_requisicion')

    if not id_requisicion:
        return JsonResponse({'error': 'No se proporcionó un ID de requisición válido.'})

    try:
        # Conectar a la base de datos y ejecutar el procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamar al procedimiento almacenado que obtiene la requisición y los detalles
            cursor.callproc('GET_REQUISICION_Y_DETALLES', [id_requisicion])
            
            # Obtener los resultados de la requisición
            column_names = [desc[0] for desc in cursor.description]
            requisicion_data = dict(zip(column_names, cursor.fetchone()))  # solo un resultado para la requisición

            # Obtener los resultados de los detalles
            cursor.nextset()  # Mover al siguiente conjunto de resultados (detalles)
            column_names = [desc[0] for desc in cursor.description]
            detalles_requisicion = [
                dict(zip(column_names, row)) for row in cursor.fetchall()
            ]
        
        # Retornar la respuesta en formato JSON con los datos de la requisición y los detalles
        return JsonResponse({
            'requisicion': requisicion_data,
            'detalles': detalles_requisicion
        })

    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})

# ----------------------------------------------------------------------------------------------------------------------------- #

# Obtiene los datos de la tabla requisicion
def get_requisicion_data (request):
    varEstado = int(request.POST.get('varEstado'))  # Convertir a entero, por defecto es 0
    requisicion_data = ''

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("GET_REQUISICIONES", [varEstado])

            column_names = [desc[0] for desc in cursor.description]
            requisicion_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        udcConn.close()
        
        return JsonResponse({'data': requisicion_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
# --------------------------------------------------------------------------------------------------------------- #

# Obtiene los datos de la tabla usuarios
def obtener_nombres_usuarios_data (request):
    
    try:
        # Conexión a la base de datos y ejecución del procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamar al procedimiento almacenado
            cursor.callproc("GET_NOMBRES", [])
            column_names = [desc[0] for desc in cursor.description]
            usuarios_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]
        
        udcConn.close()
        
        return JsonResponse({'usuarios': usuarios_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
# -------------------------------------------------------------------------------------- #

def insertar_actualizar_requisicion_data(request):
    try:
        existe = 0

        # Verificar qué datos están llegando
        print(request.POST)

        id_requisicion = request.POST.get('id_requisicion')
        if not id_requisicion:
            id_requisicion = None  # Esto permitirá al procedimiento almacenado insertar una nueva requisición

        # Recuperar los demás datos del formulario
        PKUsuario = request.POST.get('PKUsuario')
        PKgrupo = request.POST.get('PKgrupo')
        id_proveedor = request.POST.get('id_proveedor')
        fecha_pedido = request.POST.get('fecha_pedido')
        fecha_pago = request.POST.get('fecha_pago')
        costo_total = request.POST.get('costo_total')
        estado_requisicion = request.POST.get('estado_requisicion', 1)
        estado = request.POST.get('estado')

        userName = request.session.get('userName', '')

        # Validar que los valores esenciales no estén vacíos
        if not PKUsuario or not PKgrupo or not id_proveedor or not fecha_pedido or not fecha_pago or not costo_total:
            raise ValueError("Faltan datos requeridos en la requisición.")
        
        # Validar que los valores numéricos sean positivos
        if float(costo_total) <= 0:
            raise ValueError("El costo total debe ser un valor positivo.")

        with transaction.atomic():  # Usar transacción para asegurar que todo sea consistente
            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                args = [
                    id_requisicion if id_requisicion else 0,  # Enviar 0 si es nuevo
                    PKUsuario, 
                    PKgrupo,
                    id_proveedor, 
                    fecha_pedido, 
                    fecha_pago, 
                    costo_total, 
                    estado_requisicion,
                    estado, 
                    0,  # OUT parameter inicializado
                    userName
                ]
                cursor.callproc('SUM_INSERT_UPDATE_REQUISICION', args)

                # Recuperar el valor OUT después de la ejecución
                cursor.execute('SELECT @_SUM_INSERT_UPDATE_REQUISICION_9')
                p_result_id_requisicion = cursor.fetchone()[0]

                if p_result_id_requisicion == id_requisicion :
                    existe = 1
                    
        datos = {'save': 1, 'id_requisicion': p_result_id_requisicion, 'existe': existe, 'message': '✅ Requisición procesada correctamente.'}

    except Exception as e:
        print(e)
        datos = {'save': 0, 'error': f'⚠️ Error: {str(e)}'}

    return JsonResponse(datos)

# ---------------------------------------------------------------------------------------------- #

def insertar_actualizar_detalle_requisicion_data(request):
    try:
        id_requisicion = request.POST.get('id_requisicion')
        detalles = json.loads(request.POST.get('detalles'))

        if not detalles:
            raise ValueError("No se han agregado detalles para la requisición.")

        with transaction.atomic():
            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                for detalle in detalles:
                    # Validar cada detalle
                    if not detalle.get('id_suministros') or not detalle.get('cantidad') or not detalle.get('precio_unitario') or not detalle.get('justificacion'):
                        raise ValueError("Faltan datos en los detalles de la requisición.")
                    if detalle['cantidad'] <= 0 or detalle['precio_unitario'] <= 0:
                        raise ValueError("La cantidad y el precio unitario deben ser mayores a cero.")
                    if not detalle['justificacion'].strip():
                        raise ValueError("La justificación no puede estar vacía.")

                    # Llamar al procedimiento almacenado incluyendo la justificación
                    cursor.callproc('SUM_INSERT_UPDATE_DETALLE_REQUISICION', [
                        detalle.get('id_detalle_requisicion', 0), 
                        id_requisicion,
                        detalle['id_suministros'],
                        detalle['cantidad'],
                        detalle['precio_unitario'],
                        detalle['justificacion']
                    ])

        datos = {'save': 1, 'message': 'Detalles de requisición guardados correctamente.'}

    except Exception as e:
        datos = {'save': 0, 'error': f'⚠️ Error: {str(e)}'}

    return JsonResponse(datos)


# -------------------------------------------------------------------------------------------------------------------------------------- #

# CAMBIAR EL ESTADO DE REQUISICION

# Función para ejecutar el procedimiento almacenado que cambia el estado
def ejecutar_procedimiento(requisicion_id):
    try:
        # Conexión a la base de datos
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamar al procedimiento almacenado 'CAMBIAR_ESTADO_REQUISICION'
            cursor.callproc('universal_data_core.CAMBIAR_ESTADO_REQUISICION', [requisicion_id])
            # Si deseas capturar el resultado, puedes usar fetchall() o fetchone()
            cursor.fetchall()
    except Exception as e:
        # En caso de error, imprimir y lanzar la excepción
        raise Exception(f"Error al ejecutar el procedimiento almacenado: {str(e)}")


# Vista que se llama desde el frontend para cambiar el estado
def actualizar_estado(request):
    if request.method == "POST":
        # Obtener el id de la requisición desde la solicitud
        id_requisicion = request.POST.get("id_requisicion")

        # Verifica que el id_requisicion sea válido
        if not id_requisicion:
            return JsonResponse({"success": False, "error": "ID de requisición no proporcionado."})

        try:
            # Ejecutar el procedimiento almacenado para cambiar el estado de la requisición
            ejecutar_procedimiento(id_requisicion)

            # Si no hay errores, se confirma el éxito
            return JsonResponse({"success": True})

        except Exception as e:
            # En caso de error, se maneja la excepción
            return JsonResponse({"success": False, "error": f"Error al ejecutar el procedimiento: {str(e)}"})

# --------------------------------------------------------------------------------------- #

def obtener_detalles_data(request):
    # Obtener el ID de la requisición desde la solicitud
    id_requisicion = request.GET.get('id_requisicion')

    if not id_requisicion:
        return JsonResponse({'error': 'No se proporcionó un ID de requisición válido.'})

    try:
        # Conectar a la base de datos y ejecutar el procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Verificar si la requisición existe
            cursor.execute('SELECT COUNT(*) FROM universal_data_core.requisicion WHERE id_requisicion = %s', [id_requisicion])
            if cursor.fetchone()[0] == 0:
                return JsonResponse({'error': 'No se encontró la requisición con el ID proporcionado.'})

            # Llamar al procedimiento almacenado
            cursor.callproc('GET_DETALLES_REQUISICION', [id_requisicion])

            # Obtener los resultados
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            if not rows:
                return JsonResponse({'error': 'No se encontraron detalles para esta requisición.'})

            detalles_requisicion = []
            articulos = []
            detalle = dict(zip(column_names, rows[0]))

            for row in rows:
                row_dict = dict(zip(column_names, row))
                articulo = {
                    'id_detalle_requisicion': row_dict.get('id_detalle_requisicion'),
                    'id_suministros': row_dict.get('id_suministros'),
                    'nombre_suministro': row_dict.get('nombre', ''),  # Nuevo campo
                    'cantidad': row_dict.get('cantidad', 0),
                    'precio_unitario': row_dict.get('precio_unitario', 0),
                    'precio_total': row_dict.get('precio_total', 0)
                }
                articulos.append(articulo)

            detalle['articulos'] = articulos
            detalles_requisicion.append(detalle)

        return JsonResponse({'detalles': detalles_requisicion})

    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})

# --------------------------------------------------------------------------------------------------------------------------

def editar_detalle_requisicion_data(request):
    if request.method == 'POST':
        try:
            id_detalle = request.POST.get('id_detalle_requisicion')
            id_suministro = request.POST.get('suministro')
            cantidad = request.POST.get('cantidad')
            justificacion = request.POST.get('justificacion')

            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                cursor.callproc('EDITAR_DETALLE_REQUISICION', [id_detalle, id_suministro, cantidad, justificacion])

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# ---------------------------------------------------------------------------------------------------------------------- #
def get_almacenes_por_usuario(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Seleccionamos todas las columnas para no dejar nada por fuera
            # Eliminamos el WHERE y el INNER JOIN
            cursor.execute("""
                SELECT id_almacen, nombre_almacen 
                FROM universal_data_core.almacen
            """)

            rows = cursor.fetchall()

            # Mapeamos los datos para que el JavaScript los reconozca
            almacenes = [{
                "id": r[0],
                "nombre": r[1],
                "id_almacen": r[0],
                "NombreAlmacen": r[1],
            } for r in rows]

        return JsonResponse({"data": almacenes})

    except Exception as e:
        # Si hay un error (ej. nombre de tabla mal escrito), lo veremos aquí
        return JsonResponse({"data": [], "error": str(e)}, status=500)


#---------------------------GRUPO ALMACENES-----------------#

def get_grupos_data(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT id_grupo, nombre_grupo
                FROM universal_data_core.grupos
            """)

            rows = cursor.fetchall()

            grupos = [{
                "id_grupo": r[0],
                "nombre_grupo": r[1]
            } for r in rows]

        return JsonResponse({"data": grupos})

    except Exception as e:
        return JsonResponse({"data": [], "error": str(e)}, status=500)

# ---------------------------------------------------------------------------------------------------------------------- #

def verificar_detalles_requisicion_data(request):
    id_requisicion = request.GET.get("id_requisicion")

    if not id_requisicion:
        return JsonResponse({"error": "ID de requisición no proporcionado"}, status=400)

    try:
        # Establece la conexión a la base de datos
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("universal_data_core.GET_DETALLES_REQUISICION", [id_requisicion])
            detalles = cursor.fetchall()

        tiene_detalles = len(detalles) > 0  # Si hay resultados, la requisición tiene detalles
        return JsonResponse({"tiene_detalles": tiene_detalles})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------------------------------------------------------- #
# ESTO HACE QUE EL GRUPO SALGA AUTOMÁTICO (Línea 525 aprox)
def grupos_por_usuario_data(request):
    id_usuario = request.GET.get('pk_usuario') or request.GET.get('usuario_id')

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT g.PKgrupo AS id, g.Nombre AS nombre
                FROM global_security.usuarios_grupo ug
                INNER JOIN global_security.grupos g
                    ON ug.fkGrupo = g.PKgrupo
                WHERE ug.fkUsuario = %s
            """, [id_usuario])

            result = cursor.fetchall()

            grupos = []
            for row in result:
                grupos.append({
                    "id": row[0],
                    "nombre": row[1]
                })

            return JsonResponse({"data": grupos})

    except Exception as e:
        return JsonResponse({"data": [], "error": str(e)}, status=500)
# ---------------------------------------------------------------------------------------------------------------------- #

def actualizar_estado_requisicion(request):
    if request.method == "POST":
        requisicion_id = request.POST.get('id_requisicion')
        estadoR = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not requisicion_id or not estadoR:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_REQUISICION', [requisicion_id, estadoR])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# -----------------------------------------------------------------------------------------------------------------------------

def actualizar_estado_detalle_requisicion_data(request):
    if request.method == "POST":
        detalle_requisicion_id = request.POST.get('id_detalle_requisicion')
        estadoDR = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not detalle_requisicion_id or not estadoDR:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_DETALLE_REQUISICION', [detalle_requisicion_id, estadoDR])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# -----------------------------------------------------------------------------------------------------------------------------

def actualizar_estado_sum(request):
    if request.method == "POST":
        suministro_id = request.POST.get('id_suministros')
        estadoS = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not suministro_id or not estadoS:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_SUMINISTRO', [suministro_id, estadoS])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# ---------------------------------------- SECCION DE PROVEEDORES POR CATEGORIA -------------------------------------------------

# def listado_proveedores_categorias_data(request):
    
#     categorias_data = ""
#     proveedor_data = ""

#     try:
#         # TOMA LOS DATOS DE LA TABLA CATEGORIAS PARA EL SELECT CATEGORIAS DEL HTML
#         udcConn = connections['ctrlSum']
#         with udcConn.cursor() as cursor:
#             cursor.callproc("SUM_GET_CATEGORIAS", [])
#             column_names = [desc[0] for desc in cursor.description]
#             categorias_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

#         # Cierra la conexión
#         udcConn.close()

#         # TOMA LOS DATOS DE LA TABLA PROVEEDORES PARA EL SELECT PROVEEDORES DEL HTML
#         udcConn = connections['ctrlSum']
#         with udcConn.cursor() as cursor:
#             cursor.callproc("GET_PROVEEDORES", [])
#             column_names = [desc[0] for desc in cursor.description]
#             proveedor_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
#         # Cierra la conexión
#         udcConn.close()


#     except Exception as e:
#         # Manejo de excepciones, puedes personalizar esto según tus necesidades
#         return JsonResponse({'error': str(e)})
    
#     context = {
#         "categorias": categorias_data,
#         "proveedores": proveedor_data
#     }
    
#     return render(request, 'suministros/listado_proveedores_categorias.html', context)

# --------------------------------------------------------------------------------------------------------------------------

# PARA CAMBIAR EL ESTADO DE LA SECCION DE PROVEEDORES POR CATEGORIA
# def get_proveedor_categoria_data (request):
#     varEstado = int(request.POST.get('varEstado'))  # Convertir a entero, por defecto es 0
#     proveedorC_data = ''

#     try:
#         udcConn = connections['ctrlSum']
#         with udcConn.cursor() as cursor:
#             cursor.callproc("GET_PROVEEDORES_CATEGORIAS", [varEstado])
#             column_names = [desc[0] for desc in cursor.description]
#             proveedorC_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
#         udcConn.close()
        
#         return JsonResponse({'data': proveedorC_data})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

# -------------------------------------------------------------------------------------- #

# def insertar_actualizar_proveedor_categoria(request):
#     try:
#         existe = 0

#         id_categorias_proveedores = request.POST.get('id_categorias_proveedores')  
#         id_proveedor = request.POST.get('id_proveedor')
#         id_categoria = request.POST.get('id_categoria')

#         udcConn = connections['ctrlSum']
#         with udcConn.cursor() as cursor:
#             cursor.callproc('SUM_INSERT_UPDATE_PROVEEDOR_CATEGORIA', [
#                 id_categorias_proveedores,
#                 id_proveedor,
#                 id_categoria,
#                 0
#             ]) 

#             cursor.execute('SELECT @_SUM_INSERT_UPDATE_PROVEEDOR_CATEGORIA_3')
#             guardado = cursor.fetchone()[0]

#             if guardado == 1:
#                 existe = 0  # Indica que se insertó un nuevo registro
#             else:
#                 existe = 2  # Indica que se actualizó un registro existente
        
#         udcConn.close()

#         datos = {'save': 1, 'existe': existe}
#     except Exception as e:
#         datos = {'save': 0, 'error': str(e)}
    
#     return JsonResponse(datos)

# -------------------------------------------------------------------------------------------------------------- #

# def actualizar_estado_proveedor_categoria(request):
#     if request.method == "POST":
#         proveedor_categorias_id = request.POST.get('id_categorias_proveedores')
#         estadoPC = request.POST.get('estado')  # Obtener el estado nuevo

#         # Validación de los parámetros
#         if not proveedor_categorias_id or not estadoPC:
#             return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

#         try:
#             # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
#             udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
#             with udcConn.cursor() as cursor:
#                 cursor.callproc('ACTUALIZAR_ESTADO_PROVEEDORES_CATEGORIAS', [proveedor_categorias_id, estadoPC])

#             return JsonResponse({'success': True})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})

# --------------------------------------- SECCION DE ALMACENES  ------------------------------------------------ #

def listado_almacenes_data(request):
    
    almacenes_data = ""

    try:
        # TOMA LOS DATOS DE LA TABLA ALMACEN
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ALMACENES", [0,0])
            column_names = [desc[0] for desc in cursor.description]
            almacenes_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "almacenes": almacenes_data
    }
    
    return render(request, 'suministros/listado_almacenes.html', context)

#-----------------------------------------------------------------------------------------------------#

def get_almacenes_data(request):
    try:
        varEstado = int(request.GET.get('varEstado', 0))
        udcConn = connections['ctrlSum']

        with udcConn.cursor() as cursor:

            sql = """
                SELECT 
                    a.id_almacen,
                    a.nombre_almacen,
                    a.ubicacion_almacen,
                    DATE(a.fecha_hora_creacion) AS fecha_hora_creacion,
                    a.fkgrupo AS PKgrupo,
                    COALESCE(g.nombre_grupo, 'Sin grupo') AS GrupoNombre,
                    a.estado
                FROM universal_data_core.almacen a
                LEFT JOIN universal_data_core.grupos g
                    ON a.fkgrupo = g.id_grupo
            """

            params = []

            if varEstado != 0:
                sql += " WHERE a.estado = %s"
                params.append(varEstado)

            cursor.execute(sql, params)

            column_names = [desc[0] for desc in cursor.description]

            almacen_data = [
                dict(zip(column_names, row))
                for row in cursor.fetchall()
            ]

        return JsonResponse({'data': almacen_data})

    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)}, status=500)
#-----------------------------------------------------------------------------------------------------#

def insertar_actualizar_almacen_data(request):
    try:
        existe = 0

        # Obtener los valores del POST
        id_almacen = request.POST.get('id_almacen')
        nombre_almacen = request.POST.get('nombre_almacen')
        ubicacion_almacen = request.POST.get('ubicacion_almacen')
        fkgrupo = request.POST.get('fkgrupo')
        userName = request.session.get('userName', '')

        # Si viene vacío, mandarlo como None
        if not id_almacen or id_almacen == '':
            id_almacen = None
        else:
            id_almacen = int(id_almacen)

        # Conexión a la base de datos
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc('SUM_INSERT_UPDATE_ALMACEN', [
                id_almacen,
                nombre_almacen,
                ubicacion_almacen,
                0,
                userName,
                fkgrupo
            ])

            cursor.execute('SELECT @_SUM_INSERT_UPDATE_ALMACEN_3')
            guardado = cursor.fetchone()[0]

            if guardado == 1:
                existe = 0
            else:
                existe = 2

        udcConn.close()

        datos = {'save': 1, 'existe': existe}

    except Exception as e:
        datos = {'save': 0, 'error': str(e)}

    return JsonResponse(datos)

# ----------------------------------------------------------------------------------------------------------------- #

def actualizar_estado_almacenes(request):
    if request.method == "POST":
        almacen_id = request.POST.get('id_almacen')
        estadoAlmacen = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not almacen_id or not estadoAlmacen:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_ALMACEN', [almacen_id, estadoAlmacen])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# ----------------------------------------------------------------------------------------------------------------- #

# LISTADO DE SUMINISTROS 
def listado_adquisicion_data(request):
    
    adquisicion_data = ""

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ADQUISICION", [0])
            column_names = [desc[0] for desc in cursor.description]
            adquisicion_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "adquisicion": adquisicion_data
    }
    
    return render(request, 'suministros/listado_adquisicion.html', context)



# Obtiene los datos de la tabla Adquisicion
def get_adquisicion_data (request):
    varEstado = int(request.POST.get('varEstado'))  # Convertir a entero, por defecto es 0
    adquisicion_data = ''

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_ADQUISICION", [varEstado])
            column_names = [desc[0] for desc in cursor.description]
            adquisicion_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        udcConn.close()
        
        return JsonResponse({'data': adquisicion_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})

# ----------------------------------------------------------------------------------------------------------------- #


def obtener_requisiciones_usuario(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Consulta directa para obtener todas las requisiciones activas
            # con los campos que el frontend necesita para llenar el select
            cursor.execute("""
                SELECT
                    r.id_requisicion,
                    COALESCE(u.Nombre, 'Sin nombre')       AS Nombre,
                    r.PKUsuario,
                    r.PKgrupo,
                    COALESCE(g.Nombre, 'Sin grupo')        AS GrupoNombre,
                    COALESCE(p.nombre_proveedor, '')       AS nombre_proveedor,
                    r.id_proveedor
                FROM universal_data_core.requisicion r
                LEFT JOIN global_security.usuarios u
                    ON u.PKUsuario = r.PKUsuario
                LEFT JOIN global_security.grupos g
                    ON g.PKgrupo = r.PKgrupo
                LEFT JOIN universal_data_core.ct_proveedores p
                    ON p.id_proveedor = r.id_proveedor
                WHERE r.estado = 1
                ORDER BY r.id_requisicion DESC
            """)
            column_names = [desc[0] for desc in cursor.description]
            requisiciones_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]

        return JsonResponse({'requisiciones': requisiciones_data})

    except Exception as e:
        print(f"Error en obtener_requisiciones_usuario: {str(e)}")
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})
    
# ----------------------------------------------------------------------------------------------------------------- #

def obtener_requisicion_detalles_usuario(request):
    id_requisicion = request.GET.get('id_requisicion')

    if not id_requisicion:
        return JsonResponse({'success': False, 'message': 'Falta el parámetro id_requisicion'})

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:

            # 1. Obtener encabezado de la requisición
            cursor.execute("""
                SELECT
                    r.id_requisicion,
                    COALESCE(u.Nombre, '')           AS Nombre,
                    r.PKUsuario,
                    r.PKgrupo,
                    COALESCE(g.Nombre, '')           AS GrupoNombre,
                    r.id_proveedor,
                    COALESCE(p.nombre_proveedor, '') AS nombre_proveedor
                FROM universal_data_core.requisicion r
                LEFT JOIN global_security.usuarios u  ON u.PKUsuario = r.PKUsuario
                LEFT JOIN global_security.grupos g    ON g.PKgrupo   = r.PKgrupo
                LEFT JOIN universal_data_core.ct_proveedores p ON p.id_proveedor = r.id_proveedor
                WHERE r.id_requisicion = %s
                LIMIT 1
            """, [id_requisicion])
            header = cursor.fetchone()

            if not header:
                return JsonResponse({'success': False, 'message': 'No se encontró la requisición.'})

            grupo_id       = header[3]
            grupo_nombre   = header[4]
            id_proveedor   = header[5]
            nombre_proveedor = header[6]

            # 2. Obtener detalles (artículos) de la requisición
            cursor.execute("""
                SELECT
                    dr.id_detalle_requisicion,
                    dr.id_requisicion,
                    dr.id_suministros,
                    COALESCE(s.nombre, '')  AS nombre_suministro,
                    dr.cantidad,
                    dr.precio_unitario,
                    (dr.cantidad * dr.precio_unitario) AS precio_total
                FROM universal_data_core.detalle_requisicion dr
                LEFT JOIN universal_data_core.suministros s ON s.id_suministros = dr.id_suministros
                WHERE dr.id_requisicion = %s
                ORDER BY dr.id_detalle_requisicion ASC
            """, [id_requisicion])
            rows = cursor.fetchall()

            detalles = []
            for detalle in rows:
                detalles.append({
                    'id_detalle_requisicion': detalle[0],
                    'id_suministros':         detalle[2],
                    'nombre_suministro':      detalle[3],
                    'cantidad':               detalle[4],
                    'precio_unitario':        detalle[5],
                    'precio_total':           detalle[6],
                })

        return JsonResponse({
            'success': True,
            'data': {
                'id_requisicion': id_requisicion,
                'grupo_id':       grupo_id,
                'grupo':          grupo_nombre,
                'id_proveedor':   id_proveedor,
                'proveedor':      nombre_proveedor,
                'detalles':       detalles
            }
        })

    except Exception as e:
        print(f"Error en obtener_requisicion_detalles_usuario: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})


# ----------------------------------------------------------------------------------------------------------------- #

def obtener_metodos_pago(request):
    try:
        # Conexión a la base de datos usando el alias 'ctrlSum' (puedes usar el alias que necesites)
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamamos al procedimiento almacenado 'OBTENER_METODOS_PAGO'
            cursor.callproc('OBTENER_METODOS_PAGO')
            
            # Obtener los resultados del procedimiento almacenado
            column_names = [desc[0] for desc in cursor.description]  # Obtener nombres de columnas
            metodos_pago_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]
            
            # Si hay datos, devolverlos como un JsonResponse
            return JsonResponse({'metodos_pago': metodos_pago_data})
    
    except Exception as e:
        # Manejo de excepciones y errores en la ejecución
        print(f"Error en la ejecución del procedimiento o conexión: {str(e)}")
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})
    
# ----------------------------------------------------------------------------------------------------------------- #

def insertar_actualizar_adquisicion_data(request):
    try:
        existe = 0

        # Valores obtenidos del formulario o petición POST
        id_adquisicion = request.POST.get('id_adquisicion')
        if not id_adquisicion:
            id_adquisicion = None  # Esto permitirá al procedimiento almacenado insertar una nueva requisición 


        id_requisicion = request.POST.get('id_requisicion')
        PKgrupo = request.POST.get('PKgrupo')
        id_proveedor = request.POST.get('id_proveedor')
        fecha_adquisicion = request.POST.get('fecha_adquisicion')
        id_metodo_pago = request.POST.get('id_metodo_pago')
        costo_total = request.POST.get('costo_total')
        estado = request.POST.get('estado')
        userName = request.session.get('userName', '')

        # Conexión a la base de datos
        with transaction.atomic():
            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                args = [
                    id_adquisicion if id_adquisicion else 0,
                    id_requisicion,
                    PKgrupo,
                    id_proveedor,
                    fecha_adquisicion,
                    id_metodo_pago,
                    costo_total,
                    estado,
                    0,         # guardado (valor de salida)
                    userName   # userName (valor adicional)
                ]
                cursor.callproc('universal_data_core.SUM_INSERT_UPDATE_ADQUISICION', args)

                # Obtener el valor del parámetro de salida (guardado)
                cursor.execute('SELECT @_universal_data_core.SUM_INSERT_UPDATE_ADQUISICION_8')
                guardado = cursor.fetchone()[0]

                if guardado == id_adquisicion :
                    existe = 1
        
            udcConn.close()

        datos = {'save': 1, 'id_adquisicion': guardado, 'existe': existe, 'message': 'Requisición procesada correctamente.' }
    
    except Exception as e:
        datos = {'save': 0, 'error': str(e)}

    return JsonResponse(datos)

# ----------------------------------------------------------------------------------------------------------------- #

def insertar_actualizar_detalle_adquisicion_data(request):
    try:
        # Obtenemos el ID de la adquisición y detalles desde el POST
        id_adquisicion = request.POST.get('id_adquisicion')  # Corregido el nombre del campo a 'id_adquisicion'
        id_requisicion = request.POST.get('id_requisicion')
        detalles = json.loads(request.POST.get('detalles'))  # Los detalles se pasan como un JSON

        # Verificar que los detalles no estén vacíos
        if not detalles:
            raise ValueError("No se han agregado detalles para la adquisición.")

        # Validar parámetros requeridos fuera del bucle para mejor diagnóstico
        try:
            id_adq = int(id_adquisicion)
        except (ValueError, TypeError):
            raise ValueError(f"ID Adquisición inválido: '{id_adquisicion}'")

        try:
            id_req = int(id_requisicion)
        except (ValueError, TypeError):
            raise ValueError(f"ID Requisición inválido: '{id_requisicion}'")


        with transaction.atomic():  # Aseguramos que todos los cambios en la base de datos se realicen correctamente
            udcConn = connections['ctrlSum']  # Conexión a la base de datos
            with udcConn.cursor() as cursor:
                # Iteramos sobre los detalles que hemos recibido
                for detalle in detalles:
                    # Validamos que los datos esenciales estén presentes
                    if not detalle.get('id_detalle_requisicion') or not detalle.get('id_suministros') or detalle.get('cantidad') is None or detalle.get('precio_unitario') is None:
                        raise ValueError("Faltan datos en los detalles de la adquisición.")
                    
                    # Validar que cantidad y precio_unitario sean mayores a cero para NUEVOS registros
                    # En edición de registros existentes (id_detalle_adquisicion > 0), se permiten negativos
                    id_da_temp = int(detalle.get('id_detalle_adquisicion', 0))
                    if id_da_temp == 0:
                        if float(detalle.get('cantidad', 0)) <= 0 or float(detalle.get('precio_unitario', 0)) <= 0:
                            raise ValueError("La cantidad y el precio unitario deben ser mayores a cero.")


                    # Convertir a tipos de datos correctos antes de llamar al SP
                    try:
                        id_da = int(detalle.get('id_detalle_adquisicion', 0))
                        id_dr = int(detalle.get('id_detalle_requisicion', 0))
                        id_sum = int(detalle.get('id_suministros', 0))
                        cant = float(detalle.get('cantidad', 0))
                        prec = float(detalle.get('precio_unitario', 0))
                    except (ValueError, TypeError):
                        raise ValueError(f"Formato numérico inválido en detalle: {detalle}")

                    # Llamamos al procedimiento almacenado con los parámetros correspondientes
                    cursor.callproc('SUM_INSERT_UPDATE_DETALLE_ADQUISICION', [
                        id_da,
                        id_adq,
                        id_req,
                        id_dr,
                        id_sum,
                        cant,
                        prec,
                    ])


        # Si todo va bien, retornamos una respuesta de éxito
        datos = {'save': 1, 'message': 'Detalles de adquisición guardados correctamente.'}

    except Exception as e:
        # En caso de error, retornamos el mensaje de error
        datos = {'save': 0, 'error': f'⚠️ Error: {str(e)}'}

    return JsonResponse(datos)

# ----------------------------------------------------------------------------------------------------------------- #

def actualizar_estado_adquisicion(request):
    if request.method == "POST":
        adquisicion_id = request.POST.get('id_adquisicion')
        estadoAd = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not adquisicion_id or not estadoAd:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_ADQUISICION', [adquisicion_id, estadoAd])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# ----------------------------------------------------------------------------------------------------------------- #

def obtener_adquisicion_y_detalle_data(request):
    # Obtener el ID de la adquisición desde la solicitud
    id_adquisicion = request.GET.get('id_adquisicion')

    if not id_adquisicion:
        return JsonResponse({'error': 'No se proporcionó un ID de adquisición válido.'})

    try:
        # Conectar a la base de datos y ejecutar el procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamar al procedimiento almacenado que obtiene la adquisición y los detalles
            cursor.callproc('GET_ADQUISICION_Y_DETALLES', [id_adquisicion])
            
            # Obtener los resultados de la adquisición
            column_names = [desc[0] for desc in cursor.description]
            adquisicion_data = dict(zip(column_names, cursor.fetchone()))  # solo un resultado para la adquisición

            # Obtener los resultados de los detalles de la adquisición
            cursor.nextset()  # Mover al siguiente conjunto de resultados (detalles)
            column_names = [desc[0] for desc in cursor.description]
            detalles_adquisicion = [
                dict(zip(column_names, row)) for row in cursor.fetchall()
            ]
        
        # Retornar la respuesta en formato JSON con los datos de la adquisición y los detalles
        return JsonResponse({
            'adquisicion': adquisicion_data,
            'detalles': detalles_adquisicion
        })

    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})
    
# ----------------------------------------------------------------------------------------------------------------- #

# Obtiene los datos de la tabla Adquisicion
def obtener_detalle_adquisicion(request):
    if request.method == 'POST':
        # Obtener los parámetros del POST
        id_adquisicion = request.POST.get('id_adquisicion')
        id_requisicion = request.POST.get('id_requisicion')

        # Llamada al procedimiento almacenado
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc('universal_data_core.OBTENER_DETALLE_ADQUISICION', [id_adquisicion, id_requisicion])
            
            # Obtener nombres de columnas dinámicamente
            if cursor.description:
                columns = [col[0].lower() for col in cursor.description]
                results = cursor.fetchall()
                
                # Deduplicar resultados si el SP devuelve filas idénticas
                unique_results = list(dict.fromkeys(results)) # dict.fromkeys preserva el orden
                
                detalles = []
                for row in unique_results:
                    d = dict(zip(columns, row))
                    # Normalizar nombres de campos para el frontend
                    # Estricto: Solo usar IDs de detalle reales (pk_detalle_requisicion o id_detalle_requisicion)
                    # SE ELIMINAN: fkrequisicion e id_requisicion para evitar errores de llave foránea
                    id_det_req = d.get('pk_detalle_requisicion') or d.get('id_detalle_requisicion') or d.get('fk_detalle_requisicion')
                    
                    if id_det_req:
                        detalle_mapeado = {
                            'id_adquisicion': d.get('pkadquisicion') or d.get('id_adquisicion') or d.get('pk_adquisicion', id_adquisicion),
                            'id_detalle_requisicion': id_det_req,
                            'id_suministros': d.get('fk_suministros') or d.get('id_suministros'),
                            'nombre_suministro': d.get('nombre_suministro') or d.get('nombresuministro') or d.get('nombre', 'N/A'),
                            'cantidad': d.get('cantidad', 0),
                            'precio_unitario': d.get('precio_unitario', 0),
                            'precio_total': d.get('precio_total', 0),
                            'estado': d.get('estado', 'ACTIVO')
                        }
                        detalles.append(detalle_mapeado)
            else:
                detalles = []

        # Si no se encuentran resultados, devolver un error
        if not detalles:
            return JsonResponse({'success': False, 'message': 'No se encontraron detalles para esta adquisición.'})

        return JsonResponse({'success': True, 'data': detalles})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

# --------------------------------------- SECCION DE ALMACENES  ------------------------------------------------ #

def listado_devoluciones_data(request):
    
    devoluciones_data = ""

    try:
        # TOMA LOS DATOS DE LA TABLA ALMACEN
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("GET_DEVOLUCIONES", [0])
            column_names = [desc[0] for desc in cursor.description]
            devoluciones_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "devoluciones": devoluciones_data,
    }
    
    return render(request, 'suministros/listado_devolucion.html', context)

#-----------------------------------------------------------------------------------------------------#

# Insertar y Actualizar Devolución
def insertar_actualizar_devolucion_data(request):
    try:
        existe = 0

        # Obtener los datos del formulario
        id_devolucion = request.POST.get('id_devolucion')
        if not id_devolucion:
            id_devolucion = None  # Esto permitirá al procedimiento almacenado insertar una nueva requisición 

        IDadquisicion = request.POST.get('id_adquisicion')
        IDDetalleRequisicion = request.POST.get('id_detalle_requisicion')
        IDsuministros = request.POST.get('id_suministros')
        cantidad_devuelta = request.POST.get('cantidad_devuelta')
        precioUnitario = request.POST.get('precio_unitario')
        fecha_devolucion = request.POST.get('fecha_devolucion')
        id_motivo_devolucion = request.POST.get('id_motivo_devolucion')
        motivo_devolucion = request.POST.get('motivo_devolucion')
        IDproveedor = request.POST.get('id_proveedor')
        total_devolucion = request.POST.get('total_devolucion')
        estado = request.POST.get('estado')  # Estado de la devolución (1 = Creado, 2 = Editado, 3 = Anulado)

        # Obtener el nombre del usuario desde la sesión
        userName = request.session.get('userName', '')

        # Conexión a la base de datos
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamar al procedimiento almacenado
            cursor.callproc('universal_data_core.SUM_INSERT_UPDATE_DEVOLUCION', [
                id_devolucion,
                IDadquisicion,
                IDDetalleRequisicion,
                IDsuministros,
                cantidad_devuelta,
                precioUnitario,
                total_devolucion,
                fecha_devolucion,
                id_motivo_devolucion,
                motivo_devolucion,
                IDproveedor,
                estado,
                0,  # Parámetro OUT (guardado)
                userName
            ])

            # Obtener el valor del parámetro OUT (guardado)
            cursor.execute('SELECT @_universal_data_core.SUM_INSERT_UPDATE_DEVOLUCION_12')
            guardado = cursor.fetchone()[0]

            # Definir el estado de la operación
            if guardado == 1:
                existe = 0  # Indica que se insertó un nuevo registro
            else:
                existe = 2  # Indica que se actualizó un registro existente
        
        # Cerrar la conexión
        udcConn.close()

        # Retornar la respuesta como JSON
        datos = {'save': 1, 'existe': existe}
    except Exception as e:
        datos = {'save': 0, 'error': str(e)}
    
    return JsonResponse(datos)

#-----------------------------------------------------------------------------------------------------#

# Obtiene los datos de la tabla devolucion
def get_devoluciones_data (request):
    varEstado = int(request.POST.get('varEstado'))  # Convertir a entero, por defecto es 0
    devoluciones_data = ''

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("GET_DEVOLUCIONES", [varEstado])
            column_names = [desc[0] for desc in cursor.description]
            devoluciones_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]
        
        udcConn.close()
        
        return JsonResponse({'data': devoluciones_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})
  
#-----------------------------------------------------------------------------------------------------#  
def actualizar_estado_devolucion(request):
    if request.method == "POST":
        devolucion_id = request.POST.get('id_devolucion')
        estadoDev = request.POST.get('estado')  # Obtener el estado nuevo

        # Validación de los parámetros
        if not devolucion_id or not estadoDev:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros requeridos.'})

        try:
            # Llamamos al procedimiento almacenado para actualizar el estado de la requisición
            udcConn = connections['ctrlSum']  # Usa la conexión correcta para la base de datos
            with udcConn.cursor() as cursor:
                cursor.callproc('ACTUALIZAR_ESTADO_DEVOLUCION', [devolucion_id, estadoDev])

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
#-----------------------------------------------------------------------------------------------------#

def obtener_motivos_devoluciones_data(request):
    try:
        # Conexión a la base de datos usando el alias 'ctrlSum' (puedes usar el alias que necesites)
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # Llamamos al procedimiento almacenado 'OBTENER_METODOS_PAGO'
            cursor.callproc('OBTENER_MOTIVOS_DEVOLUCIONES')
            
            # Obtener los resultados del procedimiento almacenado
            column_names = [desc[0] for desc in cursor.description]  # Obtener nombres de columnas
            motivoD_data = [
                dict(zip(map(str, column_names), row)) for row in cursor.fetchall()
            ]
            
            # Si hay datos, devolverlos como un JsonResponse
            return JsonResponse({'motivoD': motivoD_data})
    
    except Exception as e:
        # Manejo de excepciones y errores en la ejecución
        print(f"Error en la ejecución del procedimiento o conexión: {str(e)}")
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'})

#-----------------------------------------------------------------------------------------------------#
def movimientos_suministros_data(request):

    categorias_data = ""

    try:
        # TOMA LOS DATOS DE LA TABLA CATEGORIAS PARA EL SELECT CATEGORIAS DEL HTML
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.callproc("SUM_GET_CATEGORIAS", [])
            column_names = [desc[0] for desc in cursor.description]
            categorias_data = [dict(zip(map(str, column_names), row)) for row in cursor.fetchall()]

        # Cierra la conexión
        udcConn.close()

    except Exception as e:
        # Manejo de excepciones, puedes personalizar esto según tus necesidades
        return JsonResponse({'error': str(e)})
    
    context = {
        "categorias": categorias_data,
    }
    
    return render(request, 'suministros/kardex_suministros.html', context)

#-----------------------------------------------------------------------------------------------------# 

def convertir_a_int(valor):
    try:
        if valor is None or str(valor).strip() == "" or str(valor) == "undefined":
            return None
        return int(valor)
    except (ValueError, TypeError):
        return None

def historial_suministros_data(request):
    try:
        id_recibido = request.POST.get('id_suministro') or request.POST.get('id_suministros') or request.GET.get('id_suministro') or request.GET.get('id_suministros')
        id_categoria = request.POST.get('id_categoria') or request.GET.get('id_categoria')
        fecha_desde = request.POST.get('fecha_desde') or request.GET.get('fecha_desde')
        fecha_hasta = request.POST.get('fecha_hasta') or request.GET.get('fecha_hasta')

        id_suministro = convertir_a_int(id_recibido)
        id_categoria = convertir_a_int(id_categoria)

        if not fecha_desde or str(fecha_desde).strip() == '' or str(fecha_desde) == 'undefined':
            fecha_desde = None
        if not fecha_hasta or str(fecha_hasta).strip() == '' or str(fecha_hasta) == 'undefined':
            fecha_hasta = None

        print("========== DEBUG KARDEX ==========")
        print(f"id_categoria: {id_categoria}")
        print(f"id_suministro: {id_suministro}")
        print(f"fecha_desde: {fecha_desde}")
        print(f"fecha_hasta: {fecha_hasta}")

        if id_suministro is None and id_categoria is None and fecha_desde is None and fecha_hasta is None:
            print("DEBUG: Todos los filtros están vacíos, retornando vacío")
            return JsonResponse({'success': True, 'data': []})

        # NUEVO: si hay suministro, no filtrar por fechas
        if id_suministro is not None:
            fecha_desde = None
            fecha_hasta = None

        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            if id_suministro:
                cursor.execute(
                    "SELECT COUNT(*) FROM universal_data_core.suministros_movimientos WHERE id_suministros = %s",
                    [id_suministro]
                )
                count = cursor.fetchone()[0]
                print(f"DEBUG: Movimientos encontrados para suministro {id_suministro}: {count}")
            
            cursor.callproc('OBTENER_HISTORIAL_KARDEX', [
                id_categoria,
                id_suministro,
                fecha_desde,
                fecha_hasta
            ])
            result = cursor.fetchall()
            columnas = [col[0] for col in cursor.description]
            
            print(f"DEBUG: SP retornó {len(result)} filas")
            print(f"DEBUG: Columnas: {columnas}")
            if result:
                print(f"DEBUG: Primera fila: {result[0]}")
            # Obtener mapeo de usuarios responsables desde la tabla de movimientos
            cursor.execute(
                "SELECT fecha_movimiento, detalle_movimiento, creado_por FROM universal_data_core.suministros_movimientos WHERE id_suministros = %s",
                [id_suministro]
            )
            mapa_usuarios = {}
            for r_user in cursor.fetchall():
                # Creamos una llave compuesta por fecha (YYYY-MM-DD) y detalle
                f_key = (str(r_user[0]).split(' ')[0], r_user[1])
                mapa_usuarios[f_key] = r_user[2]

            # --- SONDA DE DIAGNOSTICO PARA EL USUARIO ---
            with open('check_db_results.txt', 'w') as f_debug:
                f_debug.write(f"REPORTE DE DATOS CRUDOS EN BD (Suministro {id_suministro})\n")
                f_debug.write("-" * 50 + "\n")
                for key, val in mapa_usuarios.items():
                    f_debug.write(f"Fecha: {key[0]} | Detalle: {key[1]} | Usuario en BD: [{val}]\n")
            # --------------------------------------------

            data = []
            for row in result:
                item = dict(zip(columnas, row))
                
                orig_fecha = str(item.get('fecha_movimiento', ''))
                orig_detalle = item.get('detalle_movimiento', '')

                # Normalizar fecha para el retorno
                if item.get('fecha_movimiento'):
                    item['fecha_movimiento'] = orig_fecha.split(' ')[0]
                
                if 'costo_total' in item and item['costo_total'] is not None:
                    item['costo_total'] = abs(float(item['costo_total']))

                # ENRIQUECIMIENTO: Inyectar el usuario buscando en el mapa generado
                # Si no se encuentra de forma exacta, intentamos con lo que venga del SP o vacío
                search_key = (orig_fecha.split(' ')[0], orig_detalle)
                item['creado_por'] = mapa_usuarios.get(search_key) or item.get('creado_por') or ''
                
                data.append(item)

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
#-----------------------------------------------------------------------------------------------------# 
# --OBTENER MOVIMIENTO POR SUMINISTRO

def obtener_movimientos_x_suministro(request):
    if request.method == 'POST': 
        try:
            # Capturamos el ID del suministro
            suministro_id = request.POST.get('id_suministros') or request.POST.get('suministro_id')

            if not suministro_id:
                return JsonResponse({'success': False, 'error': 'Falta el ID del suministro.'}, status=400)

            # Usamos int() estándar de Python, sin funciones raras
            suministro_id = int(suministro_id)

            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                # Llamamos a tu procedimiento actualizado
                cursor.callproc('universal_data_core.OBTENER_MOVIMIENTO_X_SUMINISTRO', [suministro_id])
                result = cursor.fetchall()
                # Esto detecta los nombres de columnas de MySQL automáticamente
                columns = [col[0] for col in cursor.description]

            if not result:
                return JsonResponse({'success': False, 'error': 'No hay movimientos registrados.'})

            # Formateamos los datos para enviarlos al navegador
            movimientos = [dict(zip(columns, row)) for row in result]

            return JsonResponse({'success': True, 'data': movimientos})

        except Exception as e:
            # Si algo falla, esto nos dirá qué es en la consola
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

# <----GRUPOS_SUMINISTROS
def get_grupos_data(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id_grupo AS id,
                    nombre_grupo AS nombre
                FROM universal_data_core.grupos
                ORDER BY nombre_grupo
            """)
            rows = cursor.fetchall()

        data = [{"id": r[0], "nombre": r[1]} for r in rows]
        return JsonResponse({"data": data})

    except Exception as e:
        return JsonResponse({"data": [], "error": str(e)}, status=500)
 # <--area data      

def get_areas_data(request):
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            cursor.execute("""
                SELECT PKgrupo, Nombre
                FROM global_security.grupos
                ORDER BY Nombre
            """)
            areas = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]

        return JsonResponse({"success": True, "data": areas})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def buscar_sistema(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        try:
            udcConn = connections['ctrlSum']
            with udcConn.cursor() as cursor:
                # Buscar en Suministros
                cursor.execute("""
                    SELECT id_suministros, nombre, 'Suministro' as tipo
                    FROM universal_data_core.suministros
                    WHERE nombre LIKE %s OR descripcion LIKE %s
                    LIMIT 5
                """, [f'%{query}%', f'%{query}%'])
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'text': row[1],
                        'type': row[2],
                        'url': reverse('listado_suministro_data')
                    })

                # Buscar en Requisiciones
                cursor.execute("""
                    SELECT id_requisicion, CONCAT('Requisición #', CAST(id_requisicion AS CHAR)), 'Requisición' as tipo
                    FROM universal_data_core.requisicion
                    WHERE CAST(id_requisicion AS CHAR) LIKE %s
                    LIMIT 5
                """, [f'%{query}%'])
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'text': row[1],
                        'type': row[2],
                        'url': reverse('listado_requisicion_data')
                    })
        except Exception as e:
            print("Error en búsqueda:", e)

    return JsonResponse({'results': results})

def configuracion_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))
        
    userName = request.session.get('userName', 'USUARIO')
    return render(request, 'configuracion.html', {'userName': userName})

def perfil_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))
        
    userName = request.session.get('userName', 'USUARIO')
    fullName = request.session.get('fullName', 'Usuario del Sistema')
    empresa = request.session.get('empresa', 'Compañía')
    
    # Intentar obtener los últimos datos de la base de datos
    try:
        with connections['global_nube'].cursor() as cursor:
            cursor.execute("SELECT Nombre, Usuario FROM usuarios WHERE PKUsuario = %s", [user_id])
            row = cursor.fetchone()
            if row:
                fullName = row[0]
                userName = row[1]
                # Actualizar sesión con los datos frescos
                request.session['fullName'] = fullName
                request.session['userName'] = userName
    except Exception as e:
        print(f"Error fetching updated user profile: {e}")
    
    return render(request, 'perfil.html', {
        'userName': userName,
        'fullName': fullName,
        'empresa': empresa
    })

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def actualizar_perfil(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'No autenticado'})
            
        full_name = request.POST.get('fullName')
        user_name = request.POST.get('userName')
        empresa = request.POST.get('empresa')
        
        try:
            with connections['global_nube'].cursor() as cursor:
                # Actualizar Nombre y Usuario en la tabla principal
                cursor.execute("""
                    UPDATE usuarios 
                    SET Nombre = %s, Usuario = %s 
                    WHERE PKUsuario = %s
                """, [full_name, user_name, user_id])
                
                # Para la empresa, comprobamos si la columna Empresa_Nombre existe
                try:
                    cursor.execute("""
                        UPDATE usuarios 
                        SET Empresa_Nombre = %s 
                        WHERE PKUsuario = %s
                    """, [empresa, user_id])
                except Exception as ex:
                    # Si la columna no existe o falla, ignorar el error SQL y crearla
                    try:
                        cursor.execute("ALTER TABLE usuarios ADD Empresa_Nombre VARCHAR(255) NULL")
                        cursor.execute("""
                            UPDATE usuarios 
                            SET Empresa_Nombre = %s 
                            WHERE PKUsuario = %s
                        """, [empresa, user_id])
                    except Exception as e_col:
                        print(f"No se pudo guardar empresa en BD: {e_col}")
                        
            # Actualizar la sesión para que se refleje de inmediato
            request.session['fullName'] = full_name
            request.session['userName'] = user_name
            request.session['empresa'] = empresa
            
            return JsonResponse({'success': True, 'message': 'Perfil actualizado correctamente'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar: {str(e)}'})
            
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def subir_foto_perfil(request):
    from django.conf import settings
    from django.core.files.storage import FileSystemStorage
    try:
        if request.method == 'POST' and request.FILES.get('avatar'):
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'success': False, 'message': 'No autenticado'})
                
            avatar = request.FILES['avatar']
            
            # Validación de tipo de archivo
            extension = avatar.name.split('.')[-1].lower()
            if extension not in ['jpg', 'jpeg', 'png']:
                return JsonResponse({'success': False, 'message': 'Formato no válido. Solo JPG y PNG permitidos.'})
                
            # Validación de tamaño (< 2MB)
            if avatar.size > 2 * 1024 * 1024:
                return JsonResponse({'success': False, 'message': 'La imagen excede el límite de 2MB.'})
                
            import time
            
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'user_avatars'))
            
            filename = f'user_{user_id}_{int(time.time())}.{extension}'
            
            saved_name = fs.save(filename, avatar)
            avatar_url = f"{settings.MEDIA_URL}user_avatars/{saved_name}"
            
            # Guardar en base de datos
            with connections['global_nube'].cursor() as cursor:
                try:
                    cursor.execute("""
                        UPDATE usuarios SET Avatar = %s WHERE PKUsuario = %s
                    """, [avatar_url, user_id])
                except Exception:
                    # Si la columna no existe, crearla y luego actualizar
                    cursor.execute("ALTER TABLE usuarios ADD Avatar VARCHAR(255) NULL")
                    cursor.execute("""
                        UPDATE usuarios SET Avatar = %s WHERE PKUsuario = %s
                    """, [avatar_url, user_id])
                        
            request.session['avatar_url'] = avatar_url
            return JsonResponse({'success': True, 'avatar_url': avatar_url})
            
        return JsonResponse({'success': False, 'message': 'Petición inválida o sin imagen'})
    except Exception as e:
        import traceback
        return JsonResponse({'success': False, 'message': f'EXCEPCIÓN INTERNA: {str(e)} | Traza: {traceback.format_exc()}'})


def obtener_notificaciones_sistema(request):
    notifications = []
    user_id = request.session.get('user_id')
    
    if not user_id:
        return JsonResponse({'notifications': []}, status=200)

    # Identificadores de notificaciones ya vistas en esta sesión
    vistas = request.session.get('notificaciones_vistas', [])

    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # 1. Stock Bajo
            try:
                cursor.callproc("OBTENER_STOCK_BAJOS", [])
                results = cursor.fetchall()
                if results and cursor.description:
                    column_names = [desc[0] for desc in cursor.description]
                    stock_bajo = [dict(zip(column_names, row)) for row in results]
                    
                    for item in stock_bajo:
                        stock = item.get('stock', 0)
                        stock_min = item.get('stockMinimo', 1)
                        # PKsuministro es el ID único en la tabla suministros
                        pk_sum = item.get('PKsuministro') or item.get('id_suministros')
                        nombre = item.get('nombre', 'Suministro')
                        
                        try:
                            s_val = float(stock) if stock is not None else 0
                            sm_val = float(stock_min) if stock_min is not None else 1
                        except:
                            s_val, sm_val = 0, 1

                        notif_id = f"stock_{pk_sum}"
                        notifications.append({
                            'id': notif_id,
                            'type': 'stock_bajo',
                            'title': nombre,
                            'message': f"Stock bajo: {stock} (Mín: {stock_min})",
                            'url': reverse('listado_suministro_data') + f"?id={pk_sum}&name={nombre}",
                            'severity': 'danger' if s_val <= (sm_val * 0.5) else 'warning',
                            'is_new': notif_id not in vistas
                        })
                
                while cursor.nextset(): pass
            except Exception as e_stock:
                print(f"Error en notificaciones de stock: {str(e_stock)}")

            # 2. Requisiciones Pendientes (Estado 1)
            try:
                cursor.callproc("GET_REQUISICIONES", [1])
                results_req = cursor.fetchall()
                if results_req and cursor.description:
                    column_names = [desc[0] for desc in cursor.description]
                    requisiciones = [dict(zip(column_names, row)) for row in results_req]
                    
                    if requisiciones:
                        # Usamos un ID que cambie si cambia el número de requisiciones o el ID más reciente
                        last_id = requisiciones[0].get('id_requisicion', 0)
                        notif_id = f"req_pendientes_{len(requisiciones)}_{last_id}"
                        
                        notifications.append({
                            'id': notif_id,
                            'type': 'requisiciones',
                            'title': 'Requisiciones Pendientes',
                            'message': f"Hay {len(requisiciones)} requisiciones esperando su gestión.",
                            'url': reverse('listado_requisicion_data'),
                            'severity': 'info',
                            'is_new': notif_id not in vistas
                        })
                
                while cursor.nextset(): pass
            except Exception as e_req:
                print(f"Error en notificaciones de requisiciones: {str(e_req)}")

        # Ordenar por 'is_new' primero
        notifications.sort(key=lambda x: x['is_new'], reverse=True)

        return JsonResponse({'notifications': notifications}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def marcar_notificaciones_vistas(request):
    """Marca las notificaciones actuales como vistas guardando sus IDs en la sesión."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            
            vistas = request.session.get('notificaciones_vistas', [])
            # Combinar IDs nuevos con los ya existentes (evitando duplicados)
            vistas = list(set(vistas + ids))
            request.session['notificaciones_vistas'] = vistas
            request.session.modified = True
            
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def notificaciones_page_view(request):
    """Vista para mostrar todas las notificaciones en una página dedicada."""
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    userName = request.session.get('userName', 'Usuario')
    notifications = []
    
    # Reutilizamos la lógica de obtención pero para renderizar en el server
    try:
        udcConn = connections['ctrlSum']
        with udcConn.cursor() as cursor:
            # 1. Stock Bajo
            cursor.callproc("OBTENER_STOCK_BAJOS", [])
            results = cursor.fetchall()
            if results and cursor.description:
                cols = [desc[0] for desc in cursor.description]
                for row in results:
                    item = dict(zip(cols, row))
                    pk_sum = item.get('PKsuministro') or item.get('id_suministros')
                    stock = item.get('stock') if item.get('stock') is not None else 0
                    stock_min = item.get('stockMinimo') if item.get('stockMinimo') is not None else 0
                    
                    nombre_notif = item.get('nombre', 'Suministro')
                    notifications.append({
                        'id': f"stock_{pk_sum}",
                        'type': 'stock_bajo',
                        'title': nombre_notif,
                        'message': f"Stock bajo en inventario: {stock} (Mín: {stock_min})",
                        'url': reverse('listado_suministro_data') + f"?id={pk_sum}&name={nombre_notif}",
                        'severity': 'danger' if float(stock) <= (float(stock_min or 1) * 0.5) else 'warning',
                        'fecha': datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
            while cursor.nextset(): pass

            # 2. Requisiciones
            cursor.callproc("GET_REQUISICIONES", [1])
            results_req = cursor.fetchall()
            if results_req and cursor.description:
                cols_req = [desc[0] for desc in cursor.description]
                for row in results_req:
                    item = dict(zip(cols_req, row))
                    req_id = item.get('id_requisicion')
                    notifications.append({
                        'id': f"req_{req_id}",
                        'type': 'requisiciones',
                        'title': f"Requisición #{req_id}",
                        'message': "Nueva solicitud de suministro pendiente de gestión.",
                        'url': reverse('listado_requisicion_data') + f"?id={req_id}",
                        'severity': 'info',
                        'fecha': item.get('fecha_hora_creacion') or datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
            while cursor.nextset(): pass

    except Exception as e:
        print(f"Error cargando página de notificaciones: {e}")

    # Marcar todas como vistas al entrar a la página
    all_ids = [n['id'] for n in notifications]
    vistas = request.session.get('notificaciones_vistas', [])
    request.session['notificaciones_vistas'] = list(set(vistas + all_ids))
    request.session.modified = True

    return render(request, 'notificaciones_sistema.html', {
        'notifications': notifications,
        'userName': userName,
        'count': len(notifications)
    })
