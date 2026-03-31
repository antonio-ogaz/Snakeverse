from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class JuegoWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        titulo = QLabel("SNAKEVERSE")
        titulo.setFont(QFont("Arial", 28, QFont.Bold))
        titulo.setStyleSheet("color: darkblue; margin-bottom: 15px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        marcador = QLabel("Tiempo: 1:30    Ronda: 1/3")
        marcador.setFont(QFont("Arial", 20, QFont.Bold))
        marcador.setStyleSheet("color: black; background-color: lightgray; padding: 8px;")
        marcador.setAlignment(Qt.AlignCenter)
        layout.addWidget(marcador)

        puntajes = QLabel("P1: 400    P2: 350")
        puntajes.setFont(QFont("Arial", 18, QFont.Bold))
        puntajes.setStyleSheet("color: green; background-color: #f0f0f0; padding: 6px;")
        puntajes.setAlignment(Qt.AlignCenter)
        layout.addWidget(puntajes)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)

        mapa = QLabel("Aqui se mostraran las serpientes, el mapa, los power-ups y los obstaculos.")
        mapa.setFont(QFont("Arial", 16))
        mapa.setStyleSheet("color: gray; margin-top: 20px;")
        mapa.setAlignment(Qt.AlignCenter)
        layout.addWidget(mapa)

        self.setLayout(layout)