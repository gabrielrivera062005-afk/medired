# MEDIRED

Plataforma interoperable para la **consulta, gestión y trazabilidad de medicamentos** de una EPS en Bogotá D.C.

Este repositorio es el **prototipo (MVP académico)** del proyecto MEDIRED de la materia Gestión de Proyectos, Ingeniería en Ciencia de Datos. El piloto trabaja con **una sola EPS (Nueva EPS, Bogotá)** y con **datos sintéticos**: los usuarios, las sedes, el inventario y las solicitudes son artificiales y se crearon para mostrar cómo funciona el sistema.

## Qué hace el prototipo

- Buscar medicamentos en un catálogo (nombre, principio activo, concentración, forma farmacéutica).
- Consultar en qué sedes hay un medicamento y en qué estado está su stock (`disponible`, `bajo`, `critico` o `no_disponible`).
- Registrar entradas y salidas de inventario, con historial de cada movimiento (trazabilidad).
- Rechazar salidas mayores al stock disponible.
- Generar alertas automáticas cuando el stock queda en cero o por debajo del mínimo.

## Estructura del repositorio

```
medired/
├── backend/                  API en Python (FastAPI)
│   ├── app.py                aplicación principal
│   ├── config.py             configuración
│   ├── database.py           conexión a PostgreSQL (SQLAlchemy)
│   ├── models.py             modelos de las tablas
│   ├── schemas.py            esquemas de entrada y salida (Pydantic)
│   ├── requirements.txt      librerías necesarias
│   ├── README.md             guía detallada del backend
│   └── routes/
│       ├── medicamentos.py
│       ├── sedes.py
│       └── inventario.py
├── database/
│   ├── schema.sql            crea el esquema, tablas, triggers y la vista
│   └── seed synthetic.sql    carga los datos sintéticos
└── frontend/
    └── index.html            interfaz web (abre con doble clic)
```

## Tecnologías

- **Base de datos:** PostgreSQL
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **Frontend:** HTML, CSS y JavaScript en un solo archivo

## Base de datos

El esquema se llama `medired` e incluye:

- **12 tablas:** `eps`, `usuario`, `medicamento`, `sede`, `inventario`, `movimiento_inventario`, `solicitud`, `detalle_solicitud`, `reserva`, `entrega`, `alerta` y `historial_auditoria`.
- **2 triggers:**
  - `fn_aplicar_movimiento`: cada vez que se inserta un movimiento, calcula `stock_anterior` y `stock_nuevo`, actualiza el inventario y rechaza salidas mayores al stock disponible.
  - `fn_generar_alerta`: crea una alerta cuando el stock llega a 0 o queda por debajo del mínimo.
- **1 vista:** `vw_disponibilidad`, que muestra el estado de cada medicamento por sede.

Todo cuelga de la tabla `eps`, así que el modelo está pensado para agregar más EPS sin crear tablas nuevas.

### Cómo cargarla (pgAdmin)

1. Crea una base de datos vacía en PostgreSQL.
2. Abre el **Query Tool** sobre esa base de datos.
3. Ejecuta primero `database/schema.sql`.
4. Ejecuta después `database/seed synthetic.sql`.

> **Ojo:** `schema.sql` empieza con `DROP SCHEMA IF EXISTS medired CASCADE`. Si lo vuelves a ejecutar, **borra todo lo que haya en el esquema `medired`**, incluidos los datos.

### Qué trae el seed

| Tabla | Filas |
|---|---|
| eps | 1 |
| sede | 12 (una por localidad de Bogotá) |
| medicamento | 20 |
| usuario | 13 (10 pacientes, 1 operador, 1 administrador, 1 analista) |
| inventario | 197 |
| movimiento_inventario | 595 |
| solicitud | 25 |
| detalle_solicitud | 25 |
| entrega | 9 |

El seed inserta movimientos de inventario, así que el trigger se dispara y recalcula el stock. Por eso, al cargarlo, la tabla `alerta` queda con alertas generadas automáticamente (en la prueba salieron 132).

## Cómo correr el backend

Necesitas Python 3 y la base de datos ya cargada. Desde la carpeta `backend`:

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # en macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Después crea tu archivo `.env` a partir de `.env.example` y pon la contraseña de tu usuario de PostgreSQL. El detalle de cómo cargar las variables de entorno en Windows y en macOS/Linux está en [`backend/README.md`](backend/README.md).

Para iniciar el servidor:

```bash
uvicorn app:app --reload
```

Abre **http://localhost:8000/docs** para ver la documentación interactiva (Swagger UI), donde puedes probar cada endpoint sin escribir código.

## Cómo ver el frontend

Abre `frontend/index.html` con doble clic. Tiene dos modos:

- **Modo demostración:** funciona solo, sin backend, con los datos del seed (20 medicamentos, 12 sedes y 197 registros de inventario).
- **Modo API:** si el backend está corriendo en `localhost:8000`, la página usa los endpoints reales. Para probarlo, sirve la carpeta con `python -m http.server 5500` y abre `http://localhost:5500`. Este modo requiere que ese origen esté permitido en `CORS_ORIGINS` de `backend/config.py`.

Pantallas: Inicio con buscador, Resultados, Disponibilidad por sede (con filtro por localidad) y Detalle de la sede.

## Endpoints

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Revisar que el servicio está activo |
| GET | `/api/medicamentos?q=` | Buscar o listar medicamentos |
| GET | `/api/medicamentos/{id}` | Detalle de un medicamento |
| POST | `/api/medicamentos` | Registrar un medicamento en el catálogo |
| GET | `/api/sedes?localidad=` | Listar sedes |
| GET | `/api/sedes/{id}` | Detalle de una sede |
| GET | `/api/inventario/{id_medicamento}` | Disponibilidad por sede |
| POST | `/api/inventario/entrada` | Registrar una entrada de stock |
| POST | `/api/inventario/salida` | Registrar una salida (valida el stock disponible) |
| GET | `/api/inventario/movimientos/{id_medicamento}` | Historial de movimientos |

### Prueba rápida

```bash
curl "http://localhost:8000/api/medicamentos?q=acetaminofen"
curl "http://localhost:8000/api/sedes?localidad=Suba"
curl "http://localhost:8000/api/inventario/1"
```

## Trazabilidad

El backend **no calcula el stock a mano**: solo inserta el movimiento y deja que el trigger de la base de datos aplique la regla de negocio. Así la lógica no se duplica y la trazabilidad se mantiene incluso si alguien inserta un movimiento directo en la base de datos.

Si se intenta una salida mayor al stock disponible, la base de datos la rechaza y el endpoint `/api/inventario/salida` responde `400 Bad Request` con el detalle del error.

## Estado del proyecto

- Implementado: catálogo de medicamentos, sedes, disponibilidad y movimientos de inventario, y una interfaz web de consulta.
- Pendiente: los endpoints de solicitudes, reservas y entregas (las tablas ya existen en la base de datos).

## Datos sintéticos

Todos los datos de este repositorio son artificiales. Los documentos, correos, teléfonos y direcciones no corresponden a personas reales, y el NIT de la EPS es solo referencial.
