from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QGroupBox, QFormLayout,
                              QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from viewmodels.activitat_viewmodel import ActivitatViewModel
from models.activitat import Activitat
from views.add_soci_activitat_view import AddSociActivitatView

class ActivitatDetailView(QDialog):
    """Vista de detalle de una actividad con sus inscritos"""
    
    def __init__(self, viewmodel: ActivitatViewModel, activitat: Activitat, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.activitat = activitat
        
        self.setWindowTitle(f"Activitat: {activitat.descripcio}")
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.connect_signals()
        self.viewmodel.load_inscripcions(activitat.id)
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Información de la actividad
        info_group = QGroupBox("Informació de l'Activitat")
        info_layout = QFormLayout()
        
        info_layout.addRow("Descripció:", QLabel(self.activitat.descripcio))
        
        data_inici = self.activitat.data_inici.strftime("%d/%m/%Y") if self.activitat.data_inici else ""
        info_layout.addRow("Data Inici:", QLabel(data_inici))
        
        data_fi = self.activitat.data_fi.strftime("%d/%m/%Y") if self.activitat.data_fi else ""
        info_layout.addRow("Data Fi:", QLabel(data_fi))
        
        info_layout.addRow("Preu Soci:", QLabel(f"{self.activitat.preu_soci:.2f} €"))
        info_layout.addRow("Preu No Soci:", QLabel(f"{self.activitat.preu_no_soci:.2f} €"))
        
        estat = "Completada" if self.activitat.completada else "Activa"
        info_layout.addRow("Estat:", QLabel(estat))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Estadísticas
        self.stats_group = QGroupBox("Estadístiques")
        self.stats_layout = QHBoxLayout()
        
        self.lbl_total_inscrits = QLabel("Inscrits: 0")
        self.lbl_total_pagats = QLabel("Pagats: 0")
        self.lbl_total_recaptat = QLabel("Recaptat: 0.00 €")
        
        self.stats_layout.addWidget(self.lbl_total_inscrits)
        self.stats_layout.addWidget(self.lbl_total_pagats)
        self.stats_layout.addWidget(self.lbl_total_recaptat)
        self.stats_layout.addStretch()
        
        self.stats_group.setLayout(self.stats_layout)
        layout.addWidget(self.stats_group)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.btn_add_soci = QPushButton("Afegir Soci")
        self.btn_add_soci.clicked.connect(self.add_soci)
        btn_layout.addWidget(self.btn_add_soci)
        
        self.btn_remove_soci = QPushButton("Donar de Baixa")
        self.btn_remove_soci.clicked.connect(self.remove_soci)
        self.btn_remove_soci.setEnabled(False)
        btn_layout.addWidget(self.btn_remove_soci)
        
        self.btn_generar_llistat = QPushButton("Generar Llistat PDF")
        self.btn_generar_llistat.clicked.connect(self.generar_llistat)
        btn_layout.addWidget(self.btn_generar_llistat)
        
        btn_layout.addStretch()
        
        self.btn_tancar = QPushButton("Tancar")
        self.btn_tancar.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_tancar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de inscritos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "NIF", "Nom", "Cognoms", "Tipus", "Import", "Pagat"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        """Conecta las señales del ViewModel"""
        self.viewmodel.inscripcions_updated.connect(self.update_table)
        self.viewmodel.inscripcions_updated.connect(self.update_stats)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.success_message.connect(self.show_success)
    
    def update_table(self):
        """Actualiza la tabla con los inscritos"""
        self.table.setRowCount(0)
        inscripcions = self.viewmodel.get_inscripcions()
        
        for row, inscripcio in enumerate(inscripcions):
            self.table.insertRow(row)
            
            # NIF
            self.table.setItem(row, 0, QTableWidgetItem(inscripcio.nif_soci))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(inscripcio.nom_soci))
            
            # Cognoms
            self.table.setItem(row, 2, QTableWidgetItem(inscripcio.cognoms_soci))
            
            # Tipus
            tipus = "Soci" if inscripcio.es_soci else "No Soci"
            self.table.setItem(row, 3, QTableWidgetItem(tipus))
            
            # Import
            import_text = f"{inscripcio.import_pagat:.2f} €" if inscripcio.import_pagat else ""
            self.table.setItem(row, 4, QTableWidgetItem(import_text))
            
            # Pagat (checkbox)
            chk_pagat = QCheckBox()
            chk_pagat.setChecked(inscripcio.pagat)
            chk_pagat.stateChanged.connect(
                lambda state, insc_id=inscripcio.id: self.on_pagat_changed(insc_id, state)
            )
            
            # Centrar checkbox
            widget = QWidget()
            layout_chk = QHBoxLayout(widget)
            layout_chk.addWidget(chk_pagat)
            layout_chk.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_chk.setContentsMargins(0, 0, 0, 0)
            
            self.table.setCellWidget(row, 5, widget)
            
            # Color de fondo según si está pagado
            if inscripcio.pagat:
                for col in range(6):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(144, 238, 144))  # Verde claro
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        stats = self.viewmodel.get_estadistiques_activitat(self.activitat.id)
        
        self.lbl_total_inscrits.setText(f"Inscrits: {stats.get('total_inscrits', 0)}")
        self.lbl_total_pagats.setText(f"Pagats: {stats.get('total_pagats', 0)}")
        self.lbl_total_recaptat.setText(f"Recaptat: {stats.get('total_recaptat', 0):.2f} €")
    
    def on_selection_changed(self):
        """Maneja el cambio de selección"""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_remove_soci.setEnabled(has_selection)
    
    def on_pagat_changed(self, inscripcio_id: int, state: int):
        """Maneja el cambio del estado de pago"""
        pagat = state == Qt.CheckState.Checked.value
        self.viewmodel.marcar_pagament(inscripcio_id, pagat, self.activitat.id)
    
    def add_soci(self):
        """Añade un socio a la actividad"""
        dialog = AddSociActivitatView(self.viewmodel, self.activitat, parent=self)
        dialog.exec()
    
    def remove_soci(self):
        """Da de baja un socio de la actividad"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        inscripcions = self.viewmodel.get_inscripcions()
        
        if row >= len(inscripcions):
            return
        
        inscripcio = inscripcions[row]
        
        reply = QMessageBox.question(
            self,
            "Confirmar baixa",
            f"Estàs segur que vols donar de baixa a {inscripcio.nom_soci} {inscripcio.cognoms_soci}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.viewmodel.remove_soci_from_activitat(inscripcio.id, self.activitat.id)
    
    def generar_llistat(self):
        """Genera un PDF con el listado de inscritos"""
        from reports.activitat_report import generate_activitat_report
        
        try:
            pdf_path = generate_activitat_report(self.activitat, self.viewmodel.get_inscripcions())
            QMessageBox.information(
                self,
                "PDF Generat",
                f"El llistat s'ha generat correctament:\n{pdf_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generant el PDF: {str(e)}")
    
    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        QMessageBox.information(self, "Èxit", message)