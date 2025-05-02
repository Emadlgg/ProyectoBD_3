from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import psycopg2
from export import exportar_pdf, exportar_excel
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuración de PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="editorial",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    return conn

# Ruta principal - Formulario de reportes
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener filtros disponibles
        cursor.execute("SELECT id_editorial, nombre FROM Editorial ORDER BY nombre")
        editoriales = cursor.fetchall()
        
        cursor.execute("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
        categorias = cursor.fetchall()
        
        conn.close()
        
        return render_template('reportes.html', 
                            editoriales=editoriales, 
                            categorias=categorias,
                            fecha_inicio=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            fecha_fin=datetime.now().strftime('%Y-%m-%d'))
    
    except Exception as e:
        flash(f"Error al conectar con la base de datos: {str(e)}", "danger")
        return render_template('reportes.html', 
                            editoriales=[], 
                            categorias=[])

# Generar reporte con filtros
@app.route('/generar_reporte', methods=['POST'])
def generar_reporte():
    try:
        # Obtener parámetros del formulario
        tipo_reporte = request.form.get('tipo_reporte')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        editorial = request.form.get('editorial')
        categoria = request.form.get('categoria')
        
        # Validación básica de fechas
        if not fecha_inicio or not fecha_fin:
            flash("Las fechas son obligatorias", "warning")
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener filtros disponibles para el template
        cursor.execute("SELECT id_editorial, nombre FROM Editorial ORDER BY nombre")
        editoriales = cursor.fetchall()
        
        cursor.execute("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
        categorias = cursor.fetchall()
        
        # Consulta base según tipo de reporte
        if tipo_reporte == 'prestamos':
            query = """
            SELECT p.id_prestamo, l.titulo, u.nombre, p.fecha_prestamo, 
                   p.fecha_devolucion, p.dias_atraso, e.nombre as editorial
            FROM Prestamo p
            JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
            JOIN Libro l ON ej.id_libro = l.id_libro
            JOIN Usuario u ON p.id_usuario = u.id_usuario
            JOIN Editorial e ON l.id_editorial = e.id_editorial
            WHERE p.fecha_prestamo BETWEEN %s AND %s
            """
            params = [fecha_inicio, fecha_fin]
            
        elif tipo_reporte == 'atrasos':
            query = """
            SELECT p.id_prestamo, l.titulo, u.nombre, p.fecha_prestamo, 
                   p.fecha_devolucion, p.dias_atraso, e.nombre as editorial
            FROM Prestamo p
            JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
            JOIN Libro l ON ej.id_libro = l.id_libro
            JOIN Usuario u ON p.id_usuario = u.id_usuario
            JOIN Editorial e ON l.id_editorial = e.id_editorial
            WHERE p.fecha_prestamo BETWEEN %s AND %s
            AND p.dias_atraso > 0
            """
            params = [fecha_inicio, fecha_fin]
            
        elif tipo_reporte == 'reservas':
            query = """
            SELECT r.id_reserva as id_prestamo, l.titulo, u.nombre, 
                   r.fecha_reserva as fecha_prestamo, 
                   NULL as fecha_devolucion, 
                   0 as dias_atraso, 
                   e.nombre as editorial
            FROM Reserva r
            JOIN Libro l ON r.id_libro = l.id_libro
            JOIN Usuario u ON r.id_usuario = u.id_usuario
            JOIN Editorial e ON l.id_editorial = e.id_editorial
            WHERE r.estado = 'pendiente'
            """
            params = []
            
        elif tipo_reporte == 'sanciones':
            query = """
            SELECT s.id_sancion as id_prestamo, l.titulo, u.nombre, 
                   p.fecha_prestamo, p.fecha_devolucion, 
                   p.dias_atraso, e.nombre as editorial
            FROM Sancion s
            JOIN Prestamo p ON s.id_prestamo = p.id_prestamo
            JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
            JOIN Libro l ON ej.id_libro = l.id_libro
            JOIN Usuario u ON p.id_usuario = u.id_usuario
            JOIN Editorial e ON l.id_editorial = e.id_editorial
            WHERE s.pagada = FALSE
            """
            params = []
            
        else:  # libros_populares
            query = """
            SELECT 
                ROW_NUMBER() OVER () as id_prestamo,
                l.titulo, 
                'N/A' as nombre, 
                NULL as fecha_prestamo, 
                NULL as fecha_devolucion, 
                COUNT(p.id_prestamo) as dias_atraso, 
                e.nombre as editorial
            FROM Libro l
            LEFT JOIN Ejemplar ej ON l.id_libro = ej.id_libro
            LEFT JOIN Prestamo p ON ej.id_ejemplar = p.id_ejemplar
            JOIN Editorial e ON l.id_editorial = e.id_editorial
            GROUP BY l.id_libro, e.nombre
            ORDER BY COUNT(p.id_prestamo) DESC
            LIMIT 10
            """
            params = []
        
        # Aplicar filtros adicionales (excepto para reportes especiales)
        if tipo_reporte in ['prestamos', 'atrasos']:
            if editorial and editorial != "todas":
                query += " AND l.id_editorial = %s"
                params.append(editorial)
            
            if categoria and categoria != "todas":
                query += """
                AND l.id_libro IN (
                    SELECT id_libro FROM Libro_Categoria WHERE id_categoria = %s
                )
                """
                params.append(categoria)
        
        # Ejecutar consulta principal
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Obtener datos para gráficas (solo para reportes principales)
        libros = []
        prestamos = []
        
        if tipo_reporte in ['prestamos', 'atrasos']:
            cursor.execute("""
            SELECT l.titulo, COUNT(p.id_prestamo) as total
            FROM Prestamo p
            JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
            JOIN Libro l ON ej.id_libro = l.id_libro
            WHERE p.fecha_prestamo BETWEEN %s AND %s
            GROUP BY l.titulo
            ORDER BY total DESC
            LIMIT 5
            """, [fecha_inicio, fecha_fin])
            datos_grafica = cursor.fetchall()
            libros = [item[0] for item in datos_grafica]
            prestamos = [item[1] for item in datos_grafica]
        
        conn.close()
        
        return render_template('reportes.html', 
                            resultados=resultados,
                            libros=libros,
                            prestamos=prestamos,
                            editoriales=editoriales,
                            categorias=categorias,
                            filtros_actuales={
                                'tipo_reporte': tipo_reporte,
                                'fecha_inicio': fecha_inicio,
                                'fecha_fin': fecha_fin,
                                'editorial': editorial,
                                'categoria': categoria
                            })
    
    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "danger")
        return redirect(url_for('index'))

# Exportar a PDF
@app.route('/exportar_pdf')
def exportar_pdf_route():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta completa con joins
        cursor.execute("""
        SELECT l.titulo, u.nombre, p.fecha_prestamo, 
               p.fecha_devolucion, p.dias_atraso, e.nombre as editorial
        FROM Prestamo p
        JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
        JOIN Libro l ON ej.id_libro = l.id_libro
        JOIN Usuario u ON p.id_usuario = u.id_usuario
        JOIN Editorial e ON l.id_editorial = e.id_editorial
        ORDER BY p.fecha_prestamo DESC
        """)
        data = cursor.fetchall()
        conn.close()
        
        filename = f"reporte_prestamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = exportar_pdf(data, filename)
        
        # Enviar el archivo y luego eliminarlo
        response = send_file(
            filepath,
            as_attachment=True,
            mimetype='application/pdf'
        )
        
        # Programar eliminación después de la respuesta
        response.call_on_close(lambda: os.remove(filepath))
        return response
    
    except Exception as e:
        flash(f"Error al exportar PDF: {str(e)}", "danger")
        return redirect(url_for('index'))

# Exportar a Excel
@app.route('/exportar_excel')
def exportar_excel_route():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta completa con joins
        cursor.execute("""
        SELECT l.titulo, u.nombre, p.fecha_prestamo, 
               p.fecha_devolucion, p.dias_atraso, e.nombre as editorial
        FROM Prestamo p
        JOIN Ejemplar ej ON p.id_ejemplar = ej.id_ejemplar
        JOIN Libro l ON ej.id_libro = l.id_libro
        JOIN Usuario u ON p.id_usuario = u.id_usuario
        JOIN Editorial e ON l.id_editorial = e.id_editorial
        ORDER BY p.fecha_prestamo DESC
        """)
        data = cursor.fetchall()
        conn.close()
        
        filename = f"reporte_prestamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = exportar_excel(data, filename)
        
        # Enviar el archivo y luego eliminarlo
        response = send_file(
            filepath,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Programar eliminación después de la respuesta
        response.call_on_close(lambda: os.remove(filepath))
        return response
    
    except Exception as e:
        flash(f"Error al exportar Excel: {str(e)}", "danger")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)