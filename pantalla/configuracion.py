"""
pantalla/configuracion.py — Configuración de partida

Incluye:
  - Nombre de cada jugador
  - Selector de color de serpiente (swatches visuales)
  - Configuración de red con modo ANFITRIÓN / CLIENTE / LOCAL
    Anfitrión: crea la sala, muestra su IP para compartir
    Cliente:   ingresa la IP del anfitrión y se conecta
"""

import socket
import threading
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton,
    QSpacerItem, QSizePolicy, QFrame, QButtonGroup,
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QTimer, Signal, QObject

from utilidad.estilos import (
    DORADO, DORADO_CLARO, VERDE, AZUL, CIAN, ROJO,
    BLANCO_CALIDO, GRIS, NARANJA, MORADO,
    FONDO_MEDIO, FONDO_OSCURO, BORDE_ACTIVO,
    estilo_ventana, estilo_input,
    estilo_boton_verde, estilo_boton_base,
    estilo_boton_azul, estilo_boton_rojo,
)
from utilidad.musica import musica

# Colores disponibles para cada jugador
COLORES_J1 = [
    ("#2ECC40", "#1A8C28"),   # verde vibrante
    ("#40FF60", "#20B040"),   # verde neón
    ("#FFD040", "#C09010"),   # dorado
    ("#80FF40", "#40B020"),   # lima
    ("#20E8A0", "#10A060"),   # turquesa
    ("#40D8FF", "#2090C0"),   # cian
    ("#C060FF", "#7020C0"),   # morado
    ("#FF9040", "#C05020"),   # naranja
]
COLORES_J2 = [
    ("#209AE8", "#1464A8"),   # azul eléctrico
    ("#40B8FF", "#1880D0"),   # azul cielo
    ("#E03060", "#A01040"),   # rojo vibrante
    ("#FF4080", "#C02060"),   # magenta
    ("#E8C020", "#A08010"),   # amarillo
    ("#FF6040", "#C03020"),   # rojo-naranja
    ("#A0A8FF", "#6068C8"),   # lavanda
    ("#4DD0E1", "#006064"),   # agua
]

PUERTO_RED = 5555


