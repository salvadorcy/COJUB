import pyodbc
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime
from collections import namedtuple
from utils.sepa_lib import generar_xml_sepa

# Definir la estructura de los datos del socio y de configuración
Socio = namedtuple('Socio', [
    'FAMID', 'FAMNom', 'FAMAdressa', 'FAMPoblacio', 'FAMCodPos', 'FAMTelefon',
    'FAMMobil', 'FAMEmail', 'FAMDataAlta', 'FAMCCC', 'FAMIBAN', 'FAMBIC',
    'FAMNSocis', 'bBaixa', 'FAMObservacions', 'FAMbSeccio', 'FAMNIF',
    'FAMDataNaixement', 'FAMQuota', 'FAMIDSec', 'FAMDataBaixa', 'FAMTipus',
    'FAMSexe', 'FAMSociReferencia', 'FAMNewId', 'FAMNewIdRef',
    'FAMbPagamentDomiciliat', 'FAMbRebutCobrat', 'FAMPagamentFinestreta'
])

Dades = namedtuple('Dades', [
    'TotalDefuncions', 'AcumulatDefuncions', 'PreuDerrama', 'ComissioBancaria',
    'IdFactura', 'Presentador', 'CIFPresentador', 'Ordenant', 'CIFOrdenant',
    'IBANPresentador', 'BICPresentador', 'PWD', 'QuotaSocis',
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
        self.dades = None
        self.selected_socio = None
        self.search_text = ""
        self.filter_finestreta_enabled = False
        self.filter_baixa_enabled = False

    def load_data(self):
        """Carga todos los datos de socios y de configuración del modelo."""
        self.all_socis = self.model.get_all_socis()
        self.dades = self.model.get_dades()
        self.update_filtered_socis()
        self.dades_changed.emit()

    def update_filtered_socis(self):
        """Aplica los filtros de búsqueda y otros a la lista de socios."""
        socis = self.all_socis
        # Aplicar filtro de baja (por defecto no se muestran los socios dados de baja)
        if not self.filter_baixa_enabled:
            socis = [s for s in socis if not s.bBaixa]
        # Aplicar filtro de búsqueda de texto
        if self.search_text:
            socis = [
                s for s in socis
                if self.search_text.lower() in s.FAMID.lower() or self.search_text.lower() in s.FAMNom.lower()
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

    def save_socio(self, data):
        """Guarda o actualiza un socio en la base de datos."""
        # Se asume que el primer elemento de la tupla es el FAMID
        fam_id = data[0]
        # Si el FAMID existe, es una actualización
        if self.model.socio_exists(fam_id):
            return self.model.update_socio(data)
        # Si no, es una nueva inserción
        else:
            return self.model.add_socio(data)
            
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
        """Guarda los datos de configuración en la base de datos."""
        success = self.model.update_dades(data)
        if success:
            self.load_data() # Recargar datos después de actualizar
        return success
    
    def generar_remesa_sepa(self, filename):
        """
        Genera el archivo de remesa SEPA a partir de los socios a domiciliar
        y los datos de configuración.
        """
        if not self.dades:
            print("Error: No se han cargado los datos de configuración (G_Dades).")
            return
            
        socios_a_domiciliar = [s for s in self.all_socis if s.FAMbPagamentDomiciliat]
        
        if not socios_a_domiciliar:
            print("No hay socios para generar la remesa SEPA.")
            return
            
        try:
            generar_sepa_xml(filename, socios_a_domiciliar, self.dades)
            print(f"Remesa SEPA generada correctamente en '{filename}'.")
        except Exception as e:
            print(f"Error al generar la remesa SEPA: {e}")
