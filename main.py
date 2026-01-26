import sys
from PyQt6.QtWidgets import QApplication
from views.view import MainWindow
from viewmodels.viewmodel import ViewModel
from models.model import DatabaseModel
from viewmodels.activitat_viewmodel import ActivitatViewModel
from views.activitats_view import ActivitatsView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
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