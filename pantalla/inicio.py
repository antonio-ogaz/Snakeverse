"""
pantalla/inicio.py — Pantalla de inicio / menú principal
"""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSizePolicy, QFrame,
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

from utilidad.estilos import (
    DORADO, GRIS, VERDE,
    FONDO_OSCURO,
    estilo_boton_verde, estilo_boton_rojo,
    estilo_boton_dorado, estilo_boton_azul, estilo_boton_morado,
)
from utilidad.musica import musica


def ruta_recurso(nombre: str) -> str:
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raiz, "recursos", nombre)


class PantallaInicio(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal

        # Fondo UNIFORME en toda la pantalla
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {FONDO_OSCURO};
            }}
            QFrame {{
                background-color: {FONDO_OSCURO};
                border: none;
            }}
            QLabel {{
                background: transparent;
            }}
        """)

        musica.iniciar()
        self._construir_interfaz()

    def _construir_interfaz(self):
        # Layout principal
        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(30, 30, 30, 30)
        raiz.setSpacing(40)

        # Columna izquierda: logo
        col_logo = self._columna_logo()
        raiz.addLayout(col_logo, 50)

        # Separador vertical
        separador = QFrame()
        separador.setFrameShape(QFrame.VLine)
        separador.setStyleSheet(f"""
            background-color: {DORADO};
            max-width: 2px;
            min-width: 2px;
            margin: 50px 0;
            border: none;
        """)
        raiz.addWidget(separador, 0)

        # Columna derecha: botones
        col_botones = self._columna_botones()
        raiz.addLayout(col_botones, 50)

    def _columna_logo(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(20)
        col.setAlignment(Qt.AlignCenter)

        # Título
        lbl_title = QLabel("SNAKEVERSE")
        lbl_title.setFont(QFont("Consolas", 32, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {DORADO}; background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)
        col.addWidget(lbl_title)

        col.addStretch()

        # Logo
        self._lbl_logo = QLabel()
        self._lbl_logo.setAlignment(Qt.AlignCenter)
        self._lbl_logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._lbl_logo.setMinimumHeight(250)
        self._lbl_logo.setStyleSheet("background: transparent;")
        self._ruta_logo = ruta_recurso("logo.png")
        self._cargar_logo()
        col.addWidget(self._lbl_logo, stretch=2)

        col.addStretch()

        return col

    def _cargar_logo(self):
        """Carga el logo."""
        pixmap = QPixmap(self._ruta_logo)
        if not pixmap.isNull():
            self._pixmap_original = pixmap
            self._lbl_logo.setScaledContents(False)
        else:
            self._pixmap_original = None
            self._lbl_logo.setText("🐍")
            self._lbl_logo.setFont(QFont("Segoe UI", 80))
            self._lbl_logo.setStyleSheet(f"color: {DORADO}; background: transparent;")

    def resizeEvent(self, e):
        """Reescala el logo."""
        super().resizeEvent(e)
        if hasattr(self, '_pixmap_original') and self._pixmap_original:
            w = self._lbl_logo.width()
            h = self._lbl_logo.height()
            if w > 10 and h > 10:
                scaled = self._pixmap_original.scaled(
                    w, h,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self._lbl_logo.setPixmap(scaled)

    def _columna_botones(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(14)
        col.setAlignment(Qt.AlignVCenter)

        # Título menú
        lbl_menu = QLabel("MENÚ PRINCIPAL")
        lbl_menu.setFont(QFont("Consolas", 12, QFont.Bold))
        lbl_menu.setStyleSheet(f"color: {DORADO}; background: transparent; letter-spacing: 4px;")
        lbl_menu.setAlignment(Qt.AlignCenter)
        col.addWidget(lbl_menu)

        col.addSpacing(20)

        # Botones con sus estilos originales
        btn_jugar = QPushButton("▶   JUGAR")
        btn_ajustes = QPushButton("⚙   AJUSTES")
        btn_puntuaciones = QPushButton("⭐   PUNTUACIONES")
        btn_salir = QPushButton("✕   SALIR")
        self.btn_musica = QPushButton(
            "🔊   MÚSICA: ON" if musica.esta_activa() else "🔇   MÚSICA: OFF"
        )

        # Aplicar estilos originales
        btn_jugar.setStyleSheet(estilo_boton_verde())
        btn_ajustes.setStyleSheet(estilo_boton_morado())
        btn_puntuaciones.setStyleSheet(estilo_boton_dorado())
        btn_salir.setStyleSheet(estilo_boton_rojo())
        self.btn_musica.setStyleSheet(estilo_boton_azul())

        # Configurar tamaños como estaban originalmente
        for boton in [btn_jugar, btn_ajustes, btn_puntuaciones, btn_salir, self.btn_musica]:
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            boton.setMinimumHeight(52)
            boton.setCursor(Qt.PointingHandCursor)
            col.addWidget(boton)

        col.addStretch()

        # Versión
        lbl_version = QLabel("v1.0")
        lbl_version.setFont(QFont("Segoe UI", 9))
        lbl_version.setStyleSheet(f"color: {GRIS}; background: transparent;")
        lbl_version.setAlignment(Qt.AlignRight)
        col.addWidget(lbl_version)

        # Conexiones
        btn_jugar.clicked.connect(self._ir_configuracion)
        btn_puntuaciones.clicked.connect(self._ir_puntuaciones)
        btn_ajustes.clicked.connect(self._ir_ajustes)
        btn_salir.clicked.connect(self.ventana.close)
        self.btn_musica.clicked.connect(self._alternar_musica)

        return col

    def _ir_configuracion(self):
        from pantalla.configuracion import PantallaConfiguracion
        self.ventana.setCentralWidget(PantallaConfiguracion(self.ventana))

    def _ir_puntuaciones(self):
        from pantalla.puntuaciones import PantallaPuntuaciones
        self.ventana.setCentralWidget(PantallaPuntuaciones(self.ventana))

    def _ir_ajustes(self):
        from pantalla.ajustes import PantallaAjustes
        self.ventana.setCentralWidget(PantallaAjustes(self.ventana))

    def _alternar_musica(self):
        musica.alternar()
        if musica.esta_activa():
            self.btn_musica.setText("🔊   MÚSICA: ON")
        else:
            self.btn_musica.setText("🔇   MÚSICA: OFF")