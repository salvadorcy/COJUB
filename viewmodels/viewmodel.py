import pyodbc
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime
from collections import namedtuple
from utils.sepa_lib import generar_xml_sepa
from .pdf_generator import PdfGenerator,PdfGeneratorTabular
from .report_generator import ReportGenerator
from .etiquetas_generator import generar_etiquetas_socios

# ============================================================================
# ESTRUCTURA CORREGIDA - 22 campos (DEBE COINCIDIR CON model.py)
# ============================================================================
Socio = namedtuple('Socio', [
    'FAMID',
    'FAMNom',
    'FAMAdressa',
    'FAMPoblacio',
    'FAMCodPos',
    'FAMTelefon',
    'FAMMobil',
    'FAMEmail',
    'FAMDataAlta',
    'FAMIBAN',
    'FAMBIC',
    'bBaixa',
    'FAMObservacions',
    'FAMNIF',
    'FAMDataNaixement',
    'FAMQuota',
    'FAMDataBaixa',
    'FAMSexe',
    'FAMSociReferencia',
    'FAMbPagamentDomiciliat',
    'FAMbRebutCobrat',
    'FAMPagamentFinestreta',
    'FAMTelefonEmergencia'
])

Dades = namedtuple('Dades', [
    'Presentador', 'CIFPresentador', 'Ordenant', 'CIFOrdenant',
    'IBANPresentador', 'BICPresentador', 'QuotaSocis',
    'SufixeRebuts', 'TexteRebutFinestreta'
])

