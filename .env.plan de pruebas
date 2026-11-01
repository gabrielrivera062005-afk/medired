# Plan de pruebas de MEDIRED

Elaborado por Gabriel Esteban Rivera Orjuela. Gestión de Proyectos, Ingeniería en Ciencia de Datos, Politécnico Gran Colombiano. Noviembre de 2026.

## 1. Objetivo

Comprobar que el prototipo de MEDIRED hace lo que promete: consultar medicamentos y su disponibilidad por sede, registrar movimientos de inventario con trazabilidad, gestionar solicitudes de medicamentos con su entrega y avisar cuando el stock está bajo.

## 2. Alcance

Se prueba la base de datos (esquema, datos de prueba, triggers y vista), la API hecha con FastAPI y la interfaz web.

No se prueba el inicio de sesión y los roles, las reservas de stock, el rendimiento con muchos usuarios ni la seguridad. Todos los datos son sintéticos.

## 3. Entorno de pruebas

| Componente | Detalle |
| --- | --- |
| Base de datos | PostgreSQL con el esquema `medired`. Se cargan `schema.sql`, `seed synthetic.sql` y `fix_sequences.sql`, en ese orden |
| Backend | Python 3 con FastAPI. Se enciende con `uvicorn app:app --reload` y se prueba en http://localhost:8000/docs (Swagger UI) |
| Frontend | `frontend/index.html`. Con el backend encendido se abre desde http://localhost:5500 usando `python -m http.server 5500` |
| Navegador | Chrome o Brave |
| Repositorio | https://github.com/ramosnova977-droid/medired |

## 4. Tipos de prueba

- **Base de datos:** que el esquema, los datos de prueba, los triggers y la vista funcionen.
- **Funcionales de la API:** cada endpoint se prueba en Swagger UI con datos válidos.
- **Validación de errores:** datos inválidos, registros que no existen y reglas de negocio.
- **Interfaz:** recorrido manual de cada pantalla.

## 5. Datos de referencia

Valores que deben salir después de cargar el seed en una base limpia.

| Dato | Valor |
| --- | --- |
| Medicamento 1 | Acetaminofén 500 mg |
| Acetaminofén en Sede Chapinero (sede 1) | 103 unidades, mínimo 20 (disponible) |
| Acetaminofén en Sede Usaquén (sede 5) | 156 unidades, mínimo 80 (bajo) |
| Acetaminofén en Sede Ciudad Bolívar (sede 9) | 15 unidades, mínimo 30 (crítico) |
| Acetaminofén en Sede Fontibón (sede 7) | 0 unidades, mínimo 30 (no disponible) |
| Sede Suba | id 3 |
| Totales | 12 sedes, 20 medicamentos, 197 registros de inventario, 10 pacientes |
| Solicitudes del seed | 25 en total, 9 pendientes |
| Alertas que genera el seed | 54 agotado y 78 stock crítico |

Ejecuta los casos en el orden de las tablas. Varios cambian el stock y los siguientes parten de ese valor. Para repetir todo, recarga `schema.sql`, el seed y `fix_sequences.sql`.

## 6. Casos de prueba

Las columnas Resultado obtenido y Estado se llenan al ejecutar cada caso (Aprobado o Fallido).

### 6.1 Base de datos

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| BD-01 | Ejecutar `schema.sql` en el Query Tool de pgAdmin y listar las tablas del esquema `medired` | Sin errores. Aparecen 12 tablas y la vista `vw_disponibilidad` |  | Pendiente |
| BD-02 | Ejecutar `seed synthetic.sql` y contar las filas de cada tabla | eps 1, sede 12, medicamento 20, usuario 13, inventario 197, movimiento\_inventario 595, solicitud 25, detalle\_solicitud 25, entrega 9 |  | Pendiente |
| BD-03 | Consultar `SELECT estado, COUNT(*) FROM medired.vw_disponibilidad GROUP BY estado` | disponible 123, bajo 25, critico 24, no\_disponible 25 |  | Pendiente |
| BD-04 | Consultar `SELECT tipo, COUNT(*) FROM medired.alerta GROUP BY tipo` | agotado 54 y stock\_critico 78. Las crea el trigger al cargar el seed |  | Pendiente |
| BD-05 | Insertar una salida de 999999 unidades: `INSERT INTO medired.movimiento_inventario (id_inventario, tipo_movimiento, cantidad, stock_anterior, stock_nuevo) VALUES (1, 'salida', 999999, 0, 0)` | Error: Salida (999999) supera el stock disponible (103) en inventario 1. El stock sigue en 103 |  | Pendiente |
| BD-06 | Antes de `fix_sequences.sql`, ejecutar `SELECT nextval('medired.solicitud_id_solicitud_seq')`. Luego ejecutar el archivo y repetir la consulta | Antes devuelve 1, un id que ya existe. Después devuelve un número mayor a 25 |  | Pendiente |

