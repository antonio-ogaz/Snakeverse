import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPalette, QColor
from pantalla.inicio import InicioWindow

class Snakeverse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        self.setGeometry(100, 100, 800, 600)

        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        self.setCentralWidget(InicioWindow(self))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Snakeverse()
    ventana.show()
    sys.exit(app.exec())
