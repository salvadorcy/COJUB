from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView, 
                              QMessageBox, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from viewmodels.activitat_viewmodel import ActivitatViewModel
from views.activitat_form_view import ActivitatFormView
from views.activitat_detail_view import ActivitatDetailView

class ActivitatsView(QDialog):
    """Vista principal para listar actividades"""
    
    def __init__(self, viewmodel: ActivitatViewModel, parent=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()
        self.connect_signals()
        self.viewmodel.load_activitats_actives()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gestio d'Activitats")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.btn_nova = QPushButton("Nova Activitat")
        self.btn_nova.clicked.connect(self.show_nova_activitat)
        btn_layout.addWidget(self.btn_nova)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_activitat)
        self.btn_editar.setEnabled(False)
        btn_layout.addWidget(self.btn_editar)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_activitat)
        self.btn_eliminar.setEnabled(False)
        btn_layout.addWidget(self.btn_eliminar)
        
        self.btn_refresh = QPushButton("Actualitzar")
        self.btn_refresh.clicked.connect(self.viewmodel.load_activitats_actives)
        btn_layout.addWidget(self.btn_refresh)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Tabla de actividades
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Descripcio", "Data Inici", "Data Fi", 
            "Preu Soci", "Preu No Soci", "Estat"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.obrir_detall_activitat)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        """Conecta las senyales del ViewModel"""
        self.viewmodel.activitats_updated.connect(self.update_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.success_message.connect(self.show_success)
    
    def update_table(self):
        """Actualiza la tabla con las actividades"""
        self.table.setRowCount(0)
        activitats = self.viewmodel.get_activitats()
        
        for row, activitat in enumerate(activitats):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(activitat.id)))
            
            # Descripció
            self.table.setItem(row, 1, QTableWidgetItem(activitat.descripcio))
            
            # Data Inici
            data_inici = activitat.data_inici.strftime("%d/%m/%Y") if activitat.data_inici else ""
            self.table.setItem(row, 2, QTableWidgetItem(data_inici))
            
            # Data Fi
            data_fi = activitat.data_fi.strftime("%d/%m/%Y") if activitat.data_fi else ""
            self.table.setItem(row, 3, QTableWidgetItem(data_fi))
            
            # Preu Soci
            self.table.setItem(row, 4, QTableWidgetItem(f"{activitat.preu_soci:.2f} €"))
            
            # Preu No Soci
            self.table.setItem(row, 5, QTableWidgetItem(f"{activitat.preu_no_soci:.2f} €"))
            
            # Estat
            estat = "Completada" if activitat.completada else "Activa"
            item_estat = QTableWidgetItem(estat)
            if activitat.completada:
                item_estat.setBackground(QColor(200, 200, 200))
            else:
                item_estat.setBackground(QColor(144, 238, 144))
            self.table.setItem(row, 6, item_estat)
    
    def on_selection_changed(self):
        """Maneja el cambio de selección"""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_editar.setEnabled(has_selection)
        self.btn_eliminar.setEnabled(has_selection)
    
    def get_selected_activitat(self):
        """Obtiene la actividad seleccionada"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        activitat_id = int(self.table.item(row, 0).text())
        
        activitats = self.viewmodel.get_activitats()
        for activitat in activitats:
            if activitat.id == activitat_id:
                return activitat
        return None
    
    def show_nova_activitat(self):
        """Muestra el formulario para crear una nueva actividad"""
        dialog = ActivitatFormView(self.viewmodel, parent=self)
        dialog.exec()
    
    def editar_activitat(self):
        """Muestra el formulario para editar la actividad seleccionada"""
        activitat = self.get_selected_activitat()
        if activitat:
            dialog = ActivitatFormView(self.viewmodel, activitat=activitat, parent=self)
            dialog.exec()
    
    def eliminar_activitat(self):
        """Elimina la actividad seleccionada"""
        activitat = self.get_selected_activitat()
        if not activitat:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminació",
            f"Estàs segur que vols eliminar l'activitat '{activitat.descripcio}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.viewmodel.delete_activitat(activitat.id)
    
    def obrir_detall_activitat(self):
        """Abre el detalle de la actividad (doble clic)"""
        activitat = self.get_selected_activitat()
        if activitat:
            dialog = ActivitatDetailView(self.viewmodel, activitat, parent=self)
            dialog.exec()
    
    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        QMessageBox.information(self, "Èxit", message)