#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Etiquetas PDF para Socios
Formato: MULTI3 Ref. 4704 (70 x 37 mm)
Layout: 3 columnas x 8 filas = 24 etiquetas por hoja A4

Autor: Sistema de Gestión COJUB
Fecha: Diciembre 2024
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class EtiquetasGenerator:
    """Generador de etiquetas para socios en formato MULTI3 4704."""
    
    # Especificaciones MULTI3 4704
    ETIQUETA_ANCHO = 70 * mm
    ETIQUETA_ALTO = 37 * mm
    
    # Distribución en hoja A4
    COLUMNAS = 3
    FILAS = 8
    ETIQUETAS_POR_HOJA = COLUMNAS * FILAS  # 24
    
    # Márgenes de la hoja (ajustables según la impresora)
    MARGEN_IZQUIERDO = 0 * mm
    MARGEN_SUPERIOR = 10.5 * mm
    
    # Espaciado entre etiquetas
    ESPACIO_HORIZONTAL = 0 * mm
    ESPACIO_VERTICAL = 0 * mm
    
    # Márgenes internos de la etiqueta (padding)
    PADDING_IZQUIERDO = 3 * mm
    PADDING_SUPERIOR = 3 * mm
    
    # Tamaños de fuente
    FUENTE_NOMBRE = 10
    FUENTE_DIRECCION = 9
    FUENTE_POBLACION = 9
    
    # Espaciado entre líneas
    INTERLINEADO = 3.5 * mm
    
    def __init__(self):
        """Inicializa el generador de etiquetas."""
        self.page_width, self.page_height = A4
        
    def filtrar_socios_unicos(self, socios):
        """
        Filtra socios para eliminar direcciones duplicadas (misma familia).
        
        Args:
            socios: Lista de objetos Socio
            
        Returns:
            Lista de socios con direcciones únicas
        """
        direcciones_vistas = set()
        socios_unicos = []
        
        for socio in socios:
            # Solo socios activos (no dados de baja)
            if socio.bBaixa:
                continue
            
            # Crear clave única basada en dirección normalizada
            direccion_normalizada = f"{socio.FAMAdressa.strip().lower()}|{socio.FAMCodPos.strip()}|{socio.FAMPoblacio.strip().lower()}"
            
            if direccion_normalizada not in direcciones_vistas:
                direcciones_vistas.add(direccion_normalizada)
                socios_unicos.append(socio)
        
        return socios_unicos
    
    def calcular_posicion_etiqueta(self, indice):
        """
        Calcula la posición X, Y de una etiqueta según su índice.
        
        Args:
            indice: Índice de la etiqueta en la hoja (0-23)
            
        Returns:
            Tupla (x, y) con la posición de la esquina inferior izquierda
        """
        # Calcular fila y columna
        fila = indice // self.COLUMNAS
        columna = indice % self.COLUMNAS
        
        # Calcular posición X (de izquierda a derecha)
        x = self.MARGEN_IZQUIERDO + columna * (self.ETIQUETA_ANCHO + self.ESPACIO_HORIZONTAL)
        
        # Calcular posición Y (de arriba hacia abajo en coordenadas PDF)
        # En PDF, Y=0 está abajo, por eso restamos desde el top
        y = self.page_height - self.MARGEN_SUPERIOR - (fila + 1) * (self.ETIQUETA_ALTO + self.ESPACIO_VERTICAL)
        
        return x, y
    
    def dibujar_etiqueta(self, c, socio, x, y):
        """
        Dibuja una etiqueta individual con los datos del socio.
        
        Args:
            c: Canvas de ReportLab
            socio: Objeto Socio con los datos
            x, y: Coordenadas de la esquina inferior izquierda de la etiqueta
        """
        # Posición inicial del texto (con padding)
        texto_x = x + self.PADDING_IZQUIERDO
        texto_y = y + self.ETIQUETA_ALTO - self.PADDING_SUPERIOR
        
        # LÍNEA 1: Nombre (negrita)
        c.setFont("Helvetica-Bold", self.FUENTE_NOMBRE)
        nombre = socio.FAMNom.strip()
        if len(nombre) > 35:  # Truncar si es muy largo
            nombre = nombre[:32] + "..."
        c.drawString(texto_x, texto_y, nombre)
        texto_y -= self.INTERLINEADO
        
        # LÍNEA 2: Dirección
        c.setFont("Helvetica", self.FUENTE_DIRECCION)
        direccion = socio.FAMAdressa.strip()
        if len(direccion) > 40:  # Truncar si es muy largo
            direccion = direccion[:37] + "..."
        c.drawString(texto_x, texto_y, direccion)
        texto_y -= self.INTERLINEADO
        
        # LÍNEA 3: Código Postal - Población
        c.setFont("Helvetica", self.FUENTE_POBLACION)
        cod_postal = socio.FAMCodPos.strip()
        poblacion = socio.FAMPoblacio.strip()
        
        # Formatear código postal con ceros a la izquierda si es necesario
        if cod_postal.isdigit() and len(cod_postal) < 5:
            cod_postal = cod_postal.zfill(5)
        
        linea3 = f"{cod_postal} {poblacion}"
        if len(linea3) > 40:
            linea3 = linea3[:37] + "..."
        c.drawString(texto_x, texto_y, linea3)
        
        # DEBUG: Dibujar bordes de la etiqueta (comentar en producción)
        # c.setStrokeColor(black)
        # c.setLineWidth(0.5)
        # c.rect(x, y, self.ETIQUETA_ANCHO, self.ETIQUETA_ALTO)
    
    def generar_etiquetas(self, socios, filepath):
        """
        Genera el PDF con las etiquetas de los socios.
        
        Args:
            socios: Lista de objetos Socio
            filepath: Ruta donde guardar el PDF
            
        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            # Filtrar socios únicos (sin duplicados de dirección)
            socios_unicos = self.filtrar_socios_unicos(socios)
            
            if not socios_unicos:
                print("⚠️  No hay socios para generar etiquetas")
                return False
            
            print(f"📊 Total de socios activos: {len([s for s in socios if not s.bBaixa])}")
            print(f"📊 Etiquetas a generar (sin duplicados): {len(socios_unicos)}")
            
            # Crear el PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            c.setTitle("Etiquetas de Socios")
            
            # Contador de etiquetas
            etiqueta_actual = 0
            pagina_actual = 1
            
            for socio in socios_unicos:
                # Si hemos llenado una hoja completa, crear nueva página
                if etiqueta_actual > 0 and etiqueta_actual % self.ETIQUETAS_POR_HOJA == 0:
                    c.showPage()
                    pagina_actual += 1
                    print(f"📄 Página {pagina_actual} iniciada")
                
                # Calcular posición en la hoja actual
                indice_en_hoja = etiqueta_actual % self.ETIQUETAS_POR_HOJA
                x, y = self.calcular_posicion_etiqueta(indice_en_hoja)
                
                # Dibujar la etiqueta
                self.dibujar_etiqueta(c, socio, x, y)
                
                etiqueta_actual += 1
            
            # Guardar el PDF
            c.save()
            
            print(f"\n✅ PDF generado correctamente:")
            print(f"   📄 Total de páginas: {pagina_actual}")
            print(f"   🏷️  Total de etiquetas: {etiqueta_actual}")
            print(f"   📁 Archivo: {filepath}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al generar etiquetas: {e}")
            import traceback
            traceback.print_exc()
            return False


# ============================================================================
# Función auxiliar para usar desde el ViewModel
# ============================================================================

def generar_etiquetas_socios(socios, filepath):
    """
    Función auxiliar para generar etiquetas de socios.
    
    Args:
        socios: Lista de objetos Socio
        filepath: Ruta donde guardar el PDF
        
    Returns:
        True si se generó correctamente, False en caso contrario
    """
    generator = EtiquetasGenerator()
    return generator.generar_etiquetas(socios, filepath)


# ============================================================================
# EJEMPLO DE USO (para testing)
# ============================================================================

if __name__ == "__main__":
    from collections import namedtuple
    
    # Definir estructura Socio (simplificada para testing)
    Socio = namedtuple('Socio', [
        'FAMID', 'FAMNom', 'FAMAdressa', 'FAMPoblacio', 'FAMCodPos',
        'FAMTelefon', 'FAMMobil', 'FAMEmail', 'FAMDataAlta', 'FAMIBAN',
        'FAMBIC', 'FAMObservacions', 'FAMNIF', 'FAMDataNaixement',
        'FAMQuota', 'FAMDataBaixa', 'FAMSexe', 'FAMSociReferencia',
        'FAMbPagamentDomiciliat', 'FAMbRebutCobrat', 'FAMPagamentFinestreta', 'bBaixa'
    ])
    
    # Crear socios de prueba
    socios_test = [
        Socio("1001", "Joan García Martínez", "Carrer Major, 25", "Barcelona", "08001",
              "934567890", "612345678", "joan@example.com", None, "ES1234567890",
              "CAIXESBB", "", "12345678A", None, 50.0, None, "H", "",
              True, False, False, False),
        Socio("1002", "Maria López Sánchez", "Carrer Major, 25", "Barcelona", "08001",  # DUPLICADA
              "934567891", "612345679", "maria@example.com", None, "ES1234567891",
              "CAIXESBB", "", "12345678B", None, 50.0, None, "M", "1001",
              True, False, False, False),
        Socio("1003", "Pere Fernández Vila", "Avinguda Diagonal, 100", "Barcelona", "08019",
              "934567892", "612345680", "pere@example.com", None, "ES1234567892",
              "CAIXESBB", "", "12345678C", None, 50.0, None, "H", "",
              True, False, False, False),
        Socio("1004", "Anna Rodríguez Pons", "Carrer Balmes, 45", "Barcelona", "08007",
              "934567893", "612345681", "anna@example.com", None, "ES1234567893",
              "CAIXESBB", "", "12345678D", None, 50.0, None, "M", "",
              True, False, False, False),
        Socio("1005", "Carles Soler Ribas", "Carrer de Sants, 200", "Barcelona", "08014",
              "934567894", "612345682", "carles@example.com", None, "ES1234567894",
              "CAIXESBB", "", "12345678E", None, 50.0, None, "H", "",
              True, False, False, True),  # DADO DE BAJA - NO APARECERÁ
    ]
    
    # Generar etiquetas de prueba
    print("\n" + "="*70)
    print("🏷️  GENERADOR DE ETIQUETAS - PRUEBA")
    print("="*70)
    
    generator = EtiquetasGenerator()
    generator.generar_etiquetas(socios_test, "etiquetas_prueba.pdf")
    
    print("\n" + "="*70)
    print("✅ PRUEBA COMPLETADA")
    print("="*70)
    print("\n💡 Resultado esperado:")
    print("   - Total socios activos: 4 (uno está de baja)")
    print("   - Etiquetas generadas: 3 (dos comparten dirección)")
    print("   - Archivo: etiquetas_prueba.pdf")
    print("\n📋 Etiquetas que deben aparecer:")
    print("   1. Joan García Martínez - Carrer Major, 25")
    print("   2. Pere Fernández Vila - Avinguda Diagonal, 100")
    print("   3. Anna Rodríguez Pons - Carrer Balmes, 45")
    print("\n❌ NO debe aparecer:")
    print("   - Maria López Sánchez (dirección duplicada)")
    print("   - Carles Soler Ribas (dado de baja)")
    print()