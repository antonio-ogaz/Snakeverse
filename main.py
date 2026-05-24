"""
main.py — Punto de entrada de SNAKEVERSE
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from pantalla.inicio import PantallaInicio


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNAKEVERSE")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        self.setCentralWidget(PantallaInicio(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())