from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QSlider QCheckBox)

from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class AjustesWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent

        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()

        titulo = QLabel("AJUSTES")
        titulo.setFont(QFont("Arial", 26, QFont.Bold))
        titulo.setStyleSheet("color: gray; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)

        layout.addWidget(titulo)

        placeholder = QLabel("Opciones de ajustes próximamente...")
        placeholder.setStyleSheet("font-size: 16px; color: gray;")
        placeholder.setAlignment(Qt.AlignCenter)

        layout.addWidget(placeholder)
        
        lbl_volumen = QLabel("VOLUMEN")
        lbl_volumen.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
        """)

        layout.addWidget(lbl_volumen)

        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setMinimum(0)
        self.slider_volumen.setMaximum(100)
        self.slider_volumen.setValue(50)

        self.slider_volumen.setStyleSheet("""
            QSlider::groove:horizontal {
                background: gray;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: green;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        layout.addWidget(self.slider_volumen)

       
        self.check_musica = QCheckBox("Activar música")
        self.check_musica.setChecked(True)
        self.check_musica.setStyleSheet("""
            color: white;
            font-size: 16px;
            padding: 10px;
        """)

        layout.addWidget(self.check_musica)

        self.check_efectos = QCheckBox("Activar efectos de sonido")
        self.check_efectos.setChecked(True)
        self.check_efectos.setStyleSheet("""
            color: white;
            font-size: 16px;
            padding: 10px;
        """)

        layout.addWidget(self.check_efectos)

        lbl_velocidad = QLabel("VELOCIDAD DEL JUEGO")
        lbl_velocidad.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
        """)

        layout.addWidget(lbl_velocidad)

        self.slider_velocidad = QSlider(Qt.Horizontal)
        self.slider_velocidad.setMinimum(1)
        self.slider_velocidad.setMaximum(10)
        self.slider_velocidad.setValue(5)
        self.slider_velocidad.setStyleSheet("""
            QSlider::groove:horizontal {
                background: gray;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: blue;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        layout.addWidget(self.slider_velocidad)
        layout.addSpacerItem(
            QSpacerItem(
                20,
                40,
                QSizePolicy.Minimum,
                QSizePolicy.Expanding
            )
        )

        btn_guardar = QPushButton("GUARDAR AJUSTES")
        btn_guardar.setStyleSheet("""
            background-color: green;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
        """)

        btn_guardar.clicked.connect(self.guardar_ajustes)
        layout.addWidget(btn_guardar)
        btn_volver = QPushButton("VOLVER AL MENÚ")
        btn_volver.setStyleSheet("""
            background-color: gray;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        btn_volver.clicked.connect(self.volver)

        layout.addWidget(btn_volver)
        self.mensaje = QLabel("")

        self.mensaje.setAlignment(Qt.AlignCenter)

        self.mensaje.setStyleSheet("""
            color: green;
            font-size: 16px;
            margin-top: 10px;
        """)
        layout.addWidget(self.mensaje)
        self.setLayout(layout)

    def guardar_ajustes(self):
        volumen = self.slider_volumen.value()
        velocidad = self.slider_velocidad.value()

        musica = self.check_musica.isChecked()
        efectos = self.check_efectos.isChecked()

        self.mensaje.setText(
            f"Ajustes guardados | "
            f"Volumen: {volumen} | "
            f"Velocidad: {velocidad}"
        )

    def volver(self):
        from pantalla.inicio import InicioWindow
        self.parent.setCentralWidget(
            InicioWindow(self.parent)
        )