def obtener_ip_local() -> str:
    """Obtiene la IP local en la red LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class SeñalesRed(QObject):
    """Señales Qt para comunicar el hilo de red con la UI."""
    conectado    = Signal()
    error        = Signal(str)
    cliente_listo = Signal(str)   # emite la IP del cliente conectado


class PantallaConfiguracion(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__(ventana_principal)
        self.ventana      = ventana_principal
        self.color_j1     = COLORES_J1[0]
        self.color_j2     = COLORES_J2[0]
        self.modo_red     = "local"    # "local" | "anfitrion" | "cliente"
        self._socket_srv  = None       # socket servidor (modo anfitrión)
        self._señales_red = SeñalesRed()
        self._señales_red.conectado.connect(self._en_conectado)
        self._señales_red.error.connect(self._en_error_red)
        self.setStyleSheet(estilo_ventana())
        self._construir_interfaz()

    #  interfaz

    def _construir_interfaz(self):
        # Scroll area para pantallas pequeñas
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # Contenido scrollable
        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(0)

        lbl_titulo = QLabel("⚙  CONFIGURAR PARTIDA")
        lbl_titulo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        layout.addSpacing(4)

        lbl_sub = QLabel("Nombres, colores y modo de conexión")
        lbl_sub.setFont(QFont("Segoe UI", 10))
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)
        layout.addSpacing(20)

        # Jugadores
        fila_jugadores = QHBoxLayout()
        fila_jugadores.setSpacing(16)
        fila_jugadores.addWidget(self._tarjeta_jugador(1))
        fila_jugadores.addWidget(self._tarjeta_jugador(2))
        layout.addLayout(fila_jugadores)
        layout.addSpacing(16)

        #  Configuración de red
        layout.addWidget(self._tarjeta_red())
        layout.addSpacing(20)

        # Botones inferiores
        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(14)
        btn_volver  = QPushButton("← VOLVER")
        btn_iniciar = QPushButton("▶  INICIAR JUEGO")
        btn_volver.setStyleSheet(estilo_boton_base())
        btn_iniciar.setStyleSheet(estilo_boton_verde())
        btn_volver.setMinimumWidth(160)
        btn_iniciar.setMinimumWidth(200)
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_iniciar.setCursor(Qt.PointingHandCursor)
        fila_botones.addStretch()
        fila_botones.addWidget(btn_volver)
        fila_botones.addWidget(btn_iniciar)
        fila_botones.addStretch()
        layout.addLayout(fila_botones)

        btn_volver.clicked.connect(self._volver)
        btn_iniciar.clicked.connect(self._iniciar)

        layout_raiz.addWidget(contenido)

    # Tarjeta de jugador con nombre + selector de color

    def _tarjeta_jugador(self, numero: int) -> QFrame:
        es_j1       = (numero == 1)
        color_acento = VERDE if es_j1 else AZUL
        colores      = COLORES_J1 if es_j1 else COLORES_J2
        titulo       = "🟢  JUGADOR 1" if es_j1 else "🔵  JUGADOR 2"
        placeholder  = "Nombre J1" if es_j1 else "Nombre J2"
        pista        = "WASD + Q" if es_j1 else "↑↓←→ + /"

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_acento};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        # Título de la tarjeta
        lbl = QLabel(titulo)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet(
            f"color: {color_acento}; background: transparent; border: none;"
        )
        lay.addWidget(lbl)

        # Campo de nombre
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setMaxLength(20)
        campo.setStyleSheet(estilo_input())
        lay.addWidget(campo)

        lbl_controles = QLabel(f"Controles: {pista}")
        lbl_controles.setFont(QFont("Segoe UI", 9))
        lbl_controles.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )
        lay.addWidget(lbl_controles)

        #  Selector de color
        lbl_color = QLabel("Color de serpiente:")
        lbl_color.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_color.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        lay.addWidget(lbl_color)

        # Cuadrícula de swatches
        grid = QGridLayout()
        grid.setSpacing(6)
        swatches = []
        for i, (c1, c2) in enumerate(colores):
            swatch = QPushButton()
            swatch.setFixedSize(36, 36)
            swatch.setCursor(Qt.PointingHandCursor)
            swatch.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c1};
                    border-radius: 6px;
                    border: 3px solid {'#FFFFFF' if i == 0 else 'transparent'};
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                }}
            """)
            swatch.setToolTip(f"Color {i+1}")
            grid.addWidget(swatch, i // 4, i % 4)
            swatches.append(swatch)

        lay.addLayout(grid)

        # Preview del color seleccionado
        preview = QLabel()
        preview.setFixedHeight(14)
        preview.setStyleSheet(
            f"background-color: {colores[0][0]}; border-radius: 6px; border: none;"
        )
        lay.addWidget(preview)

        # Guardar referencias
        if es_j1:
            self.campo_j1   = campo
            self._sw1       = swatches
            self._prev1     = preview
        else:
            self.campo_j2   = campo
            self._sw2       = swatches
            self._prev2     = preview

        # Conectar swatches
        for i, sw in enumerate(swatches):
            sw.clicked.connect(
                lambda _, idx=i, n=numero: self._seleccionar_color(idx, n)
            )

        return frame

    def _seleccionar_color(self, idx: int, numero: int):
        """Actualiza el color seleccionado y resalta el swatch elegido."""
        colores  = COLORES_J1 if numero == 1 else COLORES_J2
        swatches = self._sw1  if numero == 1 else self._sw2
        preview  = self._prev1 if numero == 1 else self._prev2

        if numero == 1:
            self.color_j1 = colores[idx]
        else:
            self.color_j2 = colores[idx]

        for i, sw in enumerate(swatches):
            c1 = colores[i][0]
            borde = "3px solid #FFFFFF" if i == idx else "3px solid transparent"
            sw.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c1};
                    border-radius: 6px;
                    border: {borde};
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                }}
            """)

        preview.setStyleSheet(
            f"background-color: {colores[idx][0]}; border-radius: 6px; border: none;"
        )

    # Tarjeta de red

    def _tarjeta_red(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {CIAN};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        # Título
        lbl_titulo = QLabel("🌐  MODO DE CONEXIÓN")
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_titulo.setStyleSheet(
            f"color: {CIAN}; background: transparent; border: none;"
        )
        lay.addWidget(lbl_titulo)

        # Botones de modo
        fila_modo = QHBoxLayout()
        fila_modo.setSpacing(10)

        self.btn_local      = QPushButton("🌿  LOCAL")
        self.btn_anfitrion  = QPushButton("🏠  ANFITRIÓN")
        self.btn_cliente    = QPushButton("🔗  CLIENTE")

        for b in [self.btn_local, self.btn_anfitrion, self.btn_cliente]:
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(38)
            b.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.btn_local.setChecked(True)
        self._aplicar_estilo_modo()

        self.btn_local.clicked.connect(lambda: self._cambiar_modo("local"))
        self.btn_anfitrion.clicked.connect(lambda: self._cambiar_modo("anfitrion"))
        self.btn_cliente.clicked.connect(lambda: self._cambiar_modo("cliente"))

        fila_modo.addWidget(self.btn_local)
        fila_modo.addWidget(self.btn_anfitrion)
        fila_modo.addWidget(self.btn_cliente)
        lay.addLayout(fila_modo)

        # Panel dinámico (cambia según el modo)
        self._panel_red = QFrame()
        self._panel_red.setStyleSheet("background: transparent; border: none;")
        self._lay_panel_red = QVBoxLayout(self._panel_red)
        self._lay_panel_red.setContentsMargins(0, 0, 0, 0)
        self._lay_panel_red.setSpacing(8)
        lay.addWidget(self._panel_red)

        # Etiqueta de estado
        self._lbl_estado_red = QLabel("")
        self._lbl_estado_red.setFont(QFont("Segoe UI", 10))
        self._lbl_estado_red.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )
        self._lbl_estado_red.setWordWrap(True)
        lay.addWidget(self._lbl_estado_red)

        # Renderizar modo inicial
        self._renderizar_panel_red()
        return frame

    def _cambiar_modo(self, modo: str):
        """Cambia entre LOCAL / ANFITRIÓN / CLIENTE."""
        self.modo_red = modo
        self.btn_local.setChecked(modo == "local")
        self.btn_anfitrion.setChecked(modo == "anfitrion")
        self.btn_cliente.setChecked(modo == "cliente")
        self._aplicar_estilo_modo()
        self._renderizar_panel_red()
        # Cerrar servidor si se cambia de modo
        if self._socket_srv:
            try:
                self._socket_srv.close()
            except Exception:
                pass
            self._socket_srv = None

    def _aplicar_estilo_modo(self):
        """Colorea los botones según cuál está activo."""
        estilos = {
            "local":     (self.btn_local,     VERDE),
            "anfitrion": (self.btn_anfitrion, DORADO),
            "cliente":   (self.btn_cliente,   AZUL),
        }
        for modo, (boton, color) in estilos.items():
            activo = (self.modo_red == modo)
            borde  = f"2px solid {color}" if activo else f"2px solid {GRIS}"
            fondo  = f"rgba(0,0,0,0.3)" if activo else "transparent"
            boton.setStyleSheet(f"""
                QPushButton {{
                    color: {color if activo else GRIS};
                    background-color: {fondo};
                    border: {borde};
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {color};
                    border: 2px solid {color};
                }}
            """)

    def _limpiar_panel_red(self):
        """Elimina todos los widgets del panel dinámico."""
        while self._lay_panel_red.count():
            item = self._lay_panel_red.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _renderizar_panel_red(self):
        """Dibuja el contenido del panel según el modo actual."""
        self._limpiar_panel_red()
        self._lbl_estado_red.setText("")

        if self.modo_red == "local":
            info = QLabel(
                "Ambos jugadores usan el mismo teclado en esta PC.\n"
                "No se necesita red ni segunda computadora."
            )
            info.setFont(QFont("Segoe UI", 10))
            info.setStyleSheet(
                f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
            )
            info.setWordWrap(True)
            self._lay_panel_red.addWidget(info)

        elif self.modo_red == "anfitrion":
            ip_local = obtener_ip_local()
            lbl_ip = QLabel(f"📡  Tu IP:  {ip_local}   Puerto: {PUERTO_RED}")
            lbl_ip.setFont(QFont("Consolas", 13, QFont.Bold))
            lbl_ip.setStyleSheet(
                f"color: {DORADO}; background: transparent; border: none;"
            )
            self._lay_panel_red.addWidget(lbl_ip)

            lbl_inst = QLabel(
                "1. Comparte esta IP con el otro jugador.\n"
                "2. Haz clic en CREAR SALA — el juego esperará la conexión.\n"
                "3. Cuando el rival se conecte, el juego inicia automáticamente."
            )
            lbl_inst.setFont(QFont("Segoe UI", 9))
            lbl_inst.setStyleSheet(
                f"color: {GRIS}; background: transparent; border: none;"
            )
            lbl_inst.setWordWrap(True)
            self._lay_panel_red.addWidget(lbl_inst)

            self._btn_crear_sala = QPushButton("🏠  CREAR SALA Y ESPERAR")
            self._btn_crear_sala.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1E1400;
                    color: {DORADO};
                    border: 2px solid {DORADO};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: #2A1E00;
                    color: {DORADO_CLARO};
                }}
            """)
            self._btn_crear_sala.setCursor(Qt.PointingHandCursor)
            self._btn_crear_sala.clicked.connect(self._crear_sala)
            self._lay_panel_red.addWidget(self._btn_crear_sala)

        elif self.modo_red == "cliente":
            lbl_inst = QLabel(
                "Ingresa la IP del anfitrión y haz clic en UNIRSE."
            )
            lbl_inst.setFont(QFont("Segoe UI", 9))
            lbl_inst.setStyleSheet(
                f"color: {GRIS}; background: transparent; border: none;"
            )
            self._lay_panel_red.addWidget(lbl_inst)

            fila_ip = QHBoxLayout()
            fila_ip.setSpacing(10)
            lbl_ip = QLabel("IP del Anfitrión:")
            lbl_ip.setFont(QFont("Segoe UI", 11))
            lbl_ip.setStyleSheet(
                f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
            )
            lbl_ip.setFixedWidth(140)
            self._campo_ip_cliente = QLineEdit()
            self._campo_ip_cliente.setPlaceholderText("Ej: 192.168.1.5")
            self._campo_ip_cliente.setStyleSheet(estilo_input())
            fila_ip.addWidget(lbl_ip)
            fila_ip.addWidget(self._campo_ip_cliente)
            self._lay_panel_red.addLayout(fila_ip)

            self._btn_unirse = QPushButton("🔗  UNIRSE A LA SALA")
            self._btn_unirse.setStyleSheet(f"""
                QPushButton {{
                    background-color: #081420;
                    color: {AZUL};
                    border: 2px solid {AZUL};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: #0C1E30;
                    color: #40C8FF;
                }}
            """)
            self._btn_unirse.setCursor(Qt.PointingHandCursor)
            self._btn_unirse.clicked.connect(self._unirse_sala)
            self._lay_panel_red.addWidget(self._btn_unirse)

