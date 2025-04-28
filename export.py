import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Configurar directorio de exportación (relativo al archivo actual)
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Préstamos - Editorial', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def exportar_pdf(data, filename):
    try:
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Columnas
        column_widths = [60, 40, 30, 30, 20, 40]
        headers = ["Libro", "Usuario", "Fecha Préstamo", "Fecha Devolución", "Atraso", "Editorial"]
        
        # Cabeceras
        for i, header in enumerate(headers):
            pdf.cell(column_widths[i], 10, header, border=1, align='C')
        pdf.ln()
        
        # Datos
        for row in data:
            for i, item in enumerate(row):
                if isinstance(item, datetime):
                    item = item.strftime('%d/%m/%Y')
                pdf.cell(column_widths[i], 10, str(item), border=1)
            pdf.ln()
        
        pdf.output(filepath)
        return filepath
    
    except Exception as e:
        raise Exception(f"Error al generar PDF: {str(e)}")

def exportar_excel(data, filename):
    try:
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        df = pd.DataFrame(data, columns=[
            "Libro", "Usuario", "Fecha Préstamo", 
            "Fecha Devolución", "Días Atraso", "Editorial"
        ])
        
        # Formatear fechas
        for col in ['Fecha Préstamo', 'Fecha Devolución']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y')
        
        df.to_excel(
            filepath,
            index=False,
            engine='openpyxl',
            sheet_name='Préstamos'
        )
        return filepath
    
    except Exception as e:
        raise Exception(f"Error al generar Excel: {str(e)}")