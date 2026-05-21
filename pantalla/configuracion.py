from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt

class ConfiguracionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(60, 40, 60, 40)

        # ── Título ──
        titulo = QLabel("CONFIGURAR PARTIDA")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: blue; font-size: 26px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)

        # ── Campos de texto ──
        lbl_j1 = QLabel("Nombre Jugador 1:")
        self.jugador1 = QLineEdit()
        self.jugador1.setPlaceholderText("Jugador 1  —  controles: W A S D")

        lbl_j2 = QLabel("Nombre Jugador 2:")
        self.jugador2 = QLineEdit()
        self.jugador2.setPlaceholderText("Jugador 2  —  controles: ← ↑ ↓ →")

        lbl_ip = QLabel("IP del Servidor:")
        self.ip = QLineEdit()
        self.ip.setPlaceholderText("192.168.1.1")

        campos = [
            (lbl_j1, self.jugador1, "green"),
            (lbl_j2, self.jugador2, "blue"),
            (lbl_ip, self.ip,       "gray"),
        ]
        for lbl, campo, color in campos:
            lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            campo.setStyleSheet(f"""
                QLineEdit {{
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    background-color: #1f1f35;
                    border: 2px solid {color};
                    border-radius: 10px;
                }}
            """)
            layout.addWidget(lbl)
            layout.addWidget(campo)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Botones ──
        btn_volver  = QPushButton("[VOLVER AL MENÚ]")
        btn_iniciar = QPushButton("[INICIAR JUEGO]")

        botones = [
            (btn_volver,  "gray"),
            (btn_iniciar, "green"),
        ]
        for boton, color in botones:
            boton.setFixedWidth(300)
            boton.setStyleSheet(f"""
                QPushButton {{
                    color: {color};
                    font-size: 20px;
                    font-weight: bold;
                    padding: 12px;
                    background-color: #1f1f35;
                    border: 2px solid {color};
                    border-radius: 10px;
                }}
                QPushButton:hover {{ background-color: #2a2a4d; }}
            """)

        btn_volver.clicked.connect(self.volver)
        btn_iniciar.clicked.connect(self.iniciar_juego)

        row_btns = QHBoxLayout()
        row_btns.setAlignment(Qt.AlignCenter)
        row_btns.setSpacing(30)
        row_btns.addWidget(btn_volver)
        row_btns.addWidget(btn_iniciar)
        layout.addLayout(row_btns)

        self.setLayout(layout)

    def volver(self):
        from pantalla.inicio import InicioWindow
        self.parent.setCentralWidget(InicioWindow(self.parent))

    def iniciar_juego(self):
        from pantalla.juego import JuegoWindow
        j1 = self.jugador1.text().strip() or "Jugador 1"
        j2 = self.jugador2.text().strip() or "Jugador 2"
        self.parent.setCentralWidget(JuegoWindow(self.parent, nombre_j1=j1, nombre_j2=j2))
