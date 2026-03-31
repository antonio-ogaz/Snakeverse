import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from pantalla.inicio import InicioWindow

class Snakeverse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snakeverse")
        self.setGeometry(100, 100, 800, 600)
        self.setCentralWidget(InicioWindow(self))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Snakeverse()
    ventana.show()
    sys.exit(app.exec())