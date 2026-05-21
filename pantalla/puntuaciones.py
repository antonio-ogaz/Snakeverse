from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame)

from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from utilidad.datos_prueba import puntuaciones

class PuntuacionesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
        titulo = QLabel("TABLA DE PUNTUACIONES")
        titulo.setFont(QFont("Arial", 26, QFont.Bold))

        titulo.setStyleSheet("""
            color: gold;
            margin-bottom: 20px;
        """)

        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)

        posicion = 1

        for jugador, puntos in puntuaciones.items():
            tarjeta = QLabel(
                f"{posicion}.  {jugador}   -   {puntos} pts"
            )
            tarjeta.setFont(QFont("Arial", 18, QFont.Bold))
            tarjeta.setStyleSheet("""
                background-color: #1f1f35;
                color: white;
                border: 2px solid blue;
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
            """)

            tarjeta.setAlignment(Qt.AlignCenter)
            layout.addWidget(tarjeta)
            posicion += 1

        btn_volver = QPushButton("VOLVER AL MENÚ")
        btn_volver.setStyleSheet("""
            background-color: gray;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            margin-top: 25px;
        """)

        btn_volver.clicked.connect(self.volver)
        layout.addWidget(btn_volver)
        self.setLayout(layout)

    def volver(self):
        from pantalla.inicio import InicioWindow
        self.parent.setCentralWidget(InicioWindow(self.parent))
