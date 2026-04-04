from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtGui import QFont

class AjustesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()

        titulo = QLabel("AJUSTES")
        titulo.setFont(QFont("Arial", 26, QFont.Bold))
        titulo.setStyleSheet("color: gray; margin-bottom: 20px;")
        layout.addWidget(titulo)

        placeholder = QLabel("Opciones de ajustes próximamente...")
        placeholder.setStyleSheet("font-size: 16px; color: gray;")
        layout.addWidget(placeholder)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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

        self.setLayout(layout)

    def volver(self):
        from pantalla.inicio import InicioWindow
        self.parent.setCentralWidget(InicioWindow(self.parent))