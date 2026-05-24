"""
pantalla/resultado.py — Pantalla de resultados al final de la partida
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

from utilidad.estilos import (
    DORADO, VERDE, AZUL, GRIS, BLANCO_CALIDO,
    FONDO_OSCURO, FONDO_MEDIO,
    estilo_boton_verde, estilo_boton_rojo,
)


class PantallaResultado(QWidget):
    """
    Pantalla que muestra el resultado final de la partida:
    """

    def __init__(self, ventana_principal=None,
                 nombre_ganador: str = "",
                 victorias: list = None,
                 puntos: list = None,
                 nombres: list = None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal
        self.nombre_ganador = nombre_ganador
        self.victorias = victorias if victorias else [0, 0]
        self.puntos = puntos if puntos else [0, 0]
        self.nombres = nombres if nombres else ["Jugador 1", "Jugador 2"]

        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        # Título
        lbl_titulo = QLabel("🏆  RESULTADO FINAL  🏆")
        lbl_titulo.setFont(QFont("Segoe UI", 28, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {DORADO};")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Ganador
        lbl_ganador = QLabel(f"¡{self.nombre_ganador.upper()} ES EL CAMPEÓN!")
        lbl_ganador.setFont(QFont("Segoe UI", 20, QFont.Bold))
        lbl_ganador.setStyleSheet(f"color: {VERDE};")
        lbl_ganador.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_ganador)

        # Línea decorativa
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet(f"background-color: {DORADO}; max-height: 2px;")
        layout.addWidget(linea)

        layout.addSpacing(20)

        # Tarjeta de puntuaciones
        frame_puntuaciones = QFrame()
        frame_puntuaciones.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border-radius: 15px;
                border: 2px solid {DORADO};
            }}
        """)
        layout_punt = QVBoxLayout(frame_puntuaciones)
        layout_punt.setContentsMargins(30, 20, 30, 20)
        layout_punt.setSpacing(15)

        # Título de la tabla
        lbl_sub = QLabel("ESTADÍSTICAS DE LA PARTIDA")
        lbl_sub.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_sub.setStyleSheet(f"color: {DORADO};")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout_punt.addWidget(lbl_sub)

        # Jugador 1
        lbl_j1 = QLabel(
            f"🐍 {self.nombres[0].upper()}  →  "
            f"🏆 {self.victorias[0]} victorias  |  ⭐ {self.puntos[0]} puntos"
        )
        lbl_j1.setFont(QFont("Segoe UI", 13))
        lbl_j1.setStyleSheet(f"color: {VERDE}; padding: 8px;")
        lbl_j1.setAlignment(Qt.AlignCenter)
        layout_punt.addWidget(lbl_j1)

        # Jugador 2
        lbl_j2 = QLabel(
            f"🐍 {self.nombres[1].upper()}  →  "
            f"🏆 {self.victorias[1]} victorias  |  ⭐ {self.puntos[1]} puntos"
        )
        lbl_j2.setFont(QFont("Segoe UI", 13))
        lbl_j2.setStyleSheet(f"color: {AZUL}; padding: 8px;")
        lbl_j2.setAlignment(Qt.AlignCenter)
        layout_punt.addWidget(lbl_j2)

        # Resultado final
        resultado_texto = f"RESULTADO: {self.victorias[0]} - {self.victorias[1]}"
        lbl_resultado = QLabel(resultado_texto)
        lbl_resultado.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_resultado.setStyleSheet(f"color: {DORADO}; padding: 10px;")
        lbl_resultado.setAlignment(Qt.AlignCenter)
        layout_punt.addWidget(lbl_resultado)

        layout.addWidget(frame_puntuaciones)

        layout.addStretch()

        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(20)

        btn_menu = QPushButton("◀  VOLVER AL MENÚ")
        btn_menu.setStyleSheet(estilo_boton_rojo())
        btn_menu.setMinimumHeight(50)
        btn_menu.setMinimumWidth(200)
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.clicked.connect(self._volver_menu)

        btn_salir = QPushButton("✕  SALIR")
        btn_salir.setStyleSheet(estilo_boton_rojo())
        btn_salir.setMinimumHeight(50)
        btn_salir.setMinimumWidth(150)
        btn_salir.setCursor(Qt.PointingHandCursor)
        btn_salir.clicked.connect(self._salir)

        layout_botones.addStretch()
        layout_botones.addWidget(btn_menu)
        layout_botones.addWidget(btn_salir)
        layout_botones.addStretch()

        layout.addLayout(layout_botones)

    def _volver_menu(self):
        from pantalla.inicio import PantallaInicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))

    def _salir(self):
        self.ventana.close()