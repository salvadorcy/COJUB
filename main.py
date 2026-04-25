import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from views.view import MainWindow
from viewmodels.viewmodel import ViewModel
from models.model import DatabaseModel
from viewmodels.activitat_viewmodel import ActivitatViewModel
from views.activitats_view import ActivitatsView
from pathlib import Path


def resource_path(relative_path: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(base_path / relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/app_icon.ico")))
    
    # Crear instancia del modelo de base de datos (compartida)
    db_model = DatabaseModel()
    
    # Crear ViewModel principal para socios
    view_model = ViewModel(db_model)
    
    # Crear ViewModel para actividades (usa el mismo db_model)
    activitat_viewmodel = ActivitatViewModel(db_model)
    
    # Crear vista principal y pasarle ambos viewmodels
    view = MainWindow(view_model, activitat_viewmodel)
    
    view.showMaximized()
    
    sys.exit(app.exec())
