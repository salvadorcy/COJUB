from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from models.activitat import Activitat
from viewmodels.activitat_viewmodel import ActivitatViewModel


class AddSociActivitatView(QDialog):
    """Diálogo para añadir un socio activo a una actividad."""

    def __init__(self, viewmodel: ActivitatViewModel, activitat: Activitat, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.activitat = activitat
        self.db_model = viewmodel.db_model
        self.socis_data = {}

        self.setWindowTitle("Afegir Soci a l'Activitat")
        self.setMinimumWidth(500)

        self.init_ui()
        self.load_socis()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout()

        form = QFormLayout()

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cerca per ID, nom o NIF...")
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.txt_search.setCompleter(self.completer)
        self.txt_search.textChanged.connect(self.on_search_changed)
        form.addRow("Buscar Soci *:", self.txt_search)

        self.cmb_tipus = QComboBox()
        self.cmb_tipus.addItems(["Soci", "No Soci"])
        self.cmb_tipus.currentIndexChanged.connect(self.on_tipus_changed)
        form.addRow("Tipus *:", self.cmb_tipus)

        self.spin_import = QDoubleSpinBox()
        self.spin_import.setRange(0, 9999.99)
        self.spin_import.setDecimals(2)
        self.spin_import.setSuffix(" €")
        self.spin_import.setValue(self.activitat.preu_soci)
        form.addRow("Import *:", self.spin_import)

        layout.addLayout(form)

        nota = QLabel("* Camps obligatoris")
        nota.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(nota)

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
        """Carga socios activos para el autocompletado."""
        query = """
            SELECT FAMID, FAMNom, FAMNIF
            FROM scazorla_sa.G_Socis
            WHERE ISNULL(bBaixa, 0) = 0
            ORDER BY FAMNom, FAMID
        """

        try:
            self.db_model.ensure_connection()
            with self.db_model.conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            search_items = []
            self.socis_data = {}

            for famid, nom, nif in rows:
                famid_text = "" if famid is None else str(famid).strip()
                nom_text = "" if nom is None else str(nom).strip()
                nif_text = "" if nif is None else str(nif).strip()
                display_text = f"{famid_text} - {nom_text}"
                if nif_text:
                    display_text += f" - {nif_text}"

                self.socis_data[display_text] = famid_text
                search_items.append(display_text)

            self.completer_model.setStringList(search_items)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error carregant socis: {str(e)}")

    def on_search_changed(self, text: str):
        """Activa el botón solo cuando la selección coincide con un socio válido."""
        self.btn_afegir.setEnabled(text in self.socis_data)

    def on_tipus_changed(self, index: int):
        """Cambia el precio según el tipo de socio."""
        if index == 0:
            self.spin_import.setValue(self.activitat.preu_soci)
        else:
            self.spin_import.setValue(self.activitat.preu_no_soci)

    def add_soci(self):
        """Añade el socio seleccionado a la actividad."""
        search_text = self.txt_search.text().strip()

        if search_text not in self.socis_data:
            QMessageBox.warning(self, "Error", "Selecciona un soci vàlid")
            return

        soci_famid = self.socis_data[search_text]
        es_soci = self.cmb_tipus.currentIndex() == 0
        preu = self.spin_import.value()

        if self.viewmodel.add_soci_to_activitat(self.activitat.id, soci_famid, es_soci, preu):
            self.accept()
