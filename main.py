import sys
from PyQt6.QtWidgets import QApplication
from views.view import MainWindow
from viewmodels.viewmodel import ViewModel
from models.model import DatabaseModel

def load_stylesheet(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ No se pudo cargar la hoja de estilos '{path}': {e}")
        return ""
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("style/style.qss"))
    
    # Crear instancias de las capas del patrón MVVM
    model = DatabaseModel()
    view_model = ViewModel(model)
    view = MainWindow(view_model)
    
    view.showMaximized()
    
    sys.exit(app.exec())