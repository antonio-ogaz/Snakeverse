"""
pantalla/configuracion.py — Configuración de partida

Permite ingresar los nombres de los jugadores y la IP
del servidor para la conexión en red local.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QSpacerItem, QSizePolicy, QFrame,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utilidad.estilos import (
    DORADO, VERDE, AZUL, BLANCO_CALIDO, GRIS, FONDO_OSCURO, FONDO_MEDIO, BORDE_ACTIVO,
    estilo_ventana, estilo_titulo, estilo_etiqueta,
    estilo_boton_verde, estilo_boton_base, estilo_boton_azul, estilo_input,
)


class PantallaConfiguracion(QWidget):
    """
    Pantalla para configurar la partida antes de jugar:
    - Nombre del Jugador 1
    - Nombre del Jugador 2
    - IP del servidor (para modo red)
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

        # ── Título ────────────────────────────────────────────
        titulo = QLabel("⚙  CONFIGURAR PARTIDA")
        titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))
        titulo.setStyleSheet(estilo_titulo(DORADO, 26))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingresa los datos para iniciar la partida")
        subtitulo.setFont(QFont("Segoe UI", 11))
        subtitulo.setStyleSheet(estilo_etiqueta(GRIS, 11))
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        layout.addSpacing(30)

        # ── Tarjeta Jugador 1 ─────────────────────────────────
        layout.addWidget(self._crear_tarjeta_jugador(
            "🟢  JUGADOR 1", VERDE,
            "Nombre del Jugador 1", "campo_jugador1",
            "WASD para mover  ·  Q para usar power-up",
        ))

        layout.addSpacing(14)

        # ── Tarjeta Jugador 2 ─────────────────────────────────
        layout.addWidget(self._crear_tarjeta_jugador(
            "🔵  JUGADOR 2", AZUL,
            "Nombre del Jugador 2", "campo_jugador2",
            "↑ ↓ ← → para mover  ·  / para usar power-up",
        ))

        layout.addSpacing(14)

        # ── Tarjeta Red ───────────────────────────────────────
        layout.addWidget(self._crear_tarjeta_red())

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Botones inferiores ────────────────────────────────
        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(14)

        btn_volver = QPushButton("← VOLVER AL MENÚ")
        btn_volver.setStyleSheet(estilo_boton_base())
        btn_volver.setMinimumWidth(180)
        btn_volver.setCursor(Qt.PointingHandCursor)

        btn_iniciar = QPushButton("▶  INICIAR JUEGO")
        btn_iniciar.setStyleSheet(estilo_boton_verde())
        btn_iniciar.setMinimumWidth(220)
        btn_iniciar.setCursor(Qt.PointingHandCursor)

        fila_botones.addStretch()
        fila_botones.addWidget(btn_volver)
        fila_botones.addWidget(btn_iniciar)
        fila_botones.addStretch()
        layout.addLayout(fila_botones)

        btn_volver.clicked.connect(self._volver_al_menu)
        btn_iniciar.clicked.connect(self._iniciar_juego)

    def _crear_tarjeta_jugador(self, titulo_texto, color_acento,
                                placeholder, nombre_campo, pista):
        """Crea una tarjeta con campo de texto para un jugador."""
        tarjeta = QFrame()
        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_acento};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)

        lbl_titulo = QLabel(titulo_texto)
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {color_acento}; background: transparent; border: none;")
        lay.addWidget(lbl_titulo)

        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setMaxLength(20)
        campo.setStyleSheet(estilo_input())
        lay.addWidget(campo)

        lbl_pista = QLabel(pista)
        lbl_pista.setStyleSheet(f"color: {GRIS}; font-size: 10px; background: transparent; border: none;")
        lay.addWidget(lbl_pista)

        # Guardar referencia al campo
        setattr(self, nombre_campo, campo)
        return tarjeta

    def _crear_tarjeta_red(self) -> QFrame:
        """Crea la tarjeta de configuración de red."""
        from utilidad.estilos import CIAN
        tarjeta = QFrame()
        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {CIAN};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(8)

        lbl_titulo = QLabel("🌐  CONEXIÓN EN RED  (opcional)")
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {CIAN}; background: transparent; border: none;")
        lay.addWidget(lbl_titulo)

        fila = QHBoxLayout()
        fila.setSpacing(12)

        lbl_ip = QLabel("IP del servidor:")
        lbl_ip.setStyleSheet(f"color: {BLANCO_CALIDO}; font-size: 13px; background: transparent; border: none;")
        lbl_ip.setFixedWidth(130)

        self.campo_ip = QLineEdit()
        self.campo_ip.setPlaceholderText("192.168.1.100  (dejar vacío para modo local)")
        self.campo_ip.setStyleSheet(estilo_input())

        fila.addWidget(lbl_ip)
        fila.addWidget(self.campo_ip)
        lay.addLayout(fila)

        nota = QLabel("💡 Modo LOCAL: deja la IP vacía y ambos jugadores usan el mismo teclado.")
        nota.setStyleSheet(f"color: {GRIS}; font-size: 10px; background: transparent; border: none;")
        nota.setWordWrap(True)
        lay.addWidget(nota)

        return tarjeta

    # ── Navegación ────────────────────────────────────────────

    def _volver_al_menu(self):
        from pantalla.inicio import PantallaInicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))

    def _iniciar_juego(self):
        nombre_j1 = self.campo_jugador1.text().strip() or "Jugador 1"
        nombre_j2 = self.campo_jugador2.text().strip() or "Jugador 2"
        ip_servidor = self.campo_ip.text().strip()

        from pantalla.juego import PantallaJuego
        self.ventana.setCentralWidget(
            PantallaJuego(self.ventana, nombre_j1, nombre_j2, ip_servidor)
        )
