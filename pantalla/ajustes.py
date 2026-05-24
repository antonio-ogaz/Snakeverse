"""
pantalla/ajustes.py — Pantalla de ajustes del juego
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider,
    QSpacerItem, QSizePolicy, QFrame,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utilidad.estilos import (
    DORADO, BLANCO_CALIDO, GRIS,
    VERDE, AZUL, MORADO, NARANJA, FONDO_MEDIO, BORDE_ACTIVO,
    estilo_ventana, estilo_boton_base,
)
from utilidad.musica import musica


class PantallaAjustes(QWidget):
    """
    Pantalla de ajustes con opciones de volumen,
    velocidad del juego y personalización.
    """

    def __init__(self, ventana_principal=None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal
        self.setStyleSheet(estilo_ventana())
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(0)

        # Título
        lbl_titulo = QLabel("⚙  AJUSTES")
        lbl_titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        lbl_sub = QLabel("Personaliza tu experiencia de juego")
        lbl_sub.setFont(QFont("Segoe UI", 11))
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        layout.addSpacing(24)

        layout.addWidget(self._tarjeta_audio())
        layout.addSpacing(16)
        layout.addWidget(self._tarjeta_juego())
        layout.addSpacing(16)
        layout.addWidget(self._tarjeta_personalizacion())

        layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        btn_volver = QPushButton("← VOLVER AL MENÚ")
        btn_volver.setStyleSheet(estilo_boton_base())
        btn_volver.setMinimumWidth(220)
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.clicked.connect(self._volver)
        layout.addWidget(btn_volver, 0, Qt.AlignCenter)

    def _crear_tarjeta(self, titulo_texto, color_borde) -> tuple:
        """Devuelve (frame, layout_interno)."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_borde};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)
        lbl = QLabel(titulo_texto)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet(
            f"color: {color_borde}; background: transparent; border: none;"
        )
        lay.addWidget(lbl)
        return frame, lay

    def _tarjeta_audio(self) -> QFrame:
        frame, lay = self._crear_tarjeta("🔊  AUDIO", AZUL)

        fila = QHBoxLayout()
        fila.setSpacing(10)

        lbl = QLabel("Volumen de música:")
        lbl.setFont(QFont("Segoe UI", 12))
        lbl.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        lbl.setFixedWidth(200)

        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        # Cargar el volumen actual desde el módulo de música
        self.slider_volumen.setValue(musica.obtener_volumen())
        self.slider_volumen.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: #282840; height: 6px; border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {AZUL}; width: 16px; height: 16px;
                margin: -5px 0; border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {AZUL}; border-radius: 3px;
            }}
        """)

        self.lbl_volumen = QLabel(f"{musica.obtener_volumen()}%")
        self.lbl_volumen.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_volumen.setStyleSheet(
            f"color: {AZUL}; background: transparent; border: none;"
        )
        self.lbl_volumen.setFixedWidth(40)

        # Conectar el slider para actualizar el volumen en tiempo real
        self.slider_volumen.valueChanged.connect(self._cambiar_volumen)

        fila.addWidget(lbl)
        fila.addWidget(self.slider_volumen)
        fila.addWidget(self.lbl_volumen)
        lay.addLayout(fila)

        nota = QLabel("Nota: el volumen se ajusta en tiempo real.")
        nota.setFont(QFont("Segoe UI", 9))
        nota.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )
        lay.addWidget(nota)
        return frame

    def _cambiar_volumen(self, valor: int):
        """Cambia el volumen de la música en tiempo real."""
        self.lbl_volumen.setText(f"{valor}%")
        musica.cambiar_volumen(valor)

    def _tarjeta_juego(self) -> QFrame:
        frame, lay = self._crear_tarjeta("🎮  JUEGO", VERDE)
        info = QLabel(
            "Velocidad: Normal  ·  Rondas: Mejor de 5  ·  Tiempo por ronda: 90s\n"
            "Power-ups: Activados  ·  Obstáculos progresivos: Activados"
        )
        info.setFont(QFont("Segoe UI", 12))
        info.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        info.setWordWrap(True)
        lay.addWidget(info)
        return frame

    def _tarjeta_personalizacion(self) -> QFrame:
        frame, lay = self._crear_tarjeta("🎨  PERSONALIZACIÓN", MORADO)
        info = QLabel(
            "Los colores de las serpientes se seleccionan antes de cada partida.\n"
        )
        info.setFont(QFont("Segoe UI", 12))
        info.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        info.setWordWrap(True)
        lay.addWidget(info)
        return frame

    def _volver(self):
        from pantalla.inicio import PantallaInicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))