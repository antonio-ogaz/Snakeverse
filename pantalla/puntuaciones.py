from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from utilidad.datos_prueba import puntuaciones

class PuntuacionesWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("TABLA DE PUNTUACIONES"))

        for jugador, puntos in puntuaciones.items():
            layout.addWidget(QLabel(f"{jugador}: {puntos}"))

        volver = QLabel("VOLVER")
        volver.setStyleSheet("color: blue; font-weight: bold;")
        layout.addWidget(volver)

        self.setLayout(layout)