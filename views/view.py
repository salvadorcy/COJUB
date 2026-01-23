from PyQt6.QtWidgets import QFileDialog, QPlainTextEdit
import os
import platform
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QCheckBox, QGroupBox, QFileDialog, QDateEdit, QTextEdit, QCompleter, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QDesktopServices
from PyQt6.QtCore import QUrl
from datetime import datetime
from .style_config import STYLE_CONFIG
import platform

class SocioDialog(QDialog):
    """Diálogo para agregar o editar un socio."""
    def __init__(self, parent=None, socio=None, todos_socis=None):
        super().__init__(parent)
        self.setWindowTitle("Edita Soci" if socio else "Afegeix Soci")
        self.setGeometry(100, 100, 1000, 650)  # Más ancho para 2 columnas
        self.socio_data = socio
        self.todos_socis = todos_socis if todos_socis else []

        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # ====================================================================
        # SCROLL AREA
        # ====================================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.fields = {}
        
        # ====================================================================
        # LAYOUT DE 2 COLUMNAS
        # ====================================================================
        columns_layout = QHBoxLayout()
        
        # ====================================================================
        # COLUMNA IZQUIERDA - Datos Personales
        # ====================================================================
        left_group = QGroupBox("Dades Personals")
        left_form = QFormLayout()
        left_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # ID
        self.fields["FAMID"] = QLineEdit()
        self.fields["FAMID"].setReadOnly(True)
        self.fields["FAMID"].setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fields["FAMID"].setEnabled(False)
        self.fields["FAMID"].setStyleSheet("QLineEdit:disabled { background-color: #f0f0f0; color: #666666; border: 1px solid #cccccc; }")
        left_form.addRow("ID", self.fields["FAMID"])
        
        # NIF
        self.fields["FAMNIF"] = QLineEdit()
        left_form.addRow("NIF", self.fields["FAMNIF"])
        
        # Nom
        self.fields["FAMNom"] = QLineEdit()
        left_form.addRow("Nom", self.fields["FAMNom"])
        
        # Adreça
        self.fields["FAMAdressa"] = QLineEdit()
        left_form.addRow("Adreça", self.fields["FAMAdressa"])
        
        # Població
        self.fields["FAMPoblacio"] = QLineEdit()
        left_form.addRow("Població", self.fields["FAMPoblacio"])
        
        # Codi Postal
        self.fields["FAMCodPos"] = QLineEdit()
        left_form.addRow("Codi Postal", self.fields["FAMCodPos"])
        
        # Telèfon
        self.fields["FAMTelefon"] = QLineEdit()
        left_form.addRow("Telèfon", self.fields["FAMTelefon"])
        
        # Mòbil
        self.fields["FAMMobil"] = QLineEdit()
        left_form.addRow("Mòbil", self.fields["FAMMobil"])
        
        # Correu electrònic
        self.fields["FAMEmail"] = QLineEdit()
        left_form.addRow("Correu electrònic", self.fields["FAMEmail"])
        
        # Telèfon Emergència
        self.fields["FAMTelefonEmergencia"] = QLineEdit()
        left_form.addRow("Telèfon Emergència", self.fields["FAMTelefonEmergencia"])
        
        # Data Naixement
        self.fields["FAMDataNaixement"] = QLineEdit()
        left_form.addRow("Data Naixement (YYYY-MM-DD)", self.fields["FAMDataNaixement"])
        
        left_group.setLayout(left_form)
        
        # ====================================================================
        # COLUMNA DERECHA - Datos Administrativos
        # ====================================================================
        right_group = QGroupBox("Dades Administratives")
        right_form = QFormLayout()
        right_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Data Alta
        self.fields["FAMDataAlta"] = QLineEdit()
        right_form.addRow("Data Alta (YYYY-MM-DD)", self.fields["FAMDataAlta"])
        
        # IBAN
        self.fields["FAMIBAN"] = QLineEdit()
        right_form.addRow("IBAN", self.fields["FAMIBAN"])
        
        # BIC
        self.fields["FAMBIC"] = QLineEdit()
        right_form.addRow("BIC", self.fields["FAMBIC"])
        
        # Sexe
        self.fields["FAMSexe"] = QLineEdit()
        right_form.addRow("Sexe (H/M)", self.fields["FAMSexe"])
        
        # Soci Parella
        self.fields["FAMSociReferencia"] = QLineEdit()
        right_form.addRow("Soci Parella", self.fields["FAMSociReferencia"])
        
        # Label para nombre de pareja
        self.label_parella_nom = QLabel("")
        self.label_parella_nom.setStyleSheet("""
            QLabel {
                color: #0066cc;
                font-weight: bold;
                font-size: 10pt;
                padding: 2px;
                background-color: #f0f8ff;
                border-radius: 3px;
            }
        """)
        self.label_parella_nom.setMinimumHeight(25)
        right_form.addRow("", self.label_parella_nom)
        
        # Botón crear socio pareja
        self.btn_crear_parella = QPushButton("➕ Crear Nou Soci Parella")
        self.btn_crear_parella.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 3px;
                border: none;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_crear_parella.setMaximumWidth(200)
        self.btn_crear_parella.clicked.connect(self.crear_nuevo_socio_parella)
        self.btn_crear_parella.hide()
        right_form.addRow("", self.btn_crear_parella)
        
        # Quota
        self.fields["FAMQuota"] = QLineEdit()
        right_form.addRow("Quota", self.fields["FAMQuota"])
        
        # Observacions
        self.fields["FAMObservacions"] = QTextEdit()
        self.fields["FAMObservacions"].setMinimumHeight(80)
        self.fields["FAMObservacions"].setMaximumHeight(120)
        right_form.addRow("Observacions", self.fields["FAMObservacions"])
        
        right_group.setLayout(right_form)
        
        # Añadir columnas al layout
        columns_layout.addWidget(left_group)
        columns_layout.addWidget(right_group)
        scroll_layout.addLayout(columns_layout)
        
        # ====================================================================
        # SECCIÓN INFERIOR - Data Baixa y Checkboxes
        # ====================================================================
        bottom_layout = QHBoxLayout()
        
        # Data Baixa (condicional)
        baixa_group = QGroupBox("Data de Baixa")
        baixa_form = QFormLayout()
        self.fields["FAMDataBaixa"] = QLineEdit()
        self.fields["FAMDataBaixa"].setReadOnly(True)
        baixa_form.addRow("Data Baixa (YYYY-MM-DD)", self.fields["FAMDataBaixa"])
        baixa_group.setLayout(baixa_form)
        self.baixa_container = baixa_group
        self.baixa_container.hide()  # Oculto por defecto
        
        # Checkboxes
        checkboxes_group = QGroupBox("Opcions")
        checkboxes_layout = QVBoxLayout()
        
        self.fields["bBaixa"] = QCheckBox("Baixa")
        self.fields["FAMbPagamentDomiciliat"] = QCheckBox("Pagament Domiciliat")
        self.fields["FAMbRebutCobrat"] = QCheckBox("Rebut Cobrat")
        self.fields["FAMPagamentFinestreta"] = QCheckBox("Pagament Finestreta")
        
        checkboxes_layout.addWidget(self.fields["bBaixa"])
        checkboxes_layout.addWidget(self.fields["FAMbPagamentDomiciliat"])
        checkboxes_layout.addWidget(self.fields["FAMbRebutCobrat"])
        checkboxes_layout.addWidget(self.fields["FAMPagamentFinestreta"])
        checkboxes_group.setLayout(checkboxes_layout)
        
        bottom_layout.addWidget(self.baixa_container)
        bottom_layout.addWidget(checkboxes_group)
        scroll_layout.addLayout(bottom_layout)
        
        # Configurar scroll
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # ====================================================================
        # BOTONES
        # ====================================================================
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Desa")
        self.cancel_button = QPushButton("Cancel·la")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # ====================================================================
        # CONFIGURACIÓN DE LÍMITES Y VALIDACIONES
        # ====================================================================
        
        # Límites de caracteres
        self.fields["FAMID"].setMaxLength(5)
        self.fields["FAMNom"].setMaxLength(255)
        self.fields["FAMAdressa"].setMaxLength(255)
        self.fields["FAMPoblacio"].setMaxLength(255)
        self.fields["FAMCodPos"].setMaxLength(5)
        self.fields["FAMTelefon"].setMaxLength(20)
        self.fields["FAMMobil"].setMaxLength(20)
        self.fields["FAMTelefonEmergencia"].setMaxLength(150)
        self.fields["FAMEmail"].setMaxLength(100)
        self.fields["FAMIBAN"].setMaxLength(24)
        self.fields["FAMBIC"].setMaxLength(15)
        self.fields["FAMNIF"].setMaxLength(10)
        self.fields["FAMQuota"].setMaxLength(12)
        self.fields["FAMSexe"].setMaxLength(1)
        self.fields["FAMSociReferencia"].setMaxLength(255)
        
        # Tooltips
        self.fields["FAMSociReferencia"].setToolTip("Escriu l'ID del soci parella o comença a escriure el nom per cercar")
        
        # Conversión a mayúsculas
        campos_mayusculas = [
            "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
            "FAMTelefon", "FAMMobil", "FAMTelefonEmergencia",
            "FAMIBAN", "FAMBIC", "FAMObservacions",
            "FAMNIF", "FAMSexe", "FAMSociReferencia"
        ]
        
        for campo in campos_mayusculas:
            if campo in self.fields:
                if isinstance(self.fields[campo], QLineEdit):
                    self.fields[campo].textChanged.connect(
                        lambda text, field=self.fields[campo]: field.setText(text.upper())
                    )
                elif isinstance(self.fields[campo], QTextEdit):
                    def make_uppercase_handler(field):
                        def handler():
                            field.blockSignals(True)
                            cursor_position = field.textCursor().position()
                            text = field.toPlainText()
                            field.setPlainText(text.upper())
                            cursor = field.textCursor()
                            cursor.setPosition(min(cursor_position, len(text)))
                            field.setTextCursor(cursor)
                            field.blockSignals(False)
                        return handler
                    self.fields[campo].textChanged.connect(make_uppercase_handler(self.fields[campo]))
        
        # Email a minúsculas
        self.fields["FAMEmail"].textChanged.connect(
            lambda text: self.fields["FAMEmail"].setText(text.lower())
        )
        
        # Límite de Observacions
        def limit_observacions_length():
            field = self.fields["FAMObservacions"]
            text = field.toPlainText()
            if len(text) > 2048:
                field.blockSignals(True)
                cursor = field.textCursor()
                cursor_pos = cursor.position()
                field.setPlainText(text[:2048])
                cursor.setPosition(min(cursor_pos, 2048))
                field.setTextCursor(cursor)
                field.blockSignals(False)
        
        self.fields["FAMObservacions"].textChanged.connect(limit_observacions_length)
        
        # Autocompletado Soci Parella
        if self.todos_socis:
            sugerencias = [f"{socio.FAMID.strip()} - {socio.FAMNom}" for socio in self.todos_socis]
            completer = QCompleter(sugerencias)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.fields["FAMSociReferencia"].setCompleter(completer)
            self.fields["FAMSociReferencia"].textChanged.connect(self.actualizar_nombre_parella)
        
        # Conectar checkbox Baixa
        self.fields["bBaixa"].stateChanged.connect(self.toggle_data_baixa)
        
        # Rellenar formulario
        self.fill_form()
    
    def toggle_data_baixa(self, state):
        """Muestra u oculta el campo Data Baixa según el checkbox."""
        if state == Qt.CheckState.Checked.value:
            self.baixa_container.show()
        else:
            self.baixa_container.hide()
    
    def calcular_nuevo_id(self):
        """Calcula automáticamente el siguiente ID disponible."""
        if not self.todos_socis:
            return "1001"
        
        ids_numericos = []
        for socio in self.todos_socis:
            try:
                id_num = int(socio.FAMID.strip())
                ids_numericos.append(id_num)
            except (ValueError, AttributeError):
                continue
        
        if not ids_numericos:
            return "1001"
        
        return str(max(ids_numericos) + 1)
    
    def fill_form(self):
        """Rellena el formulario con los datos del socio si existe."""
        if self.socio_data:
            self.fields["FAMID"].setEnabled(False)
            
            ordered_keys = [
                "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
                "FAMTelefon", "FAMMobil", "FAMEmail", "FAMDataAlta", "FAMIBAN",
                "FAMBIC", "bBaixa", "FAMObservacions", "FAMNIF", "FAMDataNaixement",
                "FAMQuota", "FAMDataBaixa", "FAMSexe", "FAMSociReferencia",
                "FAMbPagamentDomiciliat", "FAMbRebutCobrat", "FAMPagamentFinestreta",
                "FAMTelefonEmergencia"
            ]

            for i, key in enumerate(ordered_keys):
                if key in self.fields and i < len(self.socio_data):
                    widget = self.fields[key]
                    value = self.socio_data[i]
                    
                    if isinstance(widget, QLineEdit):
                        if key in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"]:
                            if value and isinstance(value, datetime):
                                widget.setText(value.strftime('%Y-%m-%d'))
                            else:
                                widget.setText("")
                        elif key == "FAMQuota":
                            widget.setText(str(value) if value is not None and value != "" else "")
                        else:
                            text_value = str(value).strip() if value is not None else ""
                            widget.setText(text_value)
                    elif isinstance(widget, QTextEdit):
                        widget.setPlainText(str(value) if value is not None else "")
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
        else:
            nuevo_id = self.calcular_nuevo_id()
            self.fields["FAMID"].setText(nuevo_id)
            self.fields["FAMID"].setEnabled(False)
            self.fields["FAMDataAlta"].setText(datetime.now().strftime('%Y-%m-%d'))
            self.fields["bBaixa"].setChecked(False)

        QTimer.singleShot(100, self.actualizar_nombre_parella)
    
    def get_data(self):
        """Devuelve los datos del formulario como una tupla."""
        from datetime import datetime
        data = []
        
        ordered_keys = [
            "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
            "FAMTelefon", "FAMMobil", "FAMEmail", "FAMDataAlta", "FAMIBAN",
            "FAMBIC", "bBaixa", "FAMObservacions", "FAMNIF", "FAMDataNaixement",
            "FAMQuota", "FAMDataBaixa", "FAMSexe", "FAMSociReferencia",
            "FAMbPagamentDomiciliat", "FAMbRebutCobrat", "FAMPagamentFinestreta",
            "FAMTelefonEmergencia"
        ]
        
        for key in ordered_keys:
            if key in self.fields:
                widget = self.fields[key]
                value = None
                
                if isinstance(widget, QLineEdit):
                    value = widget.text().strip()
                    if key in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"]:
                        value = datetime.strptime(value, '%Y-%m-%d') if value else None
                    elif key == "FAMQuota":
                        try:
                            value = float(value.replace(',', '.')) if value else None
                        except:
                            value = None
                    elif value == "":
                        value = None
                elif isinstance(widget, QTextEdit):
                    value = widget.toPlainText().strip() or None
                elif isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                
                data.append(value)
        
        return tuple(data)
    
    def actualizar_nombre_parella(self):
        """Actualiza el label con el nombre del socio pareja."""
        id_parella = self.fields["FAMSociReferencia"].text().strip()
        
        if not id_parella:
            self.label_parella_nom.setText("")
            self.btn_crear_parella.hide()
            return
        
        if " - " in id_parella:
            id_solo = id_parella.split(" - ")[0].strip()
            self.fields["FAMSociReferencia"].textChanged.disconnect(self.actualizar_nombre_parella)
            self.fields["FAMSociReferencia"].setText(id_solo)
            self.fields["FAMSociReferencia"].textChanged.connect(self.actualizar_nombre_parella)
            id_parella = id_solo
        
        socio_encontrado = next((s for s in self.todos_socis if s.FAMID.strip() == id_parella), None)
        
        if socio_encontrado:
            self.label_parella_nom.setText(f"✓ {socio_encontrado.FAMNom}")
            self.label_parella_nom.setStyleSheet("QLabel { color: #006600; font-weight: bold; font-size: 10pt; padding: 2px; background-color: #e8f5e9; border-radius: 3px; }")
            self.btn_crear_parella.hide()
        else:
            self.label_parella_nom.setText(f"✗ ID '{id_parella}' no trobat")
            self.label_parella_nom.setStyleSheet("QLabel { color: #cc0000; font-weight: bold; font-size: 10pt; padding: 2px; background-color: #ffebee; border-radius: 3px; }")
            self.btn_crear_parella.show()
    
    def crear_nuevo_socio_parella(self):
        """Abre diálogo para crear nuevo socio pareja."""
        id_propuesto = self.fields["FAMSociReferencia"].text().strip()
        
        reply = QMessageBox.question(
            self, "Crear Nou Soci",
            f"Vols crear un nou soci amb l'ID '{id_propuesto}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        nuevo_socio_dialog = SocioDialog(self, None, self.todos_socis)
        
        if id_propuesto and len(id_propuesto) <= 5:
            nuevo_socio_dialog.fields["FAMID"].setEnabled(True)
            nuevo_socio_dialog.fields["FAMID"].setText(id_propuesto)
            nuevo_socio_dialog.fields["FAMID"].setEnabled(False)
        
        if nuevo_socio_dialog.exec() == QDialog.DialogCode.Accepted:
            nuevo_socio_data = nuevo_socio_dialog.get_data()
            
            if hasattr(self.parent(), 'view_model'):
                view_model = self.parent().view_model
                success = view_model.save_socio(nuevo_socio_data)
                
                if success:
                    QMessageBox.information(self, "Èxit", f"Soci '{nuevo_socio_data[1]}' creat correctament.")
                    self.todos_socis = view_model.all_socis
                    
                    # Actualizar autocompletador
                    sugerencias = [f"{s.FAMID.strip()} - {s.FAMNom}" for s in self.todos_socis]
                    completer = QCompleter(sugerencias)
                    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    completer.setFilterMode(Qt.MatchFlag.MatchContains)
                    self.fields["FAMSociReferencia"].setCompleter(completer)
                    
                    self.actualizar_nombre_parella()
                else:
                    QMessageBox.critical(self, "Error", "No s'ha pogut crear el soci.")


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

        # Contenedor principal de los botones (Horizontal)
        top_functions_layout = QHBoxLayout()

        # 1. Grupo de Gestión de Socios (CRUD)
        socis_group = QGroupBox("Gestió de Socis")
        socis_group.setFont(QFont(STYLE_CONFIG["font_family"], STYLE_CONFIG["font_size_bold"]))
        socis_layout = QHBoxLayout(socis_group)
        
        self.add_button = QPushButton("Afegeix Soci")
        self.edit_button = QPushButton("Edita Soci")
        self.delete_button = QPushButton("Elimina Soci")
        
        socis_layout.addWidget(self.add_button)
        socis_layout.addWidget(self.edit_button)
        socis_layout.addWidget(self.delete_button)
        
        top_functions_layout.addWidget(socis_group)

        # 2. Grupo de Informes y Configuració
        reports_config_group = QGroupBox("Informes i Configuració")
        reports_config_group.setFont(QFont(STYLE_CONFIG["font_family"], STYLE_CONFIG["font_size_bold"]))
        reports_config_layout = QHBoxLayout(reports_config_group)
        
        self.config_button = QPushButton("Configuració")
        self.sepa_button = QPushButton("Genera Remesa SEPA")
        self.print_general_button = QPushButton("Imprimeix Llistat General")
        self.print_banking_button = QPushButton("Imprimeix Dades Bancàries")
        self.print_etiquetes_button = QPushButton("Imprimeix Etiquetes")
        

        reports_config_layout.addWidget(self.config_button)
        reports_config_layout.addWidget(self.sepa_button)
        reports_config_layout.addWidget(self.print_general_button)
        reports_config_layout.addWidget(self.print_banking_button)
        reports_config_layout.addWidget(self.print_etiquetes_button)
        
        top_functions_layout.addWidget(reports_config_group)
        
        main_layout.addLayout(top_functions_layout)
        
        # Conexiones de botones (tras crear los objetos)
        self.add_button.clicked.connect(self.add_socio)
        self.edit_button.clicked.connect(self.edit_socio)
        self.delete_button.clicked.connect(self.delete_socio)
        self.config_button.clicked.connect(self.edit_dades)
        self.sepa_button.clicked.connect(self.generar_sepa)
        self.print_general_button.clicked.connect(self.print_general_report)
        self.print_banking_button.clicked.connect(self.print_banking_report)
        self.print_etiquetes_button.clicked.connect(self.print_etiquetas)
        
        
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
        dialog = SocioDialog(self, socio=None, todos_socis=self.view_model.all_socis)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            if self.view_model.save_socio(new_data):
                QMessageBox.information(self, "Èxit", "Soci afegit correctament.")
            else:
                QMessageBox.critical(self, "Error", "No s'ha pogut afegir el soci.")
    
    def edit_socio(self):
        """Edita el socio seleccionado."""
        selected_row = self.socis_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Avís", "Si us plau, selecciona un soci.")
            return
    
        self.view_model.set_selected_socio(selected_row)
        socio_data = self.view_model.get_selected_socio_data()
    
        if socio_data:
            dialog = SocioDialog(self, socio_data, todos_socis=self.view_model.all_socis)
        
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                success = self.view_model.save_socio(new_data)
            
                if success:
                    QMessageBox.information(self, "Èxit", "Soci actualitzat correctament.")
                    self.refresh_table()
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
            
    def print_etiquetas(self):
        """Genera e imprime etiquetas de socios en PDF."""
        # Pedir al usuario dónde guardar el archivo
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Desa les Etiquetes",
            "etiquetas_socios.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filepath:
            # Asegurarse de que tiene extensión .pdf
            if not filepath.endswith('.pdf'):
                filepath += '.pdf'
            
            # Generar el PDF
            if self.view_model.generate_etiquetas(filepath):
                QMessageBox.information(
                    self,
                    "Èxit",
                    f"Etiquetes generades correctament.\n\nArxiu: {filepath}"
                )
                # Abrir el PDF automáticamente
                self._open_file(filepath)
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No s'han pogut generar les etiquetes."
                )