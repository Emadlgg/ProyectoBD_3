// Función para inicializar gráfica de barras
function initGraficaLibros(libros, prestamos) {
    const ctx = document.getElementById('graficaLibros');
    
    // Destruir gráfica existente si hay una
    if (window.librosChart) {
        window.librosChart.destroy();
    }
    
    window.librosChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: libros,
            datasets: [{
                label: 'Número de préstamos',
                data: prestamos,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Préstamos: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Validación de fechas en el formulario
function validarFechas() {
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]');
    const fechaFin = document.querySelector('input[name="fecha_fin"]');
    
    if (fechaInicio.value && fechaFin.value && fechaInicio.value > fechaFin.value) {
        alert('Error: La fecha de inicio no puede ser mayor a la fecha final');
        return false;
    }
    return true;
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar gráfica si existe
    if (document.getElementById('graficaLibros')) {
        try {
            const librosData = JSON.parse(document.getElementById('libros-data').textContent);
            const prestamosData = JSON.parse(document.getElementById('prestamos-data').textContent);
            initGraficaLibros(librosData, prestamosData);
        } catch (e) {
            console.error("Error al cargar datos para gráfica:", e);
        }
    }
    
    // Validar fechas al enviar formulario
    const formReporte = document.querySelector('form[action="/generar_reporte"]');
    if (formReporte) {
        formReporte.addEventListener('submit', function(e) {
            if (!validarFechas()) {
                e.preventDefault();
            }
        });
    }
    
    // Formatear fechas para mostrar placeholder hoy-7 días / hoy
    const hoy = new Date().toISOString().split('T')[0];
    const hace7Dias = new Date();
    hace7Dias.setDate(hace7Dias.getDate() - 7);
    const hace7DiasStr = hace7Dias.toISOString().split('T')[0];
    
    document.querySelector('input[name="fecha_inicio"]').value = hace7DiasStr;
    document.querySelector('input[name="fecha_fin"]').value = hoy;
});