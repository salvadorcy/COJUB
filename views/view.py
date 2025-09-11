from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QCheckBox, QGroupBox
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime

class SocioDialog(QDialog):
    """Diálogo para agregar o editar un socio."""
    def __init__(self, parent=None, socio=None, todos_socis=None):
        super().__init__(parent)
        self.setWindowTitle("Edita Soci" if socio else "Afegeix Soci")
        self.setGeometry(100, 100, 650, 600)
        self.socio_data = socio
        self.todos_socis = todos_socis

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.fields = {}
        fields_config = [
            ("FAMID", QLineEdit(), "ID"),
            ("FAMNom", QLineEdit(), "Nom"),
            ("FAMAdressa", QLineEdit(), "Adreça"),
            ("FAMPoblacio", QLineEdit(), "Població"),
            ("FAMCodPos", QLineEdit(), "Codi Postal"),
            ("FAMTelefon", QLineEdit(), "Telèfon"),
            ("FAMMobil", QLineEdit(), "Mòbil"),
            ("FAMEmail", QLineEdit(), "Correu electrònic"),
            ("FAMDataAlta", QLineEdit(), "Data Alta (YYYY-MM-DD)"),
            ("FAMCCC", QLineEdit(), "CCC"),
            ("FAMIBAN", QLineEdit(), "IBAN"),
            ("FAMBIC", QLineEdit(), "BIC"),
            ("FAMNSocis", QLineEdit(), "Núm. Socis"),
            ("bBaixa", QCheckBox(), "Baixa"),
            ("FAMObservacions", QLineEdit(), "Observacions"),
            ("FAMbSeccio", QCheckBox(), "Secció"),
            ("FAMNIF", QLineEdit(), "NIF"),
            ("FAMDataNaixement", QLineEdit(), "Data Naixement (YYYY-MM-DD)"),
            ("FAMQuota", QLineEdit(), "Quota"),
            ("FAMIDSec", QLineEdit(), "ID Secció"),
            ("FAMDataBaixa", QLineEdit(), "Data Baixa (YYYY-MM-DD)"),
            ("FAMTipus", QLineEdit(), "Tipus"),
            ("FAMSexe", QLineEdit(), "Sexe (H/M)"),
            ("FAMSociReferencia", QLineEdit(), "Soci Parella"),
            ("FAMNewId", QLineEdit(), "Nou ID"),
            ("FAMNewIdRef", QLineEdit(), "Nova Ref ID"),
            ("FAMbPagamentDomiciliat", QCheckBox(), "Pagament Domiciliat"),
            ("FAMbRebutCobrat", QCheckBox(), "Rebut Cobrat"),
            ("FAMPagamentFinestreta", QCheckBox(), "Pagament Finestreta")
        ]

        for attr, widget, label_text in fields_config:
            if isinstance(widget, QCheckBox):
                self.fields[attr] = widget
                widget.setText(label_text)
                self.form_layout.addRow(widget)
            else:
                self.fields[attr] = widget
                self.form_layout.addRow(label_text, widget)
        
        # Ajustar el ancho de los campos de texto largos
        self.fields["FAMNom"].setMinimumWidth(300)
        self.fields["FAMAdressa"].setMinimumWidth(300)

        self.layout.addLayout(self.form_layout)

        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Desa")
        self.cancel_button = QPushButton("Cancel·la")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.fill_form()
    
    def fill_form(self):
        """Rellena el formulario con los datos del socio si existe."""
        if self.socio_data:
            # Deshabilitar FAMID en modo edición para evitar cambios
            self.fields["FAMID"].setEnabled(False)
            
            # Lista ordenada de los nombres de los atributos para garantizar el orden
            ordered_keys = [
                "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
                "FAMTelefon", "FAMMobil", "FAMEmail", "FAMDataAlta", "FAMCCC",
                "FAMIBAN", "FAMBIC", "FAMNSocis", "bBaixa", "FAMObservacions",
                "FAMbSeccio", "FAMNIF", "FAMDataNaixement", "FAMQuota", "FAMIDSec",
                "FAMDataBaixa", "FAMTipus", "FAMSexe", "FAMSociReferencia",
                "FAMNewId", "FAMNewIdRef", "FAMbPagamentDomiciliat",
                "FAMbRebutCobrat", "FAMPagamentFinestreta"
            ]

            # Rellenar los campos con los datos del socio, usando los índices
            for i, key in enumerate(ordered_keys):
                if key in self.fields:
                    widget = self.fields[key]
                    value = self.socio_data[i]
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value) if value is not None else "")
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))

    def get_data(self):
        """Devuelve los datos del formulario como una tupla."""
        data = []
        for attr in self.fields:
            widget = self.fields[attr]
            if isinstance(widget, QLineEdit):
                value = widget.text()
                if attr in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"] and value:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        value = None # O manejar el error
                elif attr in ["FAMNSocis"]:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        value = 0
                elif attr in ["FAMQuota"]:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = 0.0
                data.append(value)
            elif isinstance(widget, QCheckBox):
                data.append(widget.isChecked())
        return tuple(data)