#logica de red
    def _crear_sala(self):
        """Modo ANFITRIÓN: abre servidor TCP y espera al cliente."""
        self._btn_crear_sala.setEnabled(False)
        self._lbl_estado_red.setText("⏳  Esperando que el cliente se conecte…")
        self._lbl_estado_red.setStyleSheet(
            f"color: {DORADO}; background: transparent; border: none;"
        )
        # Lanzar servidor en hilo separado para no bloquear la UI
        threading.Thread(
            target=self._hilo_servidor,
            daemon=True,
        ).start()

    def _hilo_servidor(self):
        """Hilo: escucha conexiones entrantes."""
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("", PUERTO_RED))
            srv.listen(1)
            srv.settimeout(120)
            self._socket_srv = srv
            conn, addr = srv.accept()
            conn.close()
            srv.close()
            self._socket_srv = None
            # Notificar a la UI (desde hilo → señal Qt)
            self._señales_red.conectado.emit()
        except Exception as e:
            self._señales_red.error.emit(str(e))

    def _unirse_sala(self):
        """Modo CLIENTE: conecta al servidor del anfitrión."""
        ip = getattr(self, "_campo_ip_cliente", None)
        ip_texto = ip.text().strip() if ip else ""
        if not ip_texto:
            self._lbl_estado_red.setText(" Escribe la IP del anfitrión primero.")
            self._lbl_estado_red.setStyleSheet(
                f"color: {ROJO}; background: transparent; border: none;"
            )
            return
        self._btn_unirse.setEnabled(False)
        self._lbl_estado_red.setText(f"⏳  Conectando a {ip_texto}:{PUERTO_RED}…")
        self._lbl_estado_red.setStyleSheet(
            f"color: {DORADO}; background: transparent; border: none;"
        )
        self._ip_anfitrion = ip_texto
        threading.Thread(
            target=self._hilo_cliente,
            args=(ip_texto,),
            daemon=True,
        ).start()

    def _hilo_cliente(self, ip: str):
        """Hilo: intenta conectar al servidor."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect((ip, PUERTO_RED))
            s.close()
            self._señales_red.conectado.emit()
        except Exception as e:
            self._señales_red.error.emit(str(e))

    def _en_conectado(self):
        """Llamado cuando la conexión TCP se establece (ambos modos)."""
        self._lbl_estado_red.setText("✅  ¡Conexión establecida! Iniciando juego…")
        self._lbl_estado_red.setStyleSheet(
            f"color: {VERDE}; background: transparent; border: none;"
        )
        QTimer.singleShot(800, self._iniciar)

    def _en_error_red(self, mensaje: str):
        """Muestra el error de conexión en la UI."""
        self._lbl_estado_red.setText(f"❌  Error: {mensaje}")
        self._lbl_estado_red.setStyleSheet(
            f"color: {ROJO}; background: transparent; border: none;"
        )
        # Rehabilitar botones
        btn = getattr(self, "_btn_crear_sala", None) or getattr(self, "_btn_unirse", None)
        if btn:
            btn.setEnabled(True)

    #  NAVEGACIÓN

    def _volver(self):
        musica.iniciar()
        from pantalla.inicio import PantallaInicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))

    def _iniciar(self):
        nombre_j1 = self.campo_j1.text().strip() or "Jugador 1"
        nombre_j2 = self.campo_j2.text().strip() or "Jugador 2"
        ip_red    = ""
        if self.modo_red == "cliente":
            ip_red = getattr(self, "_ip_anfitrion", "")
        from pantalla.juego import PantallaJuego
        self.ventana.setCentralWidget(
            PantallaJuego(
                self.ventana,
                nombre_j1  = nombre_j1,
                nombre_j2  = nombre_j2,
                ip_red     = ip_red,
                modo_red   = self.modo_red,
                color_j1   = self.color_j1,
                color_j2   = self.color_j2,
            )
        )