### 6.2 API general y medicamentos

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| GEN-01 | GET `/` | 200 con status ok y servicio MEDIRED API |  | Pendiente |
| GEN-02 | Abrir http://localhost:8000/docs | Swagger UI con los endpoints de medicamentos, sedes, inventario, solicitudes y alertas |  | Pendiente |
| MED-01 | GET `/api/medicamentos?q=acetaminofen` | 200 y la lista incluye Acetaminofén 500 mg (id 1) |  | Pendiente |
| MED-02 | GET `/api/medicamentos` | 200 con los medicamentos del catálogo (el seed trae 20) |  | Pendiente |
| MED-03 | GET `/api/medicamentos/1` | 200 con Acetaminofén, tableta, 500 mg, vía oral |  | Pendiente |
| MED-04 | GET `/api/medicamentos/9999` | 404 |  | Pendiente |
| MED-05 | POST `/api/medicamentos` con nombre, principio\_activo y forma\_farmaceutica | Se crea y la respuesta trae el id nuevo. Necesita haber ejecutado `fix_sequences.sql` |  | Pendiente |
| MED-06 | POST `/api/medicamentos` sin el campo nombre | 422 |  | Pendiente |

### 6.3 Sedes

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| SED-01 | GET `/api/sedes` | 200 con las 12 sedes activas |  | Pendiente |
| SED-02 | GET `/api/sedes?localidad=Suba` | 200 con una sola sede: Sede Suba (id 3) |  | Pendiente |
| SED-03 | GET `/api/sedes/1` | 200 con Sede Chapinero |  | Pendiente |
| SED-04 | GET `/api/sedes/9999` | 404 Sede no encontrada |  | Pendiente |

### 6.4 Inventario y movimientos

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| INV-01 | GET `/api/inventario/1` | 200 con 10 sedes, de mayor a menor stock. Chapinero 103 disponible, Usaquén 156 bajo, Puente Aranda 25 crítico, Ciudad Bolívar 15 crítico, Fontibón 0 no disponible |  | Pendiente |
| INV-02 | GET `/api/inventario/9999` | 404 Medicamento no encontrado |  | Pendiente |
| INV-03 | POST `/api/inventario/entrada` con medicamento 1, sede 1 y cantidad 10 | 201. El stock nuevo es el anterior más 10 (en base limpia, de 103 a 113) |  | Pendiente |
| INV-04 | POST `/api/inventario/salida` con medicamento 1, sede 1 y cantidad 5 | 201. El stock nuevo es el anterior menos 5 (después de INV-03, de 113 a 108) |  | Pendiente |
| INV-05 | POST `/api/inventario/salida` con medicamento 1, sede 1 y cantidad 999999 | 400 con el mensaje Salida (999999) supera el stock disponible. Requiere el cambio de DEF-02 |  | Pendiente |
| INV-06 | POST `/api/inventario/entrada` con cantidad 0 | 422 |  | Pendiente |
| INV-07 | POST `/api/inventario/entrada` con id\_sede 9999 | 404 No existe registro de inventario para ese medicamento en esa sede |  | Pendiente |
| INV-08 | GET `/api/inventario/movimientos/1` | 200 con los movimientos del más reciente al más antiguo. Los dos primeros son la salida de 5 y la entrada de 10 |  | Pendiente |

### 6.5 Solicitudes y entregas

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| SOL-01 | GET `/api/solicitudes/pacientes` | 200 con 10 pacientes |  | Pendiente |
| SOL-02 | GET `/api/solicitudes` y luego `?estado=pendiente` | 25 solicitudes y 9 pendientes en base limpia |  | Pendiente |
| SOL-03 | GET `/api/solicitudes/1` y GET `/api/solicitudes/9999` | El primero devuelve el detalle con sus medicamentos. El segundo, 404 |  | Pendiente |
| SOL-04 | POST `/api/solicitudes` con usuario 1, sede 1, domicilio, medicamento 1 y cantidad 5 | 201, estado pendiente. En base limpia el id es 26. Necesita `fix_sequences.sql` |  | Pendiente |
| SOL-05 | PATCH `/api/solicitudes/{id}/estado` con entregada sobre la solicitud pendiente | 400: No se puede pasar de 'pendiente' a 'entregada' |  | Pendiente |
| SOL-06 | PATCH con autorizada | 200. Se crea la entrega en estado autorizada, la cantidad autorizada es 5 y el stock no cambia |  | Pendiente |
| SOL-07 | PATCH con preparando y luego con entregada | 400: Una entrega a domicilio debe pasar por 'en\_camino' |  | Pendiente |
| SOL-08 | PATCH con en\_camino y luego con entregada | 200. Queda la fecha de entrega real, el stock del medicamento 1 en Sede Chapinero baja 5 y existe un movimiento de salida ligado a la solicitud |  | Pendiente |
| SOL-09 | PATCH con cancelada sobre la solicitud ya entregada | 400 |  | Pendiente |
| SOL-10 | Crear una solicitud para recoger en sede (usuario 2, sede 2, medicamento 2, cantidad 1), autorizarla, prepararla y pedir en\_camino | 400: Una solicitud para recoger en sede no pasa por 'en\_camino'. Luego entregada da 200 |  | Pendiente |
| SOL-11 | Crear una solicitud con cantidad 999999 e intentar autorizarla. Después cancelarla | La autorización da 400 con Stock insuficiente en la sede y sigue pendiente. La cancelación da 200 |  | Pendiente |
| SOL-12 | Crear con usuario 999, con lista de medicamentos vacía y con cantidad 0 | 404, 422 y 422 |  | Pendiente |

