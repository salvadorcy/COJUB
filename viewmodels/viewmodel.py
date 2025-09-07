from PyQt6.QtCore import QObject, pyqtSignal
from models.model import DatabaseModel, Socio, Dades
import utils.sepa_lib
from PyQt6.QtWidgets import QMessageBox


class ViewModel(QObject):
    """
    ViewModel que conecta el Modelo (datos) con la Vista (UI).
    Contiene la lógica de la aplicación y notifica a la vista sobre cambios.
    """
    
    socis_changed = pyqtSignal()
    dades_changed = pyqtSignal()
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.all_socis = [] # Almacena todos los socios
        self.filtered_socis = [] # Almacena los socios filtrados
        self.dades = None
        self.selected_socio = None
        
    def load_data(self):
        """Carga todos los datos del modelo."""
        self.all_socis = self.model.get_all_socis()
        self.filtered_socis = self.all_socis # Inicialmente, todos los socios están filtrados
        self.socis_changed.emit()
        self.dades = self.model.get_all_dades()
        self.dades_changed.emit()

    def get_socis(self):
        """Devuelve la lista de socios a mostrar en la tabla."""
        return self.filtered_socis

    def filter_socis(self, search_text):
        """
        Filtra la lista de socios basada en el texto de búsqueda.
        La búsqueda es insensible a mayúsculas y minúsculas y se realiza sobre
        los campos 'FAMID' y 'FAMNom'.
        """
        if not search_text:
            self.filtered_socis = self.all_socis
        else:
            self.filtered_socis = [
                s for s in self.all_socis
                if (s.FAMID and search_text.lower() in s.FAMID.lower()) or
                   (s.FAMNom and search_text.lower() in s.FAMNom.lower())
            ]
        self.socis_changed.emit()

    def set_selected_socio(self, index):
        """Establece el socio seleccionado de la tabla."""
        if 0 <= index < len(self.filtered_socis):
            self.selected_socio = self.filtered_socis[index]
        else:
            self.selected_socio = None

    def get_selected_socio_data(self):
        """Devuelve los datos del socio seleccionado para el formulario."""
        if not self.selected_socio:
            return None
        
        # Devuelve los datos como una tupla para facilitar el llenado del formulario
        return (self.selected_socio.FAMID, self.selected_socio.FAMNom, self.selected_socio.FAMAdressa,
                self.selected_socio.FAMPoblacio, self.selected_socio.FAMCodPos, self.selected_socio.FAMTelefon,
                self.selected_socio.FAMMobil, self.selected_socio.FAMEmail, self.selected_socio.FAMDataAlta,
                self.selected_socio.FAMCCC, self.selected_socio.FAMIBAN, self.selected_socio.FAMBIC,
                self.selected_socio.FAMNSocis, self.selected_socio.bBaixa, self.selected_socio.FAMObservacions,
                self.selected_socio.FAMbSeccio, self.selected_socio.FAMNIF, self.selected_socio.FAMDataNaixement,
                self.selected_socio.FAMQuota, self.selected_socio.FAMIDSec, self.selected_socio.FAMDataBaixa,
                self.selected_socio.FAMTipus, self.selected_socio.FAMSexe, self.selected_socio.FAMSociReferencia,
                self.selected_socio.FAMNewId, self.selected_socio.FAMNewIdRef,
                self.selected_socio.FAMbPagamentDomiciliat, self.selected_socio.FAMbRebutCobrat,
                self.selected_socio.FAMPagamentFinestreta)

    def get_socio_full_name(self, famid):
        """Obtiene el nombre completo de un socio a partir de su ID."""
        for socio in self.all_socis:
            if socio.FAMID == famid:
                return socio.FAMNom
        return "N/A"

    def save_socio(self, new_socio_data):
        """Guarda un nuevo socio o actualiza uno existente."""
        fam_id = new_socio_data[0]
        
        if self.model.get_socio_by_id(fam_id):
            # Actualizar socio
            success = self.model.update_socio(fam_id, new_socio_data[1:])
        else:
            # Crear nuevo socio
            success = self.model.create_socio(new_socio_data)
        
        if success:
            self.load_data()
            return True
        return False

    def delete_selected_socio(self):
        """Elimina el socio actualmente seleccionado."""
        if self.selected_socio:
            success = self.model.delete_socio(self.selected_socio.FAMID)
            if success:
                self.selected_socio = None
                self.load_data()
                return True
        return False

    def get_dades_data(self):
        """Devuelve los datos de configuración."""
        if not self.dades:
            return None
        return (self.dades.TotalDefuncions, self.dades.AcumulatDefuncions, self.dades.PreuDerrama,
                self.dades.ComissioBancaria, self.dades.IdFactura, self.dades.Presentador,
                self.dades.CIFPresentador, self.dades.Ordenant, self.dades.CIFOrdenant,
                self.dades.IBANPresentador, self.dades.BICPresentador, self.dades.PWD,
                self.dades.QuotaSocis, self.dades.SufixeRebuts, self.dades.TexteRebutFinestreta)

    def save_dades(self, dades_data):
        """Guarda los datos de configuración."""
        success = self.model.update_dades(dades_data)
        if success:
            self.load_data()
            return True
        return False

    def generar_remesa_sepa(self, filename):
        """Genera el archivo de remesa SEPA."""
        if not self.dades or not self.all_socis:
            QMessageBox.warning(None, "Error", "No se han cargado los datos para generar la remesa.")
            return False
            
        socios_a_incluir = [s for s in self.all_socis if s.FAMbPagamentDomiciliat and not s.bBaixa]
        
        if not socios_a_incluir:
            QMessageBox.warning(None, "Atención", "No hay socios domiciliados activos para generar la remesa.")
            return False

        try:
            utils.sepa_lib.generar_xml_sepa(self.dades, socios_a_incluir, filename)
            QMessageBox.information(None, "Éxito", "Remesa SEPA generada correctamente en:\n{}".format(filename))
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", "Error al generar la remesa SEPA: {}".format(str(e)))
            return False