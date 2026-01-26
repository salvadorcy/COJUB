from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models.activitat import Activitat, ActivitatInscripcio
from typing import List
from datetime import datetime
import os

def generate_activitat_report(activitat: Activitat, inscripcions: List[ActivitatInscripcio]) -> str:
    """Genera un PDF con el listado de inscritos a una actividad"""
    
    # Crear directorio si no existe
    output_dir = "reports_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"activitat_{activitat.id}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Crear documento
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Elementos del PDF
    elements = []
    
    # Título
    elements.append(Paragraph("Llistat d'Inscrits a l'Activitat", title_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Información de la actividad
    info_text = f"""
    <b>Activitat:</b> {activitat.descripcio}<br/>
    <b>Data Inici:</b> {activitat.data_inici.strftime('%d/%m/%Y') if activitat.data_inici else 'N/A'}<br/>
    <b>Data Fi:</b> {activitat.data_fi.strftime('%d/%m/%Y') if activitat.data_fi else 'N/A'}<br/>
    <b>Preu Soci:</b> {activitat.preu_soci:.2f} €<br/>
    <b>Preu No Soci:</b> {activitat.preu_no_soci:.2f} €
    """
    elements.append(Paragraph(info_text, subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Estadísticas
    total_inscrits = len(inscripcions)
    total_pagats = sum(1 for i in inscripcions if i.pagat)
    total_recaptat = sum(i.import_pagat for i in inscripcions if i.pagat and i.import_pagat)
    
    stats_text = f"""
    <b>Total Inscrits:</b> {total_inscrits} | 
    <b>Pagats:</b> {total_pagats} | 
    <b>Recaptat:</b> {total_recaptat:.2f} €
    """
    elements.append(Paragraph(stats_text, subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabla de inscritos
    if inscripcions:
        # Encabezados
        data = [['NIF', 'Nom i Cognoms', 'Tipus', 'Import', 'Pagat']]
        
        # Datos
        for inscripcio in inscripcions:
            nom_complet = f"{inscripcio.nom_soci} {inscripcio.cognoms_soci}"
            tipus = "Soci" if inscripcio.es_soci else "No Soci"
            import_text = f"{inscripcio.import_pagat:.2f} €" if inscripcio.import_pagat else ""
            pagat_text = "Sí" if inscripcio.pagat else "No"
            
            data.append([
                inscripcio.nif_soci,
                nom_complet,
                tipus,
                import_text,
                pagat_text
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[3*cm, 7*cm, 2.5*cm, 2.5*cm, 2*cm])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No hi ha inscrits en aquesta activitat", subtitle_style))
    
    # Pie de página
    elements.append(Spacer(1, 1*cm))
    footer_text = f"Generat el {datetime.now().strftime('%d/%m/%Y a les %H:%M')}"
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], 
                                  fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(footer_text, footer_style))
    
    # Generar PDF
    doc.build(elements)
    
    return filepath