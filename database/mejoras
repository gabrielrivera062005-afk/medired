-- =====================================================================
-- MEDIRED - Parche de mejoras (se corre DESPUÉS del schema original)
-- Probado en PostgreSQL 16: schema original + este archivo, sin errores.
-- OJO: cambia el tipo 'ajuste' por 'ajuste_mas' / 'ajuste_menos'.
-- Si el backend usa 'ajuste', hay que actualizarlo.
-- =====================================================================
SET search_path TO medired;

-- 1) tipos de movimiento: ajuste separado en suma/resta
ALTER TABLE movimiento_inventario DROP CONSTRAINT movimiento_inventario_tipo_movimiento_check;
ALTER TABLE movimiento_inventario ADD CONSTRAINT movimiento_inventario_tipo_movimiento_check
  CHECK (tipo_movimiento IN ('entrada','salida','reserva','liberacion_reserva','ajuste_mas','ajuste_menos'));

-- 2) trigger de movimientos corregido
CREATE OR REPLACE FUNCTION fn_aplicar_movimiento() RETURNS TRIGGER AS $$
DECLARE
    v_disp INTEGER;
    v_res  INTEGER;
    d_disp INTEGER := 0;
    d_res  INTEGER := 0;
BEGIN
    SELECT cantidad_disponible, cantidad_reservada INTO v_disp, v_res
    FROM inventario WHERE id_inventario = NEW.id_inventario FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No existe el inventario %', NEW.id_inventario;
    END IF;

    IF NEW.tipo_movimiento IN ('entrada','ajuste_mas') THEN
        d_disp := NEW.cantidad;
    ELSIF NEW.tipo_movimiento IN ('salida','ajuste_menos') THEN
        IF NEW.cantidad > v_disp THEN
            RAISE EXCEPTION 'Salida (%) supera el stock (%) en inventario %', NEW.cantidad, v_disp, NEW.id_inventario;
        END IF;
        d_disp := -NEW.cantidad;
        IF NEW.tipo_movimiento = 'salida' AND NEW.id_solicitud IS NOT NULL THEN
            d_res := -LEAST(v_res, NEW.cantidad);      -- entregar una solicitud consume su reserva
        END IF;
    ELSIF NEW.tipo_movimiento = 'reserva' THEN
        IF NEW.cantidad > v_disp - v_res THEN
            RAISE EXCEPTION 'No hay stock libre para reservar % (libre: %)', NEW.cantidad, v_disp - v_res;
        END IF;
        d_res := NEW.cantidad;
    ELSIF NEW.tipo_movimiento = 'liberacion_reserva' THEN
        IF NEW.cantidad > v_res THEN
            RAISE EXCEPTION 'No se puede liberar % (reservado: %)', NEW.cantidad, v_res;
        END IF;
        d_res := -NEW.cantidad;
    END IF;

    NEW.stock_anterior := v_disp;
    NEW.stock_nuevo    := v_disp + d_disp;

    UPDATE inventario
       SET cantidad_disponible = v_disp + d_disp,
           cantidad_reservada  = v_res + d_res,
           fecha_actualizacion = NOW()
     WHERE id_inventario = NEW.id_inventario;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3) alertas sin duplicados
CREATE OR REPLACE FUNCTION fn_generar_alerta() RETURNS TRIGGER AS $$
DECLARE v_tipo VARCHAR(30);
BEGIN
    v_tipo := CASE WHEN NEW.cantidad_disponible = 0 THEN 'agotado' ELSE 'stock_critico' END;
    IF NOT EXISTS (SELECT 1 FROM alerta
                   WHERE id_inventario = NEW.id_inventario AND tipo = v_tipo AND NOT atendida) THEN
        INSERT INTO alerta (id_inventario, tipo) VALUES (NEW.id_inventario, v_tipo);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER trg_generar_alerta ON inventario;
CREATE TRIGGER trg_generar_alerta
    AFTER UPDATE OF cantidad_disponible ON inventario
    FOR EACH ROW
    WHEN (NEW.cantidad_disponible = 0 OR NEW.cantidad_disponible < NEW.stock_minimo)
    EXECUTE FUNCTION fn_generar_alerta();

-- 4) movimientos inmutables
CREATE OR REPLACE FUNCTION fn_bloquear_cambios() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Los movimientos de inventario no se pueden modificar ni borrar';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_movimiento_inmutable
    BEFORE UPDATE OR DELETE ON movimiento_inventario
    FOR EACH ROW EXECUTE FUNCTION fn_bloquear_cambios();

-- 5) solicitud: usuario y sede de la misma EPS
CREATE OR REPLACE FUNCTION fn_validar_solicitud_eps() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT id_eps FROM usuario WHERE id_usuario = NEW.id_usuario)
       IS DISTINCT FROM (SELECT id_eps FROM sede WHERE id_sede = NEW.id_sede) THEN
        RAISE EXCEPTION 'El usuario y la sede pertenecen a EPS distintas';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_validar_solicitud_eps
    BEFORE INSERT OR UPDATE OF id_usuario, id_sede ON solicitud
    FOR EACH ROW EXECUTE FUNCTION fn_validar_solicitud_eps();

-- 6) restricciones simples
ALTER TABLE detalle_solicitud ADD CONSTRAINT uq_detalle UNIQUE (id_solicitud, id_medicamento);
ALTER TABLE detalle_solicitud ADD CONSTRAINT ck_autorizada CHECK (cantidad_autorizada IS NULL OR cantidad_autorizada <= cantidad_solicitada);
ALTER TABLE inventario ADD CONSTRAINT ck_reservada CHECK (cantidad_reservada <= cantidad_disponible);
ALTER TABLE medicamento ADD CONSTRAINT uq_cum UNIQUE (codigo_cum);
ALTER TABLE entrega ADD CONSTRAINT uq_entrega_solicitud UNIQUE (id_solicitud);

-- 7) índices
DROP INDEX idx_inventario_medicamento;
CREATE INDEX idx_sede_eps ON sede (id_eps);
CREATE INDEX idx_usuario_eps ON usuario (id_eps);
CREATE INDEX idx_solicitud_sede ON solicitud (id_sede);
CREATE INDEX idx_detalle_medicamento ON detalle_solicitud (id_medicamento);
CREATE INDEX idx_reserva_solicitud ON reserva (id_solicitud);
CREATE INDEX idx_reserva_inventario ON reserva (id_inventario);
CREATE INDEX idx_mov_solicitud ON movimiento_inventario (id_solicitud);
CREATE INDEX idx_alerta_pendientes ON alerta (id_inventario) WHERE NOT atendida;
