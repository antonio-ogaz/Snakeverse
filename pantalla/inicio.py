from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt
from pantalla.puntuaciones import PuntuacionesWindow
from pantalla.configuracion import ConfiguracionWindow

class InicioWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


        layout_principal = QHBoxLayout()

        izquierda = QVBoxLayout()
        titulo = QLabel("SNAKEVERSE")
        titulo.setFont(QFont("Arial", 32, QFont.Bold))
        titulo.setStyleSheet("color: blue; margin-bottom: 20px;")
        izquierda.addWidget(titulo)

        logo = QLabel()
        pixmap = QPixmap("recursos/logo.png")
        logo.setPixmap(pixmap)
        logo.setScaledContents(True)
        logo.setFixedSize(500, 500)
        izquierda.addWidget(logo)

        izquierda.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


        derecha = QVBoxLayout()

        btn_jugar = QPushButton("[JUGAR]")
        btn_ajustes = QPushButton("[AJUSTES]")
        btn_puntuaciones = QPushButton("[PUNTUACIONES]")
        btn_salir = QPushButton("[SALIR]")


        btn_jugar.setStyleSheet("color: green; font-size: 22px; font-weight: bold; padding: 10px;")
        btn_ajustes.setStyleSheet("color: gray; font-size: 22px; font-weight: bold; padding: 10px;")
        btn_puntuaciones.setStyleSheet("color: blue; font-size: 22px; font-weight: bold; padding: 10px;")
        btn_salir.setStyleSheet("color: red; font-size: 22px; font-weight: bold; padding: 10px;")

        derecha.addWidget(btn_jugar)
        derecha.addWidget(btn_ajustes)
        derecha.addWidget(btn_puntuaciones)
        derecha.addWidget(btn_salir)

        derecha.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btn_jugar.clicked.connect(self.abrir_configuracion)
        btn_puntuaciones.clicked.connect(self.abrir_puntuaciones)
        btn_salir.clicked.connect(self.parent.close)
        btn_ajustes.clicked.connect(self.mostrar_ajustes)


        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile("recursos/musica.mp3"))
        self.player.play()

        layout_principal.addLayout(izquierda, stretch=2)
        layout_principal.addLayout(derecha, stretch=1)

        self.setLayout(layout_principal)

    def abrir_configuracion(self):
        self.parent.setCentralWidget(ConfiguracionWindow(self.parent))

    def abrir_puntuaciones(self):
        self.parent.setCentralWidget(PuntuacionesWindow())

    def mostrar_ajustes(self):
        ajustes = QLabel("Pantalla de AJUSTES")
        ajustes.setStyleSheet("font-size: 18px; color: gray;")
        self.parent.setCentralWidget(ajustes)

