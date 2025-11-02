from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QCheckBox, QGroupBox,QFileDialog
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QFont, QDesktopServices
from PyQt6.QtCore import QUrl
from datetime import datetime
from .style_config import STYLE_CONFIG
import os
import platform


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
        """Devuelve los datos del formulario como una tupla, asegurando el orden correcto."""
        data = []
        ordered_keys = [
            "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
            "FAMTelefon", "FAMMobil", "FAMEmail", "FAMDataAlta", "FAMCCC",
            "FAMIBAN", "FAMBIC", "FAMNSocis", "bBaixa", "FAMObservacions",
            "FAMbSeccio", "FAMNIF", "FAMDataNaixement", "FAMQuota", "FAMIDSec",
            "FAMDataBaixa", "FAMTipus", "FAMSexe", "FAMSociReferencia",
            "FAMNewId", "FAMNewIdRef", "FAMbPagamentDomiciliat",
            "FAMbRebutCobrat", "FAMPagamentFinestreta"
        ]
        
        for key in ordered_keys:
            if key in self.fields:
                widget = self.fields[key]
                value = None
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                    if key in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"] and value:
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d')
                        except ValueError:
                            value = None
                    elif key in ["FAMNSocis"]:
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            value = 0
                    elif key in ["FAMQuota"]:
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                elif isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                data.append(value)
        return tuple(data)


class DadesDialog(QDialog):
    """Diálogo para editar los datos de configuración."""
    def __init__(self, parent=None, view_model=None):
        super().__init__(parent)
        self.setWindowTitle("Configuració de l'Aplicació")
        self.setGeometry(100, 100, 500, 500)
        self.view_model = view_model

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
        if self.view_model:
            data = self.view_model.get_dades_data()
            if data:
                ordered_keys = list(self.fields.keys())
                for i, attr in enumerate(ordered_keys):
                    if i < len(data):
                        value = data[i]
                        if value is not None:
                            self.fields[attr].setText(str(value))

    def get_data(self):
        """Devuelve los datos del formulario como una tupla."""
        data = []
        ordered_keys = [
            "TotalDefuncions", "AcumulatDefuncions", "PreuDerrama", "ComissioBancaria",
            "IdFactura", "Presentador", "CIFPresentador", "Ordenant", "CIFOrdenant",
            "IBANPresentador", "BICPresentador", "PWD", "QuotaSocis",
            "SufixeRebuts", "TexteRebutFinestreta"
        ]
        
        for attr in ordered_keys:
            widget = self.fields[attr]
            value = widget.text()
            if attr in ["TotalDefuncions", "AcumulatDefuncions"]:
                try:
                    data.append(int(value) if value else 0)
                except (ValueError, TypeError):
                    data.append(0)
            elif attr in ["PreuDerrama", "ComissioBancaria", "QuotaSocis"]:
                try:
                    data.append(float(value) if value else 0.0)
                except (ValueError, TypeError):
                    data.append(0.0)
            else:
                data.append(value if value else "")
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
        
        # Botones para los listados a imprimir
        self.print_general_button = QPushButton("Imprimeix Llistat General")
        self.print_banking_button = QPushButton("Imprimeix Dades Bancàries")
        
        self.print_general_button.clicked.connect(self.print_general_report)
        self.print_banking_button.clicked.connect(self.print_banking_report)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.config_button)
        button_layout.addWidget(self.sepa_button)
        button_layout.addWidget(self.print_general_button)
        button_layout.addWidget(self.print_banking_button)
        
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

        # Etiqueta para el contador de registros
        self.record_count_label = QLabel("Total de registres: 0")
        self.record_count_label.setFont(QFont(STYLE_CONFIG["font_family"], STYLE_CONFIG["font_size_bold"], QFont.Weight.Bold))
        main_layout.addWidget(self.record_count_label)
        
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
        
        # Esta línea actualiza el contador de registros
        self.record_count_label.setText(f"Total de registres: {len(socis_to_show)}")

        for row, socio in enumerate(socis_to_show):
            # Obtener el nombre del socio pareja
            socio_pareja_nom = self.view_model.get_socio_full_name(socio.FAMSociReferencia)

            # Crear y establecer los QTableWidgetItem para cada columna
            id_item = QTableWidgetItem(socio.FAMID)
            nom_item = QTableWidgetItem(socio.FAMNom)
            adressa_item = QTableWidgetItem(socio.FAMAdressa)
            cod_pos_item = QTableWidgetItem(socio.FAMCodPos)
            poblacio_item = QTableWidgetItem(socio.FAMPoblacio)
            telefon_item = QTableWidgetItem(socio.FAMTelefon)
            mobil_item = QTableWidgetItem(socio.FAMMobil)
            email_item = QTableWidgetItem(socio.FAMEmail)
            socio_parella_item = QTableWidgetItem(socio_pareja_nom)

            # Si el socio está dado de baja, aplicar el estilo de color
            if socio.bBaixa:
                for item in [id_item, nom_item, adressa_item, cod_pos_item, poblacio_item,
                             telefon_item, mobil_item, email_item, socio_parella_item]:
                    item.setBackground(STYLE_CONFIG["color_baixa_bg"])
                    item.setForeground(STYLE_CONFIG["color_baixa_text"])

            # Establecer los ítems en la tabla
            self.socis_table.setItem(row, 0, id_item)
            self.socis_table.setItem(row, 1, nom_item)
            self.socis_table.setItem(row, 2, adressa_item)
            self.socis_table.setItem(row, 3, cod_pos_item)
            self.socis_table.setItem(row, 4, poblacio_item)
            self.socis_table.setItem(row, 5, telefon_item)
            self.socis_table.setItem(row, 6, mobil_item)
            self.socis_table.setItem(row, 7, email_item)
            self.socis_table.setItem(row, 8, socio_parella_item)

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
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar remesa SEPA", "remesa_sepa.xml", "XML Files (*.xml)")
        if filename:
            if self.view_model.generar_remesa_sepa(filename):
                QMessageBox.information(self, "Remesa SEPA Generada", f"La remesa SEPA s'ha generat correctament a:\n{filename}")
                self._open_file(filename)
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut generar la remesa SEPA.")
    
    def print_general_report(self):
        """Genera e imprime el listado general de socios."""
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar llistat general", "llistat_general.pdf", "PDF Files (*.pdf)")
        if filepath:
            if self.view_model.generate_general_report(filepath):
                QMessageBox.information(self, "Llistat Generat", f"El llistat general s'ha generat a:\n{filepath}")
                self._open_file(filepath)
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut generar el llistat general.")

    def print_banking_report(self):
        """Genera e imprime el listado de datos bancarios."""
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar llistat de dades bancàries", "llistat_bancari.pdf", "PDF Files (*.pdf)")
        if filepath:
            if self.view_model.generate_banking_report(filepath):
                QMessageBox.information(self, "Llistat Generat", f"El llistat de dades bancàries s'ha generat a:\n{filepath}")
                self._open_file(filepath)
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut generar el llistat bancari.")
    
    def _open_file(self, filepath):
        """Abre un archivo con la aplicación predeterminada del sistema."""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{filepath}"')
            else:  # Linux y otros
                os.system(f'xdg-open "{filepath}"')
        except Exception as e:
            print(f"No se pudo abrir el archivo: {e}")
            # Alternativa usando QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))