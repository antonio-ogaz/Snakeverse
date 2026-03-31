from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtGui import QFont
from pantalla.juego import JuegoWindow

class ConfiguracionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout()

        titulo = QLabel("CONFIGURAR PARTIDA")
        titulo.setFont(QFont("Arial", 26, QFont.Bold))
        titulo.setStyleSheet("color: darkblue; margin-bottom: 20px;")
        layout.addWidget(titulo)

        lbl_j1 = QLabel("Nombre Jugador 1:")
        lbl_j1.setStyleSheet("font-size: 18px;")
        self.jugador1 = QLineEdit()
        self.jugador1.setPlaceholderText("Jugador 1")
        self.jugador1.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addWidget(lbl_j1)
        layout.addWidget(self.jugador1)

        lbl_j2 = QLabel("Nombre Jugador 2:")
        lbl_j2.setStyleSheet("font-size: 18px;")
        self.jugador2 = QLineEdit()
        self.jugador2.setPlaceholderText("Jugador 2")
        self.jugador2.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addWidget(lbl_j2)
        layout.addWidget(self.jugador2)

        lbl_ip = QLabel("IP del Servidor:")
        lbl_ip.setStyleSheet("font-size: 18px;")
        self.ip = QLineEdit()
        self.ip.setPlaceholderText("192.168.1.1")
        self.ip.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addWidget(lbl_ip)
        layout.addWidget(self.ip)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btn_iniciar = QPushButton("INICIAR JUEGO")
        btn_iniciar.setStyleSheet("""
            background-color: red;
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 12px;
        """)
        btn_iniciar.clicked.connect(self.iniciar_juego)
        layout.addWidget(btn_iniciar)

        self.setLayout(layout)

    def iniciar_juego(self):
        self.parent.setCentralWidget(JuegoWindow())