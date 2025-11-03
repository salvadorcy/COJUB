#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de PDFs Tabular - Sistema COJUB
==========================================
Genera reportes PDF en formato tabular profesional en tamaño DIN A4.

Mejoras:
- Formato A4 (210 x 297 mm)
- Tipografía compacta (6pt datos, 7pt encabezados)
- Sin líneas verticales ni horizontales (solo bajo encabezado)
- Incluye fecha de alta
- Filas alternadas para legibilidad
- Sobrescritura automática

Autor: Sistema de Gestión COJUB
Fecha: 2024
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


class PdfGeneratorTabular:
    """Generador de reportes PDF en formato tabular."""
    
    def __init__(self):
        """Inicializa el generador de PDFs."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados."""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='TituloCustom',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubtituloCustom',
            parent=self.styles['Heading2'],
            fontSize=10,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para información de fecha
        self.styles.add(ParagraphStyle(
            name='FechaCustom',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
    
    def _create_header(self, titulo):
        """
        Crea el encabezado del documento.
        
        Args:
            titulo (str): Título del reporte
            
        Returns:
            list: Lista de elementos del encabezado
        """
        story = []
        
        # Título principal
        story.append(Paragraph(titulo, self.styles['TituloCustom']))
        
        # Fecha de generación
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
        story.append(Paragraph(f'Generado el: {fecha_actual}', self.styles['FechaCustom']))
        story.append(Spacer(1, 0.4*cm))
        
        return story
    
    def generate_general_report(self, socios, socis_map, filepath):
        """
        Genera un listado general de socios en formato tabular.
        Si el archivo existe, lo sobrescribe automáticamente.
        
        Args:
            socios (list): Lista de socios a incluir
            socis_map (dict): Mapa de ID a nombre para soci parella
            filepath (str): Ruta donde guardar el PDF
        """
        # Eliminar archivo existente si existe
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"ℹ️ Archivo existente eliminado: {filepath}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo existente: {e}")
        
        # Crear documento en HORIZONTAL (landscape)
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),  # A4 horizontal
            rightMargin=1.2*cm,
            leftMargin=1.2*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # Encabezado
        story.extend(self._create_header('LLISTAT GENERAL DE SOCIS'))
        story.append(Paragraph(f'Total socis: {len(socios)}', self.styles['SubtituloCustom']))
        story.append(Spacer(1, 0.2*cm))
        
        # Encabezados de la tabla
        headers = [
            'ID',
            'Data Alta',
            'Nom',
            'NIF',
            'Adreça',
            'Població',
            'CP',
            'Telèfon',
            'Mòbil',
            'Email'
        ]
        
        # Preparar datos de la tabla
        data = [headers]
        
        for socio in socios:
            # Formatear datos - CORREGIR acceso a fecha de alta
            # Probar diferentes nombres de campo posibles
            data_alta = ''
            if hasattr(socio, 'FAMDataAlta') and socio.FAMDataAlta:
                data_alta = socio.FAMDataAlta.strftime('%d/%m/%Y')
            elif hasattr(socio, 'dDataAlta') and socio.dDataAlta:
                data_alta = socio.dDataAlta.strftime('%d/%m/%Y')
            elif hasattr(socio, 'FAMDataAlta'):
                try:
                    if socio.FAMDataAlta:
                        data_alta = socio.FAMDataAlta.strftime('%d/%m/%Y')
                except:
                    data_alta = ''
            
            nombre = socio.FAMNom or ''
            nif = socio.FAMNIF or ''
            direccion = socio.FAMAdressa or ''
            poblacion = socio.FAMPoblacio or ''
            cp = socio.FAMCodPos or ''
            
            # Agregar '0' delante del CP si es necesario (08240 en lugar de 8240)
            if cp and cp.isdigit() and len(cp) == 4:
                cp = '0' + cp
            elif cp and not cp.startswith('0') and len(cp) < 5:
                cp = cp.zfill(5)  # Rellenar con ceros a la izquierda hasta 5 dígitos
            
            telefono = socio.FAMTelefon or ''
            movil = socio.FAMMobil or ''
            email = socio.FAMEmail or ''
            
            # Truncar textos largos - AUMENTAR límites para horizontal
            if len(nombre) > 45:
                nombre = nombre[:42] + '...'
            if len(direccion) > 48:
                direccion = direccion[:45] + '...'
            if len(poblacion) > 30:
                poblacion = poblacion[:27] + '...'
            if len(email) > 30:
                email = email[:27] + '...'
            
            row = [
                str(socio.FAMID),
                data_alta,
                nombre,
                nif,
                direccion,
                poblacion,
                cp,
                telefono,
                movil,
                email
            ]
            data.append(row)
        
        # Anchos de columna para A4 HORIZONTAL (29.7cm disponible)
        col_widths = [
            0.8*cm,   # ID
            1.5*cm,   # Data Alta
            5.5*cm,   # Nombre (AUMENTADO - prioridad)
            2.0*cm,   # NIF
            5.5*cm,   # Dirección (AUMENTADO - prioridad)
            3.5*cm,   # Población (AUMENTADO)
            1.2*cm,   # CP (con 5 dígitos)
            2.0*cm,   # Teléfono
            2.0*cm,   # Móvil
            2.5*cm    # Email
        ]
        
        # Crear tabla
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla - SIN LÍNEAS VERTICALES NI HORIZONTALES
        table_style = TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),  # Tamaño reducido
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Fecha centrada
            ('ALIGN', (2, 1), (-1, -1), 'LEFT'),   # Resto a la izquierda
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 6),  # Tamaño reducido
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            
            # SOLO línea debajo del encabezado
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2c3e50')),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Generar PDF
        doc.build(story)
        print(f"✓ Listado general generado: {filepath}")
    
    def generate_banking_report(self, socios, socis_map, filepath):
        """
        Genera un listado de datos bancarios en formato tabular.
        Si el archivo existe, lo sobrescribe automáticamente.
        
        Args:
            socios (list): Lista de socios a incluir
            socis_map (dict): Mapa de ID a nombre para soci parella
            filepath (str): Ruta donde guardar el PDF
        """
        # Eliminar archivo existente si existe
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"ℹ️ Archivo existente eliminado: {filepath}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo existente: {e}")
        
        # Filtrar solo socios con datos bancarios
        socios_con_banco = [s for s in socios if s.FAMIBAN and s.FAMIBAN.strip()]
        
        # Crear documento
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Encabezado
        story.extend(self._create_header('LLISTAT DE DADES BANCÀRIES'))
        story.append(Paragraph(
            f'Total de socis amb dades bancàries: {len(socios_con_banco)}',
            self.styles['SubtituloCustom']
        ))
        story.append(Spacer(1, 0.3*cm))
        
        # Encabezados de la tabla
        headers = [
            'ID',
            'Nom',
            'NIF',
            'IBAN',
            'BIC',
            'Domiciliat'
        ]
        
        # Preparar datos
        data = [headers]
        
        for socio in socios_con_banco:
            nombre = socio.FAMNom or ''
            nif = socio.FAMNIF or ''
            iban = socio.FAMIBAN or ''
            bic = socio.FAMBIC or ''
            domiciliado = 'Sí' if socio.FAMbPagamentDomiciliat else 'No'
            
            # Truncar nombre si es muy largo
            if len(nombre) > 35:
                nombre = nombre[:32] + '...'
            
            row = [
                str(socio.FAMID),
                nombre,
                nif,
                iban,
                bic,
                domiciliado
            ]
            data.append(row)
        
        # Anchos de columna optimizados
        col_widths = [
            1.0*cm,   # ID
            4.5*cm,   # Nombre
            2.3*cm,   # NIF
            5.5*cm,   # IBAN
            2.3*cm,   # BIC
            1.8*cm    # Domiciliado
        ]
        
        # Crear tabla
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla
        table_style = TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Domiciliado centrado
            ('ALIGN', (1, 1), (4, -1), 'LEFT'),    # Resto a la izquierda
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#27ae60')),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f8f5')])
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Nota al pie
        story.append(Spacer(1, 0.5*cm))
        nota_style = ParagraphStyle(
            name='Nota',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique'
        )
        story.append(Paragraph(
            '<b>Nota:</b> Aquest llistat inclou únicament socis actius amb dades bancàries registrades.',
            nota_style
        ))
        
        # Generar PDF
        doc.build(story)
        print(f"✓ Listado bancario generado: {filepath}")
    
    def generate_sepa_report(self, socios, dades, filepath):
        """
        Genera un reporte de socios para remesa SEPA.
        Si el archivo existe, lo sobrescribe automáticamente.
        
        Args:
            socios (list): Lista de socios para la remesa
            dades: Datos del presentador
            filepath (str): Ruta donde guardar el PDF
        """
        # Eliminar archivo existente si existe
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"ℹ️ Archivo existente eliminado: {filepath}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo existente: {e}")
        
        # Filtrar socios con pago domiciliado y activos
        socios_sepa = [
            s for s in socios 
            if s.FAMbPagamentDomiciliat and not s.bBaixa and s.FAMIBAN and s.FAMIBAN.strip()
        ]
        
        # Calcular total
        total_cuota = sum(float(s.FAMQuota or 0) for s in socios_sepa)
        
        # Crear documento
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Encabezado
        story.extend(self._create_header('REMESA SEPA - LLISTAT DE DOMICILIACIONS'))
        
        # Información del presentador
        if dades:
            info_presentador = f"""
            <b>Presentador:</b> {dades.DADESNom or 'N/A'}<br/>
            <b>NIF:</b> {dades.DADESNIF or 'N/A'}<br/>
            <b>IBAN:</b> {dades.DADESIBAN or 'N/A'}
            """
            story.append(Paragraph(info_presentador, self.styles['Normal']))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            f'<b>Total de socis:</b> {len(socios_sepa)} | <b>Import total:</b> {total_cuota:.2f} €',
            self.styles['SubtituloCustom']
        ))
        story.append(Spacer(1, 0.3*cm))
        
        # Encabezados
        headers = [
            'ID',
            'Nom',
            'NIF',
            'IBAN',
            'Quota (€)'
        ]
        
        # Datos
        data = [headers]
        
        for socio in socios_sepa:
            nombre = socio.FAMNom or ''
            if len(nombre) > 40:
                nombre = nombre[:37] + '...'
            
            row = [
                str(socio.FAMID),
                nombre,
                socio.FAMNIF or '',
                socio.FAMIBAN or '',
                f"{float(socio.FAMQuota or 0):.2f}"
            ]
            data.append(row)
        
        # Fila de total
        data.append(['', '', '', 'TOTAL:', f"{total_cuota:.2f}"])
        
        # Anchos de columna
        col_widths = [
            1.0*cm,   # ID
            5.5*cm,   # Nombre
            2.3*cm,   # NIF
            5.5*cm,   # IBAN
            2.0*cm    # Cuota
        ]
        
        # Crear tabla
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Estilo
        table_style = TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # ID
            ('ALIGN', (4, 1), (4, -2), 'RIGHT'),   # Cuota
            ('ALIGN', (1, 1), (3, -2), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 7),
            
            # Fila de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('ALIGN', (3, -1), (3, -1), 'RIGHT'),
            ('ALIGN', (4, -1), (4, -1), 'RIGHT'),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#3498db')),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#ebf5fb')])
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Generar PDF
        doc.build(story)
        print(f"✓ Reporte SEPA generado: {filepath}")


# Para mantener compatibilidad con código existente
class PdfGenerator(PdfGeneratorTabular):
    """Alias para mantener compatibilidad con código anterior."""
    pass


if __name__ == "__main__":
    print("Generador de PDFs Tabular - Sistema COJUB")
    print("Importa esta clase en tu viewmodel para usarla")