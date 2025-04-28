CREATE DATABASE editorial
-- Tablas principales
CREATE TABLE Editorial (
    id_editorial SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    telefono VARCHAR(15)
);

CREATE TABLE Libro (
    id_libro SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    año_publicacion INTEGER CHECK(año_publicacion > 0),
    edicion INTEGER DEFAULT 1,
    id_editorial INTEGER REFERENCES Editorial(id_editorial)
);

CREATE TABLE Autor (
    id_autor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais_origen VARCHAR(50),
    fecha_nacimiento DATE
);

CREATE TABLE Categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(15),
    tipo VARCHAR(20) CHECK(tipo IN ('Estudiante', 'Profesor', 'Personal'))
);

-- Tablas de relación N:M
CREATE TABLE Libro_Autor (
    id_libro INTEGER REFERENCES Libro(id_libro),
    id_autor INTEGER REFERENCES Autor(id_autor),
    PRIMARY KEY (id_libro, id_autor)
);

CREATE TABLE Libro_Categoria (
    id_libro INTEGER REFERENCES Libro(id_libro),
    id_categoria INTEGER REFERENCES Categoria(id_categoria),
    PRIMARY KEY (id_libro, id_categoria)
);

-- Tablas de operaciones
CREATE TABLE Ejemplar (
    id_ejemplar SERIAL PRIMARY KEY,
    id_libro INTEGER REFERENCES Libro(id_libro),
    codigo_barras VARCHAR(50) UNIQUE,
    estado VARCHAR(20) CHECK(estado IN ('disponible', 'prestado', 'en_reparacion')) DEFAULT 'disponible',
    ubicacion VARCHAR(50)
);

CREATE TABLE Prestamo (
    id_prestamo SERIAL PRIMARY KEY,
    id_ejemplar INTEGER REFERENCES Ejemplar(id_ejemplar),
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    fecha_prestamo DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_limite DATE NOT NULL,
    fecha_devolucion DATE,
    dias_atraso INTEGER DEFAULT 0
);

CREATE TABLE Reserva (
    id_reserva SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_libro INTEGER REFERENCES Libro(id_libro),
    fecha_reserva DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_limite DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'completada', 'cancelada'))
);

CREATE TABLE Sancion (
    id_sancion SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_prestamo INTEGER REFERENCES Prestamo(id_prestamo),
    monto DECIMAL(10,2) NOT NULL,
    fecha_sancion DATE NOT NULL DEFAULT CURRENT_DATE,
    pagada BOOLEAN NOT NULL DEFAULT FALSE
);

-- 1. Función para calcular fecha límite (CORRECTA)
CREATE OR REPLACE FUNCTION calcular_fecha_limite()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_limite := NEW.fecha_prestamo + INTERVAL '15 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Actualizar estado de ejemplar (CORRECTA)
CREATE OR REPLACE FUNCTION actualizar_estado_ejemplar()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Ejemplar SET estado = 'prestado' WHERE id_ejemplar = NEW.id_ejemplar;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Calcular días de atraso (MEJORADA)
CREATE OR REPLACE FUNCTION calcular_atraso()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_devolucion IS NOT NULL THEN
        NEW.dias_atraso := (NEW.fecha_devolucion - NEW.fecha_limite);
        -- Asegurar que no sea negativo
        IF NEW.dias_atraso < 0 THEN 
            NEW.dias_atraso := 0;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Generar sanción (CORRECTA)
CREATE OR REPLACE FUNCTION generar_sancion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.dias_atraso > 0 AND (OLD.dias_atraso IS NULL OR OLD.dias_atraso <= 0) THEN
        INSERT INTO Sancion (id_usuario, id_prestamo, monto)
        VALUES (NEW.id_usuario, NEW.id_prestamo, NEW.dias_atraso * 5.0);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Completar reserva (SIMPLIFICADA)
CREATE OR REPLACE FUNCTION completar_reserva()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'disponible' AND OLD.estado = 'prestado' THEN
        -- Primero identificar la reserva más antigua pendiente
        UPDATE Reserva 
        SET estado = 'completada'
        WHERE id_reserva = (
            SELECT id_reserva 
            FROM Reserva 
            WHERE id_libro = (
                SELECT id_libro FROM Ejemplar WHERE id_ejemplar = NEW.id_ejemplar
            )
            AND estado = 'pendiente'
            ORDER BY fecha_reserva ASC
            LIMIT 1
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Eliminar triggers existentes
DROP TRIGGER IF EXISTS trigger_calcular_fecha_limite ON Prestamo;
DROP TRIGGER IF EXISTS trigger_actualizar_estado_ejemplar ON Prestamo;
DROP TRIGGER IF EXISTS trigger_calcular_atraso ON Prestamo;
DROP TRIGGER IF EXISTS trigger_generar_sancion ON Prestamo;
DROP TRIGGER IF EXISTS trigger_completar_reserva ON Ejemplar;

-- Crear nuevos triggers
CREATE TRIGGER trigger_calcular_fecha_limite
BEFORE INSERT ON Prestamo
FOR EACH ROW
EXECUTE FUNCTION calcular_fecha_limite();

CREATE TRIGGER trigger_actualizar_estado_ejemplar
AFTER INSERT ON Prestamo
FOR EACH ROW
EXECUTE FUNCTION actualizar_estado_ejemplar();

CREATE TRIGGER trigger_calcular_atraso
BEFORE UPDATE OF fecha_devolucion ON Prestamo 
FOR EACH ROW
EXECUTE FUNCTION calcular_atraso();

CREATE TRIGGER trigger_generar_sancion
AFTER UPDATE OF dias_atraso ON Prestamo 
FOR EACH ROW
EXECUTE FUNCTION generar_sancion();

CREATE TRIGGER trigger_completar_reserva
AFTER UPDATE OF estado ON Ejemplar 
FOR EACH ROW
EXECUTE FUNCTION completar_reserva();