# MEDIRED — Backend (Etapa 2)

API en **FastAPI** conectada al schema `medired` que ya creaste con
`database/schema.sql` en pgAdmin.

## Endpoints implementados (Fases 1–4)

| Método | Endpoint | Función |
|---|---|---|
| GET | `/api/medicamentos?q=` | Buscar/listar medicamentos |
| GET | `/api/medicamentos/{id}` | Detalle de un medicamento |
| POST | `/api/medicamentos` | Registrar medicamento en catálogo |
| GET | `/api/sedes?localidad=` | Listar sedes |
| GET | `/api/sedes/{id}` | Detalle de una sede |
| GET | `/api/inventario/{id_medicamento}` | Disponibilidad por sede |
| POST | `/api/inventario/entrada` | Registrar entrada de stock |
| POST | `/api/inventario/salida` | Registrar salida (valida stock disponible) |
| GET | `/api/inventario/movimientos/{id_medicamento}` | Historial de trazabilidad |

## Cómo correrlo

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edita .env con la contraseña de tu usuario postgres en pgAdmin
```

Cargar las variables de entorno (en Windows/PowerShell usa `$env:VAR="valor"`
o instala `python-dotenv` y añade `from dotenv import load_dotenv; load_dotenv()`
al inicio de `app.py` si prefieres no exportarlas a mano):

```bash
export $(cat .env | xargs)   # macOS/Linux
uvicorn app:app --reload
```

Abre **http://localhost:8000/docs** — ahí tienes Swagger UI, la documentación
interactiva donde puedes probar cada endpoint sin necesidad de Postman ni
escribir código de prueba.

## Prueba rápida

Con el servidor corriendo:

```bash
curl "http://localhost:8000/api/medicamentos?q=acetaminofen"
curl "http://localhost:8000/api/sedes?localidad=Suba"
curl "http://localhost:8000/api/inventario/1"
```

El último debería devolver la disponibilidad del medicamento con
`id_medicamento=1` (Acetaminofén) en todas las sedes que lo tienen en
inventario — el ejemplo técnico de la sección 17 del documento maestro.

## Cómo funciona la trazabilidad (importante)

El `schema.sql` tiene un **trigger** (`fn_aplicar_movimiento`) que calcula
`stock_anterior`/`stock_nuevo` y actualiza `inventario.cantidad_disponible`
automáticamente cada vez que se inserta una fila en `movimiento_inventario`.
Por diseño, **el backend no recalcula el stock a mano**: solo inserta el
movimiento y dejamos que la base de datos aplique la regla de negocio. Esto
evita duplicar lógica entre backend y BD, y garantiza la trazabilidad
incluso si alguien inserta un movimiento directamente en la base.

Si intentas una salida mayor al stock disponible, la base de datos la
rechaza y el endpoint `/api/inventario/salida` devuelve `400 Bad Request`
con el detalle del error — esa es la regla de la sección 16 del documento
maestro ("no se debe permitir una salida mayor al stock disponible").

## Siguiente paso (Etapa 3)

Frontend: pantallas de Inicio → Buscar medicamento → Resultados → Sede →
Disponibilidad, consumiendo estos mismos endpoints.
