import sys
from PyQt6.QtWidgets import QApplication
from views.view import MainWindow
from viewmodels.viewmodel import ViewModel
from models.model import DatabaseModel
from viewmodels.activitat_viewmodel import ActivitatViewModel
from views.activitats_view import ActivitatsView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear instancias de las capas del patrón MVVM
    model = DatabaseModel()
    view_model = ViewModel(model)
    view = MainWindow(view_model)
    
    view.showMaximized()
    
    sys.exit(app.exec())