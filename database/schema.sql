-- =====================================================================
-- MEDIRED - Schema de base de datos (PostgreSQL)
-- MVP académico: piloto con Nueva EPS - Bogotá D.C.
-- =====================================================================
-- Diseño multi-EPS desde el inicio: NO hay tablas por EPS
-- (nada de inventario_eps1, tabla_eps2, etc). Todo cuelga de una única
-- tabla `eps` vía FK, así que agregar una EPS nueva es solo una fila más
-- en `eps`, sin tocar el resto del modelo ni del código.
-- Convenciones:
--  - Todas las PK son SERIAL/BIGSERIAL.
--  - Todos los movimientos de inventario quedan registrados (trazabilidad).
--  - Los datos personales del MVP son sintéticos (ver sección 21 doc maestro).
-- =====================================================================

DROP SCHEMA IF EXISTS medired CASCADE;
CREATE SCHEMA medired;
SET search_path TO medired;

-- ---------------------------------------------------------------------
-- 1. EPS
-- ---------------------------------------------------------------------
CREATE TABLE eps (
    id_eps          SERIAL PRIMARY KEY,
    codigo          VARCHAR(20) UNIQUE NOT NULL,      -- ej: 'EPS037' (Nueva EPS)
    nombre          VARCHAR(150) NOT NULL,
    nit             VARCHAR(20),
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- 2. USUARIO (paciente, operador, administrador, analista)
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario      SERIAL PRIMARY KEY,
    id_eps          INTEGER REFERENCES eps(id_eps),
    documento       VARCHAR(20) UNIQUE NOT NULL,       -- documento sintético
    nombre          VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE,
    telefono        VARCHAR(20),
    rol             VARCHAR(20) NOT NULL CHECK (rol IN
                        ('paciente','operador_inventario','administrador','analista')),
    password_hash   VARCHAR(255) NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- 3. MEDICAMENTO (catálogo maestro - referencia INVIMA/SISMED)
-- ---------------------------------------------------------------------
CREATE TABLE medicamento (
    id_medicamento      SERIAL PRIMARY KEY,
    codigo_cum          VARCHAR(30),                    -- INVIMA
    codigo_ium          VARCHAR(30),                    -- SISMED / estándar
    nombre              VARCHAR(200) NOT NULL,
    principio_activo    VARCHAR(200) NOT NULL,
    forma_farmaceutica  VARCHAR(60) NOT NULL,
    concentracion       VARCHAR(50),
    via_administracion  VARCHAR(50),
    requiere_formula    BOOLEAN NOT NULL DEFAULT TRUE,
    activo              BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- 4. SEDE (puntos de atención / dispensación por EPS)
-- ---------------------------------------------------------------------
CREATE TABLE sede (
    id_sede         SERIAL PRIMARY KEY,
    id_eps          INTEGER NOT NULL REFERENCES eps(id_eps),
    nombre          VARCHAR(150) NOT NULL,
    localidad       VARCHAR(80) NOT NULL,       -- localidad de Bogotá
    direccion       VARCHAR(200) NOT NULL,
    telefono        VARCHAR(20),
    horario         VARCHAR(100),
    latitud         NUMERIC(9,6),
    longitud        NUMERIC(9,6),
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- 5. INVENTARIO (stock por medicamento/sede)
-- ---------------------------------------------------------------------
CREATE TABLE inventario (
    id_inventario       SERIAL PRIMARY KEY,
    id_medicamento      INTEGER NOT NULL REFERENCES medicamento(id_medicamento),
    id_sede             INTEGER NOT NULL REFERENCES sede(id_sede),
    cantidad_disponible INTEGER NOT NULL DEFAULT 0 CHECK (cantidad_disponible >= 0),
    cantidad_reservada  INTEGER NOT NULL DEFAULT 0 CHECK (cantidad_reservada >= 0),
    stock_minimo        INTEGER NOT NULL DEFAULT 0,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_medicamento, id_sede)
);

-- ---------------------------------------------------------------------
-- 6. MOVIMIENTO_INVENTARIO (trazabilidad: entradas, salidas, ajustes)
-- ---------------------------------------------------------------------
CREATE TABLE movimiento_inventario (
    id_movimiento   BIGSERIAL PRIMARY KEY,
    id_inventario   INTEGER NOT NULL REFERENCES inventario(id_inventario),
    tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN
                        ('entrada','salida','reserva','liberacion_reserva','ajuste')),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    stock_anterior  INTEGER NOT NULL,
    stock_nuevo     INTEGER NOT NULL,
    id_solicitud    INTEGER,                         -- FK lógica a solicitud (opcional)
    id_operador     INTEGER REFERENCES usuario(id_usuario),
    fuente          VARCHAR(100) NOT NULL DEFAULT 'manual', -- manual | api_simulada | integracion
    fecha_hora      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- 7. SOLICITUD (solicitud de medicamentos del paciente)
-- ---------------------------------------------------------------------
CREATE TABLE solicitud (
    id_solicitud    SERIAL PRIMARY KEY,
    id_usuario      INTEGER NOT NULL REFERENCES usuario(id_usuario),
    id_sede         INTEGER NOT NULL REFERENCES sede(id_sede),
    tipo_entrega    VARCHAR(20) NOT NULL CHECK (tipo_entrega IN ('domicilio','recoger_sede')),
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN
                        ('pendiente','autorizada','preparando','en_camino','entregada','cancelada')),
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE movimiento_inventario
    ADD CONSTRAINT fk_movimiento_solicitud
    FOREIGN KEY (id_solicitud) REFERENCES solicitud(id_solicitud);

-- ---------------------------------------------------------------------
-- 8. DETALLE_SOLICITUD
-- ---------------------------------------------------------------------
CREATE TABLE detalle_solicitud (
    id_detalle          SERIAL PRIMARY KEY,
    id_solicitud        INTEGER NOT NULL REFERENCES solicitud(id_solicitud) ON DELETE CASCADE,
    id_medicamento      INTEGER NOT NULL REFERENCES medicamento(id_medicamento),
    cantidad_solicitada INTEGER NOT NULL CHECK (cantidad_solicitada > 0),
    cantidad_autorizada INTEGER
);

-- ---------------------------------------------------------------------
-- 9. RESERVA (cantidad apartada mientras se procesa la solicitud)
-- ---------------------------------------------------------------------
CREATE TABLE reserva (
    id_reserva      SERIAL PRIMARY KEY,
    id_solicitud    INTEGER NOT NULL REFERENCES solicitud(id_solicitud),
    id_inventario   INTEGER NOT NULL REFERENCES inventario(id_inventario),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    estado          VARCHAR(20) NOT NULL DEFAULT 'activa' CHECK (estado IN
                        ('activa','liberada','consumida','expirada')),
    fecha_reserva     TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_expiracion  TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 10. ENTREGA (seguimiento de domicilio / recogida)
-- ---------------------------------------------------------------------
CREATE TABLE entrega (
    id_entrega                  SERIAL PRIMARY KEY,
    id_solicitud                INTEGER NOT NULL REFERENCES solicitud(id_solicitud),
    estado                      VARCHAR(20) NOT NULL DEFAULT 'autorizada' CHECK (estado IN
                                    ('autorizada','preparando','en_camino','entregada','cancelada')),
    direccion_entrega           VARCHAR(200),
    transportista               VARCHAR(100),
    fecha_estado                TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_entrega_estimada      TIMESTAMP,
    fecha_entrega_real          TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 11. ALERTA (stock crítico, agotado, faltantes recurrentes)
-- ---------------------------------------------------------------------
CREATE TABLE alerta (
    id_alerta           SERIAL PRIMARY KEY,
    id_inventario       INTEGER NOT NULL REFERENCES inventario(id_inventario),
    tipo                VARCHAR(30) NOT NULL CHECK (tipo IN
                            ('stock_critico','agotado','faltante_recurrente')),
    fecha_generacion    TIMESTAMP NOT NULL DEFAULT NOW(),
    atendida            BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_atencion      TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 12. HISTORIAL / AUDITORÍA genérica
-- ---------------------------------------------------------------------
CREATE TABLE historial_auditoria (
    id_historial    BIGSERIAL PRIMARY KEY,
    tabla_afectada  VARCHAR(60) NOT NULL,
    id_registro     INTEGER NOT NULL,
    accion          VARCHAR(20) NOT NULL CHECK (accion IN ('insert','update','delete')),
    id_usuario      INTEGER REFERENCES usuario(id_usuario),
    fecha_hora      TIMESTAMP NOT NULL DEFAULT NOW(),
    detalle         JSONB
);

-- =====================================================================
-- ÍNDICES
-- =====================================================================
CREATE INDEX idx_medicamento_nombre ON medicamento USING GIN (to_tsvector('spanish', nombre));
CREATE INDEX idx_medicamento_principio ON medicamento (principio_activo);
CREATE INDEX idx_inventario_medicamento ON inventario (id_medicamento);
CREATE INDEX idx_inventario_sede ON inventario (id_sede);
CREATE INDEX idx_movimiento_inventario ON movimiento_inventario (id_inventario, fecha_hora);
CREATE INDEX idx_solicitud_usuario ON solicitud (id_usuario);
CREATE INDEX idx_alerta_inventario ON alerta (id_inventario, atendida);

-- =====================================================================
-- TRIGGERS: reglas de negocio de la sección 16 del documento maestro
-- =====================================================================

-- 1) Al insertar un movimiento, actualizar el stock de inventario
--    y validar que una salida no supere el disponible.
CREATE OR REPLACE FUNCTION fn_aplicar_movimiento()
RETURNS TRIGGER AS $$
DECLARE
    v_disponible INTEGER;
BEGIN
    SELECT cantidad_disponible INTO v_disponible
    FROM inventario WHERE id_inventario = NEW.id_inventario
    FOR UPDATE;

    IF NEW.tipo_movimiento = 'salida' AND NEW.cantidad > v_disponible THEN
        RAISE EXCEPTION 'Salida (%) supera el stock disponible (%) en inventario %',
            NEW.cantidad, v_disponible, NEW.id_inventario;
    END IF;

    NEW.stock_anterior := v_disponible;

    IF NEW.tipo_movimiento IN ('entrada','liberacion_reserva') THEN
        NEW.stock_nuevo := v_disponible + NEW.cantidad;
    ELSIF NEW.tipo_movimiento IN ('salida') THEN
        NEW.stock_nuevo := v_disponible - NEW.cantidad;
    ELSIF NEW.tipo_movimiento = 'reserva' THEN
        NEW.stock_nuevo := v_disponible; -- la reserva mueve a cantidad_reservada, no al disponible
    ELSE
        NEW.stock_nuevo := v_disponible; -- ajuste manual se resuelve aparte
    END IF;

    UPDATE inventario
       SET cantidad_disponible = NEW.stock_nuevo,
           fecha_actualizacion = NOW()
     WHERE id_inventario = NEW.id_inventario;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_aplicar_movimiento
    BEFORE INSERT ON movimiento_inventario
    FOR EACH ROW EXECUTE FUNCTION fn_aplicar_movimiento();

-- 2) Generar alerta automática cuando el stock quede en 0 o por debajo del mínimo
CREATE OR REPLACE FUNCTION fn_generar_alerta()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.cantidad_disponible = 0 THEN
        INSERT INTO alerta (id_inventario, tipo)
        VALUES (NEW.id_inventario, 'agotado');
    ELSIF NEW.cantidad_disponible < NEW.stock_minimo THEN
        INSERT INTO alerta (id_inventario, tipo)
        VALUES (NEW.id_inventario, 'stock_critico');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generar_alerta
    AFTER UPDATE OF cantidad_disponible ON inventario
    FOR EACH ROW
    WHEN (NEW.cantidad_disponible <= NEW.stock_minimo)
    EXECUTE FUNCTION fn_generar_alerta();

-- =====================================================================
-- VISTA: disponibilidad legible (usada por GET /api/inventario/{id})
-- =====================================================================
CREATE VIEW vw_disponibilidad AS
SELECT
    m.id_medicamento,
    m.nombre            AS medicamento,
    m.concentracion,
    s.id_sede,
    s.nombre            AS sede,
    s.localidad,
    i.cantidad_disponible,
    i.stock_minimo,
    CASE
        WHEN i.cantidad_disponible = 0 THEN 'no_disponible'
        WHEN i.cantidad_disponible < i.stock_minimo THEN 'critico'
        WHEN i.cantidad_disponible < i.stock_minimo * 2 THEN 'bajo'
        ELSE 'disponible'
    END AS estado
FROM inventario i
JOIN medicamento m ON m.id_medicamento = i.id_medicamento
JOIN sede s ON s.id_sede = i.id_sede;
