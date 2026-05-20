from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt
from pantalla.puntuaciones import PuntuacionesWindow
from pantalla.configuracion import ConfiguracionWindow

class InicioWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setStyleSheet(""" background-color: black; """)

        layout_principal = QHBoxLayout()
        layout_principal.setSpacing(50)

        layout_logo = QVBoxLayout()
        layout_menu = QVBoxLayout()

        layout_logo.setAlignment(Qt.AlignCenter)
        layout_menu.setAlignment(Qt.AlignCenter)
        layout_menu.setSpacing(20)

        logo = QLabel()
        pixmap = QPixmap("recursos/logo.png")

        logo.setPixmap(
            pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        logo.setAlignment(Qt.AlignCenter)

        btn_jugar = QPushButton("[JUGAR]")
        btn_ajustes = QPushButton("[AJUSTES]")
        btn_puntuaciones = QPushButton("[PUNTUACIONES]")
        btn_salir = QPushButton("[SALIR]")

        botones = [
            (btn_jugar, "green"),
            (btn_ajustes, "gray"),
            (btn_puntuaciones, "blue"),
            (btn_salir, "red")
        ]

        for boton, color in botones:

            boton.setFixedWidth(300)

            boton.setStyleSheet(f"""
                QPushButton {{
                    color: {color};
                    font-size: 22px;
                    font-weight: bold;
                    padding: 12px;
                    background-color: #1f1f35;
                    border: 2px solid {color};
                    border-radius: 10px;
                }}

                QPushButton:hover {{
                    background-color: #2a2a4d;
                }}
            """)

        layout_logo.addWidget(logo)

        layout_menu.addWidget(btn_jugar)
        layout_menu.addWidget(btn_ajustes)
        layout_menu.addWidget(btn_puntuaciones)
        layout_menu.addWidget(btn_salir)

        layout_principal.addLayout(layout_logo)
        layout_principal.addLayout(layout_menu)

        btn_jugar.clicked.connect(self.abrir_configuracion)
        btn_puntuaciones.clicked.connect(self.abrir_puntuaciones)
        btn_salir.clicked.connect(self.parent.close)
        btn_ajustes.clicked.connect(self.mostrar_ajustes)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(
            QUrl.fromLocalFile("recursos/sonido.mp3"))
        self.player.play()
        self.setLayout(layout_principal)

    def abrir_configuracion(self):
        self.parent.setCentralWidget(ConfiguracionWindow(self.parent))

    def abrir_puntuaciones(self):
        self.parent.setCentralWidget(PuntuacionesWindow())

    def mostrar_ajustes(self):
        ajustes = QLabel("Pantalla de AJUSTES")
        ajustes.setStyleSheet("""font-size: 18px; color: gray; """)
        ajustes.setAlignment(Qt.AlignCenter)
        self.parent.setCentralWidget(ajustes)