class ViewModel(QObject):
    """
    ViewModel actúa como intermediario entre el Modelo (Model) y la Vista (View).
    Contiene la lógica de presentación y el estado de la aplicación.
    """
    socis_changed = pyqtSignal()
    dades_changed = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.all_socis = []
        self.filtered_socis = []
        self.socis_map = {}  # Diccionario para buscar socios por ID
        self.dades = None
        self.selected_socio = None
        self.search_text = ""
        self.filter_finestreta_enabled = False
        self.filter_baixa_enabled = False

    def load_data(self):
        """Carga todos los datos de socios y de configuración del modelo."""
        self.all_socis = self.model.get_all_socis()
        self.dades = self.model.get_dades()
        # Crear el mapa de socios para búsquedas rápidas
        self.socis_map = {socio.FAMID: socio.FAMNom for socio in self.all_socis}
        self.update_filtered_socis()
        self.dades_changed.emit()

    def update_filtered_socis(self):
        """Aplica los filtros de búsqueda y otros a la lista de socios."""
        socis = self.all_socis

        # Aplicar filtro de baja (por defecto no se muestran los socios dados de baja)
        if not self.filter_baixa_enabled:
            socis = [s for s in socis if not s.bBaixa]

        # Aplicar filtro de búsqueda de texto
        text = (self.search_text or "").strip().lower()
        if text:
            socis = [
                s for s in socis
                if text in ((s.FAMID or "").lower())
                or text in ((s.FAMNom or "").lower())
            ]

        # Aplicar filtro de pago por ventanilla
        if self.filter_finestreta_enabled:
            socis = [s for s in socis if s.FAMPagamentFinestreta]

        self.filtered_socis = socis
        self.socis_changed.emit()

    def filter_socis(self, text):
        """Actualiza el texto de búsqueda y filtra la lista."""
        self.search_text = text
        self.update_filtered_socis()
    
    def toggle_finestreta_filter(self, state):
        """Activa o desactiva el filtro de pago por ventanilla."""
        self.filter_finestreta_enabled = bool(state)
        self.update_filtered_socis()
        
    def toggle_baixa_filter(self, state):
        """Activa o desactiva el filtro para mostrar a los socios dados de baja."""
        self.filter_baixa_enabled = bool(state)
        self.update_filtered_socis()

    def get_socis(self):
        """Devuelve la lista de socios filtrada para mostrar en la vista."""
        return self.filtered_socis

    def get_socio_full_name(self, socio_id):
        """Busca y devuelve el nombre completo de un socio por su ID."""
        if not socio_id:
            return ""
        try:
            socio = next(s for s in self.all_socis if s.FAMID == socio_id.strip())
            return socio.FAMNom
        except StopIteration:
            return ""

    def set_selected_socio(self, row_index):
        """Establece el socio seleccionado a partir del índice de la fila."""
        if row_index is not None and 0 <= row_index < len(self.filtered_socis):
            self.selected_socio = self.filtered_socis[row_index]
        else:
            self.selected_socio = None

    def get_selected_socio_data(self):
        """Devuelve los datos del socio seleccionado en formato de tupla."""
        if self.selected_socio:
            return self.selected_socio
        return None

    def save_socio(self, data, original_fam_id=None):
        """Guarda o actualiza un socio en la base de datos."""
        print(f"DEBUG save_socio: original_fam_id={original_fam_id!r}, new_id={data[0]!r}")
        try:
            new_id = (data[0] or "").strip()
            if not new_id:
                print("Error: FAMID vacío")
                return False

            old_id = (original_fam_id or "").strip() if original_fam_id else None

            # =========================
            # EDICIÓN
            # =========================
            if old_id:
                # Si cambió el ID -> validar y renombrar
                if new_id != old_id:
                    if self.model.socio_exists(new_id):
                        print(f"Error: ya existe un socio con el ID {new_id}")
                        return False

                    # OJO: rename_socio(old_id, new_id)
                    if not self.model.rename_socio(old_id, new_id):
                        return False

                # En edición SIEMPRE update, NUNCA add
                success = self.model.update_socio(data)

            # =========================
            # ALTA
            # =========================
            else:
                if self.model.socio_exists(new_id):
                    print(f"Error: ya existe un socio con el ID {new_id}")
                    return False

                success = self.model.add_socio(data)

            if success:
                self.load_data()

            return success

        except Exception as e:
            print(f"ERROR save_socio: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def delete_selected_socio(self):
        """Elimina el socio seleccionado de la base de datos."""
        if self.selected_socio:
            success = self.model.delete_socio(self.selected_socio.FAMID)
            if success:
                self.load_data()  # Recargar datos después de eliminar
            return success
        return False
        
    def get_dades_data(self):
        """Devuelve los datos de configuración."""
        if self.dades:
            return self.dades
        return None
        
    def save_dades(self, data):
        """Guarda los datos de configuración y replica QuotaSocis a todos los socios si cambia."""
        # Quota anterior (lo que había antes de guardar)
        old_quota = self.dades.QuotaSocis if self.dades else None

        success = self.model.update_dades(data)
        if not success:
            return False

        # Quota nueva (viene del dialog y está en el campo QuotaSocis)
        # En DadesDialog.get_data() QuotaSocis se convierte a float, así que aquí ya llega como float.
        try:
            new_quota = float(data[12])  # índice 12 = "QuotaSocis"
        except Exception:
            new_quota = None

        # Si la quota ha cambiado -> replicar a socios (por defecto solo activos)
        if new_quota is not None and new_quota != old_quota:
            self.model.set_quota_for_all_socis(new_quota, only_active=True)

        # Recargar todo para reflejar cambios en UI y tabla
        self.load_data()
        return True
    
    def generate_general_report(self, filepath, orden_alfabetic=True):
        """
        Genera el informe general de socios.

        Args:
            filepath: Ruta del archivo PDF
            orden_alfabetic: True para orden alfabético, False para orden por número
        """
        try:
            # Filtrar solo socios activos
            socis_actius = [s for s in self.all_socis if not s.bBaixa]

            # Función auxiliar para ordenar sin petar con None
            def safe_text(value):
                return (str(value).strip().lower() if value is not None else "")

            # Ordenar según parámetro
            if orden_alfabetic:
                # Orden alfabético: por nombre y dirección (ambos seguros ante None)
                socis_ordenats = sorted(
                    socis_actius,
                    key=lambda s: (
                        safe_text(getattr(s, "FAMNom", None)),
                        safe_text(getattr(s, "FAMAdressa", None)),
                        safe_text(getattr(s, "FAMID", None)),
                    )
                )
            else:
                # Orden por número de socio (FAMID) (seguro ante None)
                socis_ordenats = sorted(
                    socis_actius,
                    key=lambda s: safe_text(getattr(s, "FAMID", None))
                )

            # Generar PDF con los socios ordenados
            generator = PdfGenerator()
            generator.dades = self.dades
            generator.generate_general_report(socis_ordenats, self.dades, filepath)
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_banking_report(self, filepath):
        try:
            socis_actius = [s for s in self.all_socis if not s.bBaixa]

            generator = PdfGeneratorTabular()
            generator.dades = self.dades
            generator.generate_banking_report(socis_actius, self.dades, filepath)

            return True
        except Exception as e:
            print(f"Error al generar el listado bancario: {e}")
            return False
    def generate_etiquetas(self, filepath):
        """
        Genera etiquetas en PDF para los socios.
        
        Características:
        - Solo socios activos (no dados de baja)
        - Sin duplicados de dirección (misma familia)
        - Formato MULTI3 4704 (70 x 37 mm)
        - 3 columnas x 8 filas = 24 etiquetas por hoja A4
        
        Args:
            filepath: Ruta donde guardar el PDF
            
        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            # Usar todos los socios (no solo los filtrados)
            # El generador ya filtra activos y duplicados
            success = generar_etiquetas_socios(self.all_socis, filepath)
            return success
        except Exception as e:
            print(f"Error al generar etiquetas: {e}")
            return False
    
    def generar_remesa_sepa(self, filename):
        """
        Genera el archivo de remesa SEPA a partir de los socios a domiciliar
        y los datos de configuración.
        """
        if not self.dades:
            print("Error: No se han cargado los datos de configuración (G_Dades).")
            return False
            
        socios_a_domiciliar = [s for s in self.all_socis if s.FAMbPagamentDomiciliat and not s.bBaixa]
        
        if not socios_a_domiciliar:
            print("No hay socios para generar la remesa SEPA.")
            return False
            
        try:
            generar_xml_sepa(self.dades, socios_a_domiciliar, filename)
            print(f"Remesa SEPA generada correctamente en '{filename}'.")
            return True
        except Exception as e:
            print(f"Error al generar la remesa SEPA: {e}")
            return False