class DadesDialog(QDialog):
    """Diálogo para editar los datos de configuración."""
    def __init__(self, parent=None, dades=None):
        super().__init__(parent)
        self.setWindowTitle("Configuració de l'Aplicació")
        self.setGeometry(100, 100, 500, 500)
        self.dades = dades

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.fields = {}
        fields_config = [
            ("TotalDefuncions", QLineEdit(), "Total Defuncions"),
            ("AcumulatDefuncions", QLineEdit(), "Acumulat Defuncions"),
            ("PreuDerrama", QLineEdit(), "Preu Derrama"),
            ("ComissioBancaria", QLineEdit(), "Comissió Bancària"),
            ("IdFactura", QLineEdit(), "ID Factura"),
            ("Presentador", QLineEdit(), "Presentador"),
            ("CIFPresentador", QLineEdit(), "CIF Presentador"),
            ("Ordenant", QLineEdit(), "Ordenant"),
            ("CIFOrdenant", QLineEdit(), "CIF Ordenant"),
            ("IBANPresentador", QLineEdit(), "IBAN Presentador"),
            ("BICPresentador", QLineEdit(), "BIC Presentador"),
            ("PWD", QLineEdit(), "Contrasenya"),
            ("QuotaSocis", QLineEdit(), "Quota Socis"),
            ("SufixeRebuts", QLineEdit(), "Sufix Rebuts"),
            ("TexteRebutFinestreta", QLineEdit(), "Text Rebut Finestreta")
        ]

        for attr, widget, label_text in fields_config:
            self.fields[attr] = widget
            self.form_layout.addRow(label_text, widget)
        
        self.layout.addLayout(self.form_layout)

        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Desa")
        self.cancel_button = QPushButton("Cancel·la")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.fill_form()
    
    def fill_form(self):
        """Rellena el formulario con los datos de configuración."""
        if self.dades:
            data = self.dades.get_dades_data()
            for i, attr in enumerate(self.fields):
                value = data[i]
                if value is not None:
                    self.fields[attr].setText(str(value))

    def get_data(self):
        """Devuelve los datos del formulario como una tupla."""
        data = []
        for attr in self.fields:
            widget = self.fields[attr]
            value = widget.text()
            if attr in ["TotalDefuncions", "AcumulatDefuncions"]:
                try:
                    data.append(int(value))
                except (ValueError, TypeError):
                    data.append(0)
            elif attr in ["PreuDerrama", "ComissioBancaria", "QuotaSocis"]:
                try:
                    data.append(float(value))
                except (ValueError, TypeError):
                    data.append(0.0)
            else:
                data.append(value)
        return tuple(data)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    def __init__(self, view_model):
        super().__init__()
        self.setWindowTitle("Gestió de Socis i Remeses SEPA")
        self.setGeometry(100, 100, 1280, 800)
        self.view_model = view_model
        
        # Conectar señales del ViewModel a métodos de la Vista
        self.view_model.socis_changed.connect(self.update_socis_table)
        self.view_model.dades_changed.connect(self.update_ui_with_dades)

        self.init_ui()
        self.view_model.load_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Botones de acción
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Afegeix Soci")
        self.edit_button = QPushButton("Edita Soci")
        self.delete_button = QPushButton("Elimina Soci")
        self.config_button = QPushButton("Configuració")
        self.sepa_button = QPushButton("Genera Remesa SEPA")
        
        self.add_button.clicked.connect(self.add_socio)
        self.edit_button.clicked.connect(self.edit_socio)
        self.delete_button.clicked.connect(self.delete_socio)
        self.config_button.clicked.connect(self.edit_dades)
        self.sepa_button.clicked.connect(self.generar_sepa)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.config_button)
        button_layout.addWidget(self.sepa_button)
        
        main_layout.addLayout(button_layout)
        
        # Grupo para la información de la remesa
        remesa_group = QGroupBox("Informació de Remesa")
        remesa_layout = QFormLayout(remesa_group)
        self.label_quota = QLabel("Quota Socis: N/A")
        self.label_presentador = QLabel("Presentador: N/A")
        remesa_layout.addRow(self.label_quota)
        remesa_layout.addRow(self.label_presentador)
        main_layout.addWidget(remesa_group)

        # Barra de búsqueda y filtro
        search_layout = QHBoxLayout()
        search_label = QLabel("Cercar Soci:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cercar per ID o Nom...")
        self.search_input.textChanged.connect(self.view_model.filter_socis)
        
        self.finestreta_checkbox = QCheckBox("Pagament per Finestreta")
        self.finestreta_checkbox.stateChanged.connect(self.view_model.toggle_finestreta_filter)
        
        self.baixa_checkbox = QCheckBox("Mostrar Baixes")
        self.baixa_checkbox.stateChanged.connect(self.view_model.toggle_baixa_filter)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.finestreta_checkbox)
        search_layout.addWidget(self.baixa_checkbox)
        
        main_layout.addLayout(search_layout)

        # Tabla de socios
        self.socis_table = QTableWidget()
        self.socis_table.setColumnCount(9) # Solo mostramos algunas columnas relevantes
        self.socis_table.setColumnWidth(0,50)
        self.socis_table.setColumnWidth(1,300)
        self.socis_table.setColumnWidth(2,300)
        self.socis_table.setColumnWidth(3,50)
        self.socis_table.setColumnWidth(4,150)
        self.socis_table.setColumnWidth(5,80)
        self.socis_table.setColumnWidth(6,80)
        self.socis_table.setColumnWidth(7,180)
        self.socis_table.setColumnWidth(8,300)
        
        self.socis_table.setHorizontalHeaderLabels(["ID", "Nom", "Adreça", "Cod.Pos.", "Poblacio","Telèfon","Mòbil","Email","Soci Referencia/Parella"])
        self.socis_table.horizontalHeader().setStretchLastSection(True)
        self.socis_table.setAlternatingRowColors(True)
        self.socis_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.socis_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.socis_table.itemSelectionChanged.connect(self.on_socio_selected)
        self.socis_table.itemDoubleClicked.connect(self.on_socio_double_clicked)
        main_layout.addWidget(self.socis_table)
        
    def update_socis_table(self):
        """Actualiza la tabla de socios con los datos del ViewModel."""
        socis_to_show = self.view_model.get_socis()
        self.socis_table.setRowCount(len(socis_to_show))
        for row, socio in enumerate(socis_to_show):
            # Colorear la fila si el socio está dado de baja
            if socio.bBaixa:
                for col in range(self.socis_table.columnCount()):
                    item = QTableWidgetItem()
                    item.setBackground(QColor(255, 0, 0)) # Rojo
                    item.setForeground(QColor(255, 255, 255)) # Blanco
                    self.socis_table.setItem(row, col, item)
            self.socis_table.setItem(row, 0, QTableWidgetItem(socio.FAMID))
            self.socis_table.setItem(row, 1, QTableWidgetItem(socio.FAMNom))
            self.socis_table.setItem(row, 2, QTableWidgetItem(socio.FAMAdressa))
            self.socis_table.setItem(row, 3, QTableWidgetItem(socio.FAMCodPos))
            self.socis_table.setItem(row, 4, QTableWidgetItem(socio.FAMPoblacio))
            self.socis_table.setItem(row, 5, QTableWidgetItem(socio.FAMTelefon))
            self.socis_table.setItem(row, 6, QTableWidgetItem(socio.FAMMobil))
            self.socis_table.setItem(row, 7, QTableWidgetItem(socio.FAMEmail))            
            
            # Manejar el campo de socio pareja
            socio_pareja_nom = self.view_model.get_socio_full_name(socio.FAMSociReferencia)
            self.socis_table.setItem(row, 8, QTableWidgetItem(socio_pareja_nom))

    def on_socio_selected(self):
        """Maneja la selección de un socio en la tabla."""
        selected_rows = self.socis_table.selectedIndexes()
        if selected_rows:
            row_index = selected_rows[0].row()
            self.view_model.set_selected_socio(row_index)
        else:
            self.view_model.set_selected_socio(None)
    
    def on_socio_double_clicked(self, item):
        """Maneja el evento de doble clic para editar un socio."""
        self.edit_socio()

    def add_socio(self):
        """Abre el diálogo para agregar un nuevo socio."""
        dialog = SocioDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            if self.view_model.save_socio(new_data):
                QMessageBox.information(self, "Èxit", "Soci afegit correctament.")
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut afegir el soci.")
    
    def edit_socio(self):
        """Abre el diálogo para editar el socio seleccionado."""
        socio_data = self.view_model.get_selected_socio_data()
        if not socio_data:
            QMessageBox.warning(self, "Advertència", "Si us plau, selecciona un soci per editar.")
            return

        dialog = SocioDialog(self, socio_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            if self.view_model.save_socio(updated_data):
                QMessageBox.information(self, "Èxit", "Soci actualitzat correctament.")
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut actualitzar el soci.")
                
    def delete_socio(self):
        """Elimina el socio seleccionado."""
        if not self.view_model.selected_socio:
            QMessageBox.warning(self, "Advertència", "Si us plau, selecciona un soci per eliminar.")
            return

        reply = QMessageBox.question(self, "Confirmar eliminació",
                                     "Estàs segur que vols eliminar el soci seleccionat?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.view_model.delete_selected_socio():
                QMessageBox.information(self, "Èxit", "Soci eliminat correctament.")
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut eliminar el soci.")
                
    def edit_dades(self):
        """Abre el diálogo para editar los datos de configuración."""
        dades_data = self.view_model.get_dades_data()
        if not dades_data:
            QMessageBox.warning(self, "Error", "No hi ha dades de configuració per editar.")
            return

        dialog = DadesDialog(self, self.view_model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            if self.view_model.save_dades(updated_data):
                QMessageBox.information(self, "Èxit", "Dades de configuració actualitzades.")
            else:
                QMessageBox.critical(self, "Error", "No s'han pogut actualitzar les dades de configuració.")

    def update_ui_with_dades(self):
        """Actualiza los elementos de la UI con los datos de configuración."""
        if self.view_model.dades:
            self.label_quota.setText("Quota Socis: " + str(self.view_model.dades.QuotaSocis) + " €")
            self.label_presentador.setText("Presentador: " + self.view_model.dades.Presentador)
            
    def generar_sepa(self):
        """Llama a la lógica del viewmodel para generar la remesa SEPA."""
        # Se podría agregar un diálogo para seleccionar la ruta del archivo
        filename = "remesa_sepa.xml"
        self.view_model.generar_remesa_sepa(filename)