### 6.6 Alertas

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| ALE-01 | GET `/api/alertas?atendida=false&limit=5` | 200 con 5 alertas, primero las de tipo agotado |  | Pendiente |
| ALE-02 | GET `/api/alertas/resumen` | agotado 54 y stock\_critico 78 en base limpia. Pueden ser más si los movimientos anteriores dejaron stock bajo |  | Pendiente |
| ALE-03 | PATCH `/api/alertas/{id}/atender` dos veces y con el id 999999 | La primera da 200 con atendida verdadera. La segunda da 400: Esta alerta ya estaba atendida. El id 999999 da 404 |  | Pendiente |

### 6.7 Interfaz web

| ID | Qué se prueba | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| FRO-01 | Abrir `frontend/index.html` con doble clic | Se ve el buscador y arriba dice Modo demostración |  | Pendiente |
| FRO-02 | Buscar acetaminofen sin tilde | 1 resultado: Acetaminofén |  | Pendiente |
| FRO-03 | Entrar al medicamento Acetaminofén | Dice que hay unidades en 9 de 10 sedes y muestra una tabla con los últimos movimientos (hasta 8 filas) |  | Pendiente |
| FRO-04 | Usar los filtros de localidad, ordenar y Solo con unidades | La lista cambia. Con Solo con unidades desaparece Sede Fontibón |  | Pendiente |
| FRO-05 | Abrir el menú Resumen | Muestra 123, 25, 24 y 25, que suman 197, y una lista Lo más urgente con 12 filas |  | Pendiente |
| FRO-06 | Menú Operador en modo demostración: salida de 999999 y entrada de 10 | La salida muestra un error en rojo que dice que supera el stock disponible. La entrada muestra en verde que el stock pasó de un valor a otro |  | Pendiente |
| FRO-07 | Con el backend encendido, abrir http://localhost:5500 | Arriba dice Conectado a la API |  | Pendiente |
| FRO-08 | Menú Solicitudes: crear una y avanzarla con los botones hasta Entregada | Cada botón cambia el estado y al final ya no hay botones |  | Pendiente |
| FRO-09 | Crear una solicitud con cantidad 999999 y pulsar Autorizar | Aparece el mensaje Stock insuficiente en la pantalla y sigue pendiente |  | Pendiente |
| FRO-10 | Menú Alertas: pulsar Marcar atendida | Las pendientes bajan en 1 y la alerta aparece en la lista de atendidas |  | Pendiente |
| FRO-11 | Abrir Solicitudes y Alertas sin el backend encendido | Se muestra un aviso de que la sección necesita el backend |  | Pendiente |

## 7. Defectos encontrados

| ID | Descripción | Casos donde aparece | Corrección propuesta |
| --- | --- | --- | --- |
| DEF-01 | El seed inserta filas con id fijo y deja los contadores de id en 1. El primer INSERT nuevo falla con duplicate key | BD-06, SOL-04, MED-05 | Ejecutar `database/fix_sequences.sql` después del seed |
| DEF-02 | Una salida mayor al stock devuelve error 500 en vez de 400, porque el error del trigger no lo captura `inventario.py` | INV-05 | En `backend/routes/inventario.py` usar `DBAPIError` en lugar de `IntegrityError` |

## 8. Criterios de aceptación

- Todos los casos de las secciones 6.1 a 6.6 en estado Aprobado.
- Los casos de interfaz (6.7) aprobados, o con defectos menores documentados.
- Ningún defecto abierto que impida registrar movimientos o avanzar una solicitud.

## 9. Registro de ejecución

| Dato | Valor |
| --- | --- |
| Fecha de ejecución |  |
| Ejecutado por | Gabriel Esteban Rivera Orjuela |
| Casos aprobados |  |
| Casos fallidos |  |
