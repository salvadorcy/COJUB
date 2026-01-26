from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
                              QLabel, QCompleter, QMessageBox)
from PyQt6.QtCore import Qt
from viewmodels.activitat_viewmodel import ActivitatViewModel
from models.activitat import Activitat
from models.model import DatabaseModel

class AddSociActivitatView(QDialog):
    """Diálogo para añadir un socio a una actividad"""
    
    def __init__(self, viewmodel: ActivitatViewModel, activitat: Activitat, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.activitat = activitat
        self.db_model = db_model
        
        self.setWindowTitle("Afegir Soci a l'Activitat")
        self.setMinimumWidth(400)
        
        self.init_ui()
        self.load_socis()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        # Buscador de socios
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cerca per nom, cognoms o NIF...")
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.txt_search.setCompleter(self.completer)
        self.txt_search.textChanged.connect(self.on_search_changed)
        form.addRow("Buscar Soci *:", self.txt_search)
        
        # Tipo (Soci / No Soci)
        self.cmb_tipus = QComboBox()
        self.cmb_tipus.addItems(["Soci", "No Soci"])
        self.cmb_tipus.currentIndexChanged.connect(self.on_tipus_changed)
        form.addRow("Tipus *:", self.cmb_tipus)
        
        # Import
        self.spin_import = QDoubleSpinBox()
        self.spin_import.setRange(0, 9999.99)
        self.spin_import.setDecimals(2)
        self.spin_import.setSuffix(" €")
        self.spin_import.setValue(self.activitat.preu_soci)
        form.addRow("Import *:", self.spin_import)
        
        layout.addLayout(form)
        
        # Nota
        nota = QLabel("* Camps obligatoris")
        nota.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(nota)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_afegir = QPushButton("Afegir")
        self.btn_afegir.clicked.connect(self.add_soci)
        self.btn_afegir.setEnabled(False)
        btn_layout.addWidget(self.btn_afegir)
        
        self.btn_cancelar = QPushButton("Cancel·lar")
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_socis(self):
        """Carga la lista de socios para el autocompletado"""
        try:
            # CAMBIADO: Usar FAMID en lugar de codi
            query = """
                SELECT FAMID, Nom, Cognom1, Cognom2, NIF
                FROM scazorla_sa.G_Socis
                WHERE Actiu = 1
                ORDER BY Cognom1, Cognom2, Nom
            """
            rows = self.db_model.execute_query(query)
            
            self.socis_data = {}
            search_items = []
            
            for row in rows:
                famid = row[0]  # FAMID en lugar de codi
                nom = row[1]
                cognom1 = row[2]
                cognom2 = row[3] if row[3] else ""
                nif = row[4]
                
                cognoms = f"{cognom1} {cognom2}".strip()
                display_text = f"{cognoms}, {nom} - {nif}"
                
                self.socis_data[display_text] = famid  # Guardar FAMID
                search_items.append(display_text)
            
            self.completer.setModel(self.completer.model().__class__(search_items))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error carregant socis: {str(e)}")
    
    def on_search_changed(self, text: str):
        """Maneja el cambio en el buscador"""
        self.btn_afegir.setEnabled(text in self.socis_data)
    
    def on_tipus_changed(self, index: int):
        """Cambia el precio según el tipo de socio"""
        if index == 0:  # Soci
            self.spin_import.setValue(self.activitat.preu_soci)
        else:  # No Soci
            self.spin_import.setValue(self.activitat.preu_no_soci)
    
    def add_soci(self):
        """Añade el socio a la actividad"""
        search_text = self.txt_search.text()
        
        if search_text not in self.socis_data:
            QMessageBox.warning(self, "Error", "Selecciona un soci vàlid")
            return
        
        soci_famid = self.socis_data[search_text]  # Ahora es FAMID (str)
        es_soci = self.cmb_tipus.currentIndex() == 0
        preu = self.spin_import.value()
        
        if self.viewmodel.add_soci_to_activitat(self.activitat.id, soci_famid, es_soci, preu):
            self.accept()