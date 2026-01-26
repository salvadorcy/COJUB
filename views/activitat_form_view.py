from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLineEdit, QDateEdit, QDoubleSpinBox, QCheckBox,
                              QPushButton, QTextEdit, QLabel)
from PyQt6.QtCore import QDate
from viewmodels.activitat_viewmodel import ActivitatViewModel
from models.activitat import Activitat
from datetime import date

class ActivitatFormView(QDialog):
    """Formulario para crear/editar actividades"""
    
    def __init__(self, viewmodel: ActivitatViewModel, activitat: Activitat = None, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.activitat = activitat
        self.is_edit_mode = activitat is not None
        
        self.setWindowTitle("Editar Activitat" if self.is_edit_mode else "Nova Activitat")
        self.setMinimumWidth(500)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_data()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Formulario
        form = QFormLayout()
        
        # Descripció
        self.txt_descripcio = QLineEdit()
        self.txt_descripcio.setMaxLength(200)
        form.addRow("Descripció *:", self.txt_descripcio)
        
        # Data Inici
        self.date_inici = QDateEdit()
        self.date_inici.setCalendarPopup(True)
        self.date_inici.setDate(QDate.currentDate())
        self.date_inici.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Data Inici *:", self.date_inici)
        
        # Data Fi
        self.date_fi = QDateEdit()
        self.date_fi.setCalendarPopup(True)
        self.date_fi.setDate(QDate.currentDate())
        self.date_fi.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Data Fi:", self.date_fi)
        
        # Preu Soci
        self.spin_preu_soci = QDoubleSpinBox()
        self.spin_preu_soci.setRange(0, 9999.99)
        self.spin_preu_soci.setDecimals(2)
        self.spin_preu_soci.setSuffix(" €")
        form.addRow("Preu Soci:", self.spin_preu_soci)
        
        # Preu No Soci
        self.spin_preu_no_soci = QDoubleSpinBox()
        self.spin_preu_no_soci.setRange(0, 9999.99)
        self.spin_preu_no_soci.setDecimals(2)
        self.spin_preu_no_soci.setSuffix(" €")
        form.addRow("Preu No Soci:", self.spin_preu_no_soci)
        
        # Completada
        self.chk_completada = QCheckBox("Activitat completada")
        form.addRow("", self.chk_completada)
        
        layout.addLayout(form)
        
        # Nota
        nota = QLabel("* Camps obligatoris")
        nota.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(nota)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.save)
        btn_layout.addWidget(self.btn_guardar)
        
        self.btn_cancelar = QPushButton("Cancel·lar")
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Carga los datos de la actividad en el formulario"""
        if not self.activitat:
            return
        
        self.txt_descripcio.setText(self.activitat.descripcio)
        
        if self.activitat.data_inici:
            qdate = QDate(self.activitat.data_inici.year, 
                         self.activitat.data_inici.month,
                         self.activitat.data_inici.day)
            self.date_inici.setDate(qdate)
        
        if self.activitat.data_fi:
            qdate = QDate(self.activitat.data_fi.year,
                         self.activitat.data_fi.month,
                         self.activitat.data_fi.day)
            self.date_fi.setDate(qdate)
        
        self.spin_preu_soci.setValue(self.activitat.preu_soci)
        self.spin_preu_no_soci.setValue(self.activitat.preu_no_soci)
        self.chk_completada.setChecked(self.activitat.completada)
    
    def save(self):
        """Guarda la actividad"""
        # Validación
        if not self.txt_descripcio.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "La descripció és obligatòria")
            return
        
        # Crear/actualizar activitat
        if self.is_edit_mode:
            self.activitat.descripcio = self.txt_descripcio.text().strip()
            self.activitat.data_inici = self.date_inici.date().toPyDate()
            self.activitat.data_fi = self.date_fi.date().toPyDate()
            self.activitat.preu_soci = self.spin_preu_soci.value()
            self.activitat.preu_no_soci = self.spin_preu_no_soci.value()
            self.activitat.completada = self.chk_completada.isChecked()
            
            if self.viewmodel.update_activitat(self.activitat):
                self.accept()
        else:
            activitat = Activitat(
                descripcio=self.txt_descripcio.text().strip(),
                data_inici=self.date_inici.date().toPyDate(),
                data_fi=self.date_fi.date().toPyDate(),
                preu_soci=self.spin_preu_soci.value(),
                preu_no_soci=self.spin_preu_no_soci.value(),
                completada=self.chk_completada.isChecked()
            )
            
            if self.viewmodel.create_activitat(activitat):
                self.accept()