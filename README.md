
# 📚 Sistema de Gestión Editorial

## 📌 Descripción

Este proyecto es un sistema de gestión de préstamos y publicaciones para una editorial, desarrollado como parte del curso de Bases de Datos 1. Permite:

- ✅ Registrar libros, autores, editoriales y usuarios  
- ✅ Gestionar préstamos y reservas  
- ✅ Generar reportes con filtros avanzados  
- ✅ Exportar datos a Excel (XLSX) y PDF  

---

## ⚙️ Requisitos

- **PostgreSQL** (v14+)
- **Python** (v3.9+)

### Dependencias

Instalar usando `pip`:

```bash
pip install -r requirements.txt
```

---

## 🚀 Instalación

### 1. Configuración de la Base de Datos

```bash
# Crear la base de datos
createdb -U postgres editorial

# Ejecutar scripts SQL
psql -U postgres -d editorial -f database/schema.sql
psql -U postgres -d editorial -f database/data.sql
```

### 2. Configuración del Entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```ini
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

### 3. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en:

🌐 [http://localhost:5000](http://localhost:5000)

---

## 📂 Estructura del Proyecto

```
/proyecto_editorial
├── app.py                # Aplicación principal (Flask)
├── export.py             # Lógica de exportación (PDF/Excel)
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno (opcional)
├── /database
│   ├── schema.sql        # Estructura de la base de datos
│   └── data.sql          # Datos de prueba
├── /templates
│   ├── base.html         # Plantilla principal
│   ├── reportes.html     # Página de reportes
│   └── exportar.html     # Página de exportación
└── /static
    ├── style.css         # Estilos CSS
    ├── graficas.js       # Gráficas con Chart.js
    └── exportar.js       # Lógica de exportación
```

---

## 🔍 Funcionalidades Clave

### 📊 Reportes

Filtros por:

- Fecha de préstamo/devolución  
- Editorial  
- Categoría  
- Tipo de usuario  

Incluye gráficas interactivas de libros más prestados.

### 📤 Exportación

- **Excel (XLSX):** Ideal para análisis adicionales  
- **PDF:** Formato listo para imprimir  

---

## ⚡ Automatizaciones

- Cálculo automático de fechas límite (15 días)  
- Generación de sanciones por atrasos ($5 por día)  
- Actualización de reservas cuando un libro se devuelve  

---

## 🐛 Solución de Problemas

### Error al exportar archivos

Si falla la descarga de Excel/PDF:

- Verifica que la carpeta `exports` exista y tenga permisos de escritura.  
- Revisa los logs de Flask para ver errores específicos.

### Error de conexión a PostgreSQL

- Asegúrate de que PostgreSQL esté corriendo:

```bash
sudo service postgresql status
```

- Verifica que las credenciales en `.env` o `app.py` sean correctas.

---

## 📜 Licencia

Este proyecto está bajo la licencia **MIT**.

---

## ✨ ¡Gracias por usar el sistema!

Si tienes preguntas, abre un issue en el repositorio.
