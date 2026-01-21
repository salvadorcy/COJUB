from PyQt6.QtWidgets import QFileDialog, QPlainTextEdit
import os
import platform
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QCheckBox, QGroupBox, QFileDialog, QDateEdit, QTextEdit, QCompleter
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
        self.setGeometry(100, 100, 650, 600)
        self.socio_data = socio
        self.todos_socis = todos_socis if todos_socis else []

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.fields = {}
        # ============================================================================
        # CAMPOS SIMPLIFICADOS - 22 campos (coincide con model.py)
        # ============================================================================
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
            ("FAMIBAN", QLineEdit(), "IBAN"),
            ("FAMBIC", QLineEdit(), "BIC"),
            ("bBaixa", QCheckBox(), "Baixa"),
            ("FAMObservacions", QTextEdit(), "Observacions"),
            ("FAMNIF", QLineEdit(), "NIF"),
            ("FAMDataNaixement", QLineEdit(), "Data Naixement (YYYY-MM-DD)"),
            ("FAMQuota", QLineEdit(), "Quota"),
            ("FAMDataBaixa", QLineEdit(), "Data Baixa (YYYY-MM-DD)"),
            ("FAMSexe", QLineEdit(), "Sexe (H/M)"),
            ("FAMSociReferencia", QLineEdit(), "Soci Parella"),
            ("FAMbPagamentDomiciliat", QCheckBox(), "Pagament Domiciliat"),
            ("FAMbRebutCobrat", QCheckBox(), "Rebut Cobrat"),
            ("FAMPagamentFinestreta", QCheckBox(), "Pagament Finestreta"),
            ("FAMTelefonEmergencia", QLineEdit(), "Telèfon Emergència")
        ]

        for attr, widget, label_text in fields_config:
            if isinstance(widget, QCheckBox):
                self.fields[attr] = widget
                widget.setText(label_text)
                self.form_layout.addRow(widget)
            else:
                self.fields[attr] = widget
                # Configurar altura para QTextEdit
                if isinstance(widget, QTextEdit):
                    widget.setMinimumHeight(100)  # Altura mínima en píxeles
                    widget.setMaximumHeight(150)  # Altura máxima en píxeles
                self.form_layout.addRow(label_text, widget)

        # Crear label para mostrar el nombre del socio pareja
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

        # ============================================================================
        # LÍMITES DE CARACTERES SEGÚN BASE DE DATOS
        # ============================================================================

        # Campos CHAR(5)
        self.fields["FAMID"].setMaxLength(5)              # char(5)
        self.fields["FAMCodPos"].setMaxLength(5)          # char(5)
        self.fields["FAMSociReferencia"].setMaxLength(255)  # char(5)

        # Campos CHAR(1)
        self.fields["FAMSexe"].setMaxLength(1)            # char(1)

        # Campos NVARCHAR
        self.fields["FAMNom"].setMaxLength(255)           # nvarchar(255)
        self.fields["FAMAdressa"].setMaxLength(255)       # nvarchar(255)
        self.fields["FAMPoblacio"].setMaxLength(255)      # nvarchar(255)
        self.fields["FAMTelefon"].setMaxLength(20)        # nvarchar(20)
        self.fields["FAMMobil"].setMaxLength(20)          # nvarchar(20)
        self.fields["FAMTelefonEmergencia"].setMaxLength(150)
        
        parella_row = None
        for i in range(self.form_layout.rowCount()):
            label_item = self.form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label_item and label_item.widget():
                if label_item.widget().text() == "Soci Parella":
                    parella_row = i
                    break

        if parella_row is not None:
            # Insertar label debajo del campo
            self.form_layout.insertRow(parella_row + 1, "", self.label_parella_nom)

        # Configurar autocompletado
        if self.todos_socis:
            # Crear lista de sugerencias: "ID - Nombre"
            sugerencias = [f"{socio.FAMID.strip()} - {socio.FAMNom}" for socio in self.todos_socis]
    
            completer = QCompleter(sugerencias)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
    
            self.fields["FAMSociReferencia"].setCompleter(completer)
    
            # Conectar evento para actualizar el nombre cuando cambie el ID
            self.fields["FAMSociReferencia"].textChanged.connect(self.actualizar_nombre_parella)

        # Crear tooltip mejorado
        self.fields["FAMSociReferencia"].setToolTip(
            "Escriu l'ID del soci parella o comença a escriure el nom per cercar.\n"
            "Exemples: 1001 o 'JUAN'"
        )
        self.fields["FAMEmail"].setMaxLength(100)         # nvarchar(100)
        self.fields["FAMIBAN"].setMaxLength(24)           # nvarchar(24)
        self.fields["FAMBIC"].setMaxLength(15)            # nvarchar(15)
        self.fields["FAMNIF"].setMaxLength(10)            # nvarchar(10)
        #self.fields["FAMObservacions"].setMaxLength(2048) # nvarchar(2048)

        def limit_observacions_length():
            """Limita el campo Observacions a 2048 caracteres."""
            text = self.fields["FAMObservacions"].toPlainText()
            if len(text) > 2048:
                # Truncar a 2048 caracteres
                cursor = self.fields["FAMObservacions"].textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.deletePreviousChar()
                self.fields["FAMObservacions"].setTextCursor(cursor)

        self.fields["FAMObservacions"].textChanged.connect(limit_observacions_length)

        # Campos numéricos (limitar caracteres para evitar valores excesivos)
        self.fields["FAMQuota"].setMaxLength(12)          # numeric (ej: 999999.99)

        campos_mayusculas = [
            "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
            "FAMTelefon", "FAMMobil", "FAMTelefonEmergencia",  # ← AÑADIR AQUÍ
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
                            # Bloquear señales para evitar recursión
                            field.blockSignals(True)
                            cursor_position = field.textCursor().position()
                            text = field.toPlainText()
                            field.setPlainText(text.upper())
                            # Restaurar posición del cursor
                            cursor = field.textCursor()
                            cursor.setPosition(min(cursor_position, len(text)))
                            field.setTextCursor(cursor)
                            field.blockSignals(False)
                        return handler
                    self.fields[campo].textChanged.connect(make_uppercase_handler(self.fields[campo]))

        # Convertir email a minúsculas automáticamente
        self.fields["FAMEmail"].textChanged.connect(
            lambda text: self.fields["FAMEmail"].setText(text.lower())
        )
        
        # ============================================================================
        # CONFIGURACIÓN DE CAMPOS
        # ============================================================================
        # Campo ID: readonly, no focusable, estilo deshabilitado
        self.fields["FAMID"].setReadOnly(True)
        self.fields["FAMID"].setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fields["FAMID"].setEnabled(False)
        self.fields["FAMID"].setStyleSheet("""
            QLineEdit:disabled {
                background-color: #f0f0f0;
                color: #666666;
                border: 1px solid #cccccc;
            }
        """)
        
        # Campos de texto largos
        self.fields["FAMNom"].setMinimumWidth(300)
        self.fields["FAMAdressa"].setMinimumWidth(300)
        self.fields["FAMObservacions"].setMinimumWidth(300)
        
        # Campo de baja: readonly
        self.fields["FAMDataBaixa"].setReadOnly(True)

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

    def calcular_nuevo_id(self):
        """
        Calcula automáticamente el siguiente ID disponible.
        """
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
        
        max_id = max(ids_numericos)
        nuevo_id = max_id + 1
        
        return str(nuevo_id)
    
    def fill_form(self):
        """Rellena el formulario con los datos del socio si existe."""
        if self.socio_data:
            # Modo edición: deshabilitar campo ID
            self.fields["FAMID"].setEnabled(False)
            
            # ============================================================================
            # ORDEN DE CAMPOS - 22 campos (DEBE COINCIDIR CON model.py)
            # ============================================================================
            ordered_keys = [
                "FAMID",
                "FAMNom",
                "FAMAdressa",
                "FAMPoblacio",
                "FAMCodPos",
                "FAMTelefon",
                "FAMMobil",
                "FAMEmail",
                "FAMDataAlta",
                "FAMIBAN",
                "FAMBIC",
                "bBaixa",
                "FAMObservacions",
                "FAMNIF",
                "FAMDataNaixement",
                "FAMQuota",
                "FAMDataBaixa",
                "FAMSexe",
                "FAMSociReferencia",
                "FAMbPagamentDomiciliat",
                "FAMbRebutCobrat",
                "FAMPagamentFinestreta",
                "FAMTelefonEmergencia"
            ]

            # Rellenar los campos con los datos del socio
            for i, key in enumerate(ordered_keys):
                if key in self.fields and i < len(self.socio_data):
                    widget = self.fields[key]
                    value = self.socio_data[i]
                    
                    if isinstance(widget, QLineEdit):
                        # Manejar fechas
                        if key in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"]:
                            if value and isinstance(value, datetime):
                                widget.setText(value.strftime('%Y-%m-%d'))
                            else:
                                widget.setText("")
                        elif key == "FAMQuota":
                            if value is not None and value != "":
                                widget.setText(str(value))
                            else:
                                widget.setText("")
                        # Otros campos de texto (incluyendo FAMSociReferencia)
                        else:
                            # Limpiar espacios en blanco
                            text_value = str(value).strip() if value is not None else ""
                            widget.setText(text_value)
                    elif isinstance(widget, QTextEdit):  # ← AÑADIR ESTO
                        widget.setPlainText(str(value) if value is not None else "")
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
        else:
            # Modo nuevo: calcular ID automático
            nuevo_id = self.calcular_nuevo_id()
            self.fields["FAMID"].setText(nuevo_id)
            self.fields["FAMID"].setEnabled(False)
    
            # Establecer fecha de alta por defecto a hoy
            self.fields["FAMDataAlta"].setText(datetime.now().strftime('%Y-%m-%d'))
    
            # Establecer bBaixa a False por defecto
            self.fields["bBaixa"].setChecked(False)

        # ============================================================================
        # ACTUALIZAR NOMBRE DE SOCIO PAREJA (tanto en modo edición como nuevo)
        # ============================================================================
        # Usar QTimer para asegurar que se ejecuta después de que todo esté cargado        
        QTimer.singleShot(100, self.actualizar_nombre_parella)


        print("\n=== DEBUG FILL_FORM ===")
        print(f"Modo edición: {self.socio_data is not None}")
        if self.socio_data:
            print(f"Total campos en socio_data: {len(self.socio_data)}")
            # Buscar índice de FAMSociReferencia
            ordered_keys_temp = [
                "FAMID", "FAMNom", "FAMAdressa", "FAMPoblacio", "FAMCodPos",
                "FAMTelefon", "FAMMobil", "FAMTelefonEmergencia", "FAMEmail", "FAMDataAlta", "FAMIBAN",
                "FAMBIC", "FAMObservacions", "FAMNIF", "FAMDataNaixement",
                "FAMQuota", "FAMDataBaixa", "FAMSexe", "FAMSociReferencia",
                "FAMbPagamentDomiciliat", "FAMbRebutCobrat", "FAMPagamentFinestreta",
                "bBaixa"
            ]
            idx = ordered_keys_temp.index("FAMSociReferencia") if "FAMSociReferencia" in ordered_keys_temp else -1
            print(f"Índice FAMSociReferencia: {idx}")
            if idx >= 0 and idx < len(self.socio_data):
                print(f"Valor FAMSociReferencia: '{self.socio_data[idx]}'")
    
            valor_campo = self.fields["FAMSociReferencia"].text()
            print(f"Valor en campo después de fill: '{valor_campo}'")
        print("=======================\n")

    def get_data(self):
        """Devuelve los datos del formulario como una tupla."""
        from datetime import datetime
    
        data = []
    
        # ============================================================================
        # ORDEN DE CAMPOS - 23 campos (DEBE COINCIDIR CON model.py)
        # ============================================================================
        ordered_keys = [
            "FAMID",
            "FAMNom",
            "FAMAdressa",
            "FAMPoblacio",
            "FAMCodPos",
            "FAMTelefon",
            "FAMMobil",
            "FAMEmail",
            "FAMDataAlta",
            "FAMIBAN",
            "FAMBIC",
            "bBaixa",
            "FAMObservacions",
            "FAMNIF",
            "FAMDataNaixement",
            "FAMQuota",
            "FAMDataBaixa",
            "FAMSexe",
            "FAMSociReferencia",
            "FAMbPagamentDomiciliat",
            "FAMbRebutCobrat",
            "FAMPagamentFinestreta",
            "FAMTelefonEmergencia"
        ]
    
        for key in ordered_keys:
            if key in self.fields:
                widget = self.fields[key]
                value = None
            
                if isinstance(widget, QLineEdit):
                    value = widget.text().strip()  # ← Limpiar espacios
                
                    # Convertir fechas
                    if key in ["FAMDataAlta", "FAMDataNaixement", "FAMDataBaixa"]:
                        if value and value != "":
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d')
                            except ValueError:
                                value = None
                        else:
                            value = None
                        
                    # Convertir números (FAMQuota)
                    elif key == "FAMQuota":
                        if value and value != "":
                            try:
                                value_clean = value.replace(',', '.')
                                value = float(value_clean)
                            except (ValueError, TypeError):
                                value = None
                        else:
                            value = None
                        
                    # String vacío → None para campos opcionales
                    elif value == "":
                        value = None
                    
                elif isinstance(widget, QTextEdit):
                    value = widget.toPlainText().strip()
                    if value == "":
                        value = None
                    
                elif isinstance(widget, QCheckBox):
                    value = widget.isChecked()  # Ya es bool
            
                data.append(value)
            else:
                # Si el campo no existe en el formulario, agregar valor por defecto
                if key == "FAMQuota":
                    data.append(None)
                elif key == "bBaixa":
                    data.append(False)
                elif key in ["FAMbPagamentDomiciliat", "FAMbRebutCobrat", "FAMPagamentFinestreta"]:
                    data.append(False)
                else:
                    data.append(None)
    
        return tuple(data)

    def actualizar_nombre_parella(self):
        """Actualiza el label con el nombre del socio pareja cuando cambia el ID."""
        id_parella = self.fields["FAMSociReferencia"].text().strip()
    
        if not id_parella:
            self.label_parella_nom.setText("")
            return
    
        # Extraer solo el ID si se seleccionó de la lista (formato: "ID - Nombre")
        if " - " in id_parella:
            id_solo = id_parella.split(" - ")[0].strip()
        
            # CRÍTICO: Desconectar la señal antes de modificar el texto
            self.fields["FAMSociReferencia"].textChanged.disconnect(self.actualizar_nombre_parella)
        
            # Actualizar el campo con solo el ID
            self.fields["FAMSociReferencia"].setText(id_solo)
        
            # Reconectar la señal
            self.fields["FAMSociReferencia"].textChanged.connect(self.actualizar_nombre_parella)
        
            # Usar el ID extraído para buscar
            id_parella = id_solo
    
        # Buscar el socio por ID
        socio_encontrado = None
        for socio in self.todos_socis:
            if socio.FAMID.strip() == id_parella:
                socio_encontrado = socio
                break
    
        if socio_encontrado:
            self.label_parella_nom.setText(f"✓ {socio_encontrado.FAMNom}")
            self.label_parella_nom.setStyleSheet("""
                QLabel {
                    color: #006600;
                    font-weight: bold;
                    font-size: 10pt;
                    padding: 2px;
                    background-color: #e8f5e9;
                    border-radius: 3px;
                }
            """)
        else:
            self.label_parella_nom.setText(f"✗ ID '{id_parella}' no trobat")
            self.label_parella_nom.setStyleSheet("""
                QLabel {
                    color: #cc0000;
                    font-weight: bold;
                    font-size: 10pt;
                    padding: 2px;
                    background-color: #ffebee;
                    border-radius: 3px;
                }
            """)


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
        selected_row = self.table.currentRow()
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