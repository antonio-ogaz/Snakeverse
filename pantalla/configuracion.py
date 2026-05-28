"""
pantalla/configuracion.py — Lobby de partida SNAKEVERSE

Flujo:
  1. Pantalla de entrada : nombre + elegir Anfitrión / Cliente
  2a. Sala Anfitrión     : muestra IP, selector de color, espera al cliente
  2b. Sala Cliente       : campo IP + conectar, luego selector de color
  3. Ambos listos        : el anfitrión pulsa "INICIAR" y arranca el juego
"""

import socket
import threading
import json
import struct
import select

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QStackedWidget, QSizePolicy,
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QTimer, Signal, QObject

from utilidad.estilos import (
    DORADO, DORADO_CLARO, VERDE, AZUL, CIAN, ROJO,
    BLANCO_CALIDO, GRIS, NARANJA, MORADO,
    FONDO_OSCURO, FONDO_MEDIO, FONDO_CLARO, BORDE, BORDE_ACTIVO,
    estilo_ventana, estilo_input,
    estilo_boton_verde, estilo_boton_base, estilo_boton_rojo,
    estilo_boton_azul,
)
from utilidad.musica import musica

# ── Paleta de colores disponibles ────────────────────────────
PALETA = [
    ("#2ECC40", "#1A8C28"),   # verde vibrante
    ("#40FF60", "#20B040"),   # verde neón
    ("#209AE8", "#1464A8"),   # azul eléctrico
    ("#40B8FF", "#1880D0"),   # azul cielo
    ("#FFD040", "#C09010"),   # dorado
    ("#E03060", "#A01040"),   # rojo vibrante
    ("#FF4080", "#C02060"),   # magenta
    ("#FF9040", "#C05020"),   # naranja
    ("#80FF40", "#40B020"),   # lima
    ("#20E8A0", "#10A060"),   # turquesa
    ("#C060FF", "#7020C0"),   # morado
    ("#4DD0E1", "#006064"),   # agua
]

PUERTO = 5555


# ── Utilidades de red ─────────────────────────────────────────
def _ip_local() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _enviar(sock, datos: dict):
    raw = json.dumps(datos).encode("utf-8")
    sock.sendall(struct.pack(">I", len(raw)) + raw)


def _recibir(sock) -> dict | None:
    try:
        hdr = _recibir_exacto(sock, 4)
        if not hdr:
            return None
        n = struct.unpack(">I", hdr)[0]
        raw = _recibir_exacto(sock, n)
        return json.loads(raw.decode("utf-8")) if raw else None
    except Exception:
        return None


def _recibir_exacto(sock, n) -> bytes | None:
    buf = b""
    while len(buf) < n:
        trozo = sock.recv(n - len(buf))
        if not trozo:
            return None
        buf += trozo
    return buf


# ── Señales Qt para comunicación hilo ↔ UI ───────────────────
class Señales(QObject):
    cliente_conectado = Signal(str)   # anfitrión: nombre del cliente
    conectado_ok      = Signal(str)   # cliente: nombre del anfitrión
    color_rival       = Signal(list)  # color actualizado del rival
    rival_listo       = Signal(bool)  # rival cambió estado listo
    iniciar_partida   = Signal(dict)  # anfitrión ordena iniciar
    error             = Signal(str)


# ── Gestor de conexión del lobby ──────────────────────────────
class LobbyRed:
    """
    Maneja el TCP del lobby antes de iniciar la partida.
    Mensajes:
      unirse   : cliente → anfitrión al conectar  {"tipo":"unirse","nombre":...,"color":...}
      bienvenida: anfitrión → cliente              {"tipo":"bienvenida","nombre":...,"color":...}
      color    : cualquiera → rival               {"tipo":"color","color":...}
      listo    : cualquiera → rival               {"tipo":"listo","valor":bool}
      iniciar  : anfitrión → cliente              {"tipo":"iniciar","config":{...}}
    """

    def __init__(self, modo: str, ip: str = ""):
        self.modo    = modo   # "anfitrion" | "cliente"
        self.ip      = ip
        self._sock   = None
        self._srv    = None
        self._activo = False
        self.señales = Señales()

    # ── Conexión ──────────────────────────────────────────────

    def escuchar(self, nombre: str, color: list):
        """Anfitrión: abre servidor y espera al cliente."""
        threading.Thread(
            target=self._hilo_anfitrion, args=(nombre, color), daemon=True
        ).start()

    def conectar(self, ip: str, nombre: str, color: list):
        """Cliente: conecta al anfitrión."""
        self.ip = ip
        threading.Thread(
            target=self._hilo_cliente, args=(nombre, color), daemon=True
        ).start()

    def _hilo_anfitrion(self, nombre: str, color: list):
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("", PUERTO))
            srv.listen(1)
            srv.settimeout(180)
            self._srv = srv
            conn, _ = srv.accept()
            srv.close(); self._srv = None
            self._sock   = conn
            self._activo = True

            # Recibir presentación del cliente
            msg = _recibir(self._sock)
            if not msg or msg.get("tipo") != "unirse":
                raise ConnectionError("Protocolo inválido")

            nombre_cliente = msg.get("nombre", "Cliente")
            color_cliente  = msg.get("color", PALETA[2])

            # Responder con los datos del anfitrión
            _enviar(self._sock, {
                "tipo":   "bienvenida",
                "nombre": nombre,
                "color":  color,
            })

            self.señales.cliente_conectado.emit(nombre_cliente)
            self.señales.color_rival.emit(color_cliente)

            # Iniciar loop de mensajes
            threading.Thread(target=self._loop_mensajes, daemon=True).start()

        except Exception as e:
            self.señales.error.emit(str(e))

    def _hilo_cliente(self, nombre: str, color: list):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect((self.ip, PUERTO))
            s.settimeout(None)
            self._sock   = s
            self._activo = True

            # Presentarse al anfitrión
            _enviar(self._sock, {
                "tipo":   "unirse",
                "nombre": nombre,
                "color":  color,
            })

            # Recibir datos del anfitrión
            msg = _recibir(self._sock)
            if not msg or msg.get("tipo") != "bienvenida":
                raise ConnectionError("Sin respuesta del anfitrión")

            nombre_anfitrion = msg.get("nombre", "Anfitrión")
            color_anfitrion  = msg.get("color", PALETA[0])

            self.señales.conectado_ok.emit(nombre_anfitrion)
            self.señales.color_rival.emit(color_anfitrion)

            # Iniciar loop de mensajes
            threading.Thread(target=self._loop_mensajes, daemon=True).start()

        except Exception as e:
            self.señales.error.emit(str(e))

    def _loop_mensajes(self):
        """Loop que escucha mensajes del rival mientras estamos en el lobby."""
        while self._activo:
            # select espera hasta 0.5 segundos para ver si hay mensajes nuevos.
            # Si no hay, permite que el ciclo avance para verificar si _activo sigue siendo True.
            listos, _, _ = select.select([self._sock], [], [], 0.5)

            if not listos:
                continue

            msg = _recibir(self._sock)
            if msg is None:
                self._activo = False
                self.señales.error.emit("Rival desconectado")
                break

            tipo = msg.get("tipo")
            if tipo == "color":
                self.señales.color_rival.emit(msg["color"])
            elif tipo == "listo":
                self.señales.rival_listo.emit(msg["valor"])
            elif tipo == "iniciar":
                self._activo = False  # Esto apagará el loop limpiamente
                self.señales.iniciar_partida.emit(msg["config"])

    # ── Envíos ────────────────────────────────────────────────

    def enviar_color(self, color: list):
        if self._activo and self._sock:
            try: _enviar(self._sock, {"tipo": "color", "color": color})
            except Exception: pass

    def enviar_listo(self, valor: bool):
        if self._activo and self._sock:
            try: _enviar(self._sock, {"tipo": "listo", "valor": valor})
            except Exception: pass

    def enviar_iniciar(self, config: dict):
        """Solo el anfitrión llama esto."""
        if self._activo and self._sock:
            try: _enviar(self._sock, {"tipo": "iniciar", "config": config})
            except Exception: pass

    def cancelar(self):
        self._activo = False
        if self._srv:
            try: self._srv.close()
            except Exception: pass
        if self._sock:
            try: self._sock.close()
            except Exception: pass


# ── Widget: selector de color ────────────────────────────────
class SelectorColor(QFrame):
    color_cambiado = Signal(list)

    def __init__(self, color_inicial: list, titulo: str, color_acento: str):
        super().__init__()
        self.color_actual = color_inicial
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_acento};
                border-radius: 10px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        lbl = QLabel(titulo)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet(f"color: {color_acento}; background: transparent; border: none;")
        lay.addWidget(lbl)

        # Preview de color
        self.preview = QFrame()
        self.preview.setFixedHeight(18)
        self.preview.setStyleSheet(
            f"background-color: {color_inicial[0]}; border-radius: 6px; border: none;"
        )
        lay.addWidget(self.preview)

        # Grid de swatches
        grid = QGridLayout()
        grid.setSpacing(6)
        self._swatches = []
        for i, (c1, c2) in enumerate(PALETA):
            btn = QPushButton()
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.PointingHandCursor)
            seleccionado = ([c1, c2] == color_inicial)
            btn.setStyleSheet(self._estilo_swatch(c1, seleccionado))
            btn.clicked.connect(lambda _, idx=i: self._seleccionar(idx))
            grid.addWidget(btn, i // 6, i % 6)
            self._swatches.append(btn)
        lay.addLayout(grid)

    def _estilo_swatch(self, c1: str, activo: bool) -> str:
        borde = "3px solid #FFFFFF" if activo else "3px solid transparent"
        return f"""
            QPushButton {{
                background-color: {c1};
                border-radius: 6px;
                border: {borde};
            }}
            QPushButton:hover {{ border: 3px solid #FFFFFF; }}
        """

    def _seleccionar(self, idx: int):
        self.color_actual = list(PALETA[idx])
        for i, btn in enumerate(self._swatches):
            btn.setStyleSheet(self._estilo_swatch(PALETA[i][0], i == idx))
        self.preview.setStyleSheet(
            f"background-color: {PALETA[idx][0]}; border-radius: 6px; border: none;"
        )
        self.color_cambiado.emit(self.color_actual)

    def set_color(self, color: list):
        """Actualiza el selector programáticamente (para mostrar el color del rival)."""
        self.color_actual = color
        try:
            idx = PALETA.index(tuple(color))
        except ValueError:
            idx = -1
        for i, btn in enumerate(self._swatches):
            btn.setStyleSheet(self._estilo_swatch(PALETA[i][0], i == idx))
        self.preview.setStyleSheet(
            f"background-color: {color[0]}; border-radius: 6px; border: none;"
        )


# ── Pantalla principal de configuración ──────────────────────
class PantallaConfiguracion(QWidget):

    def __init__(self, ventana_principal=None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal

        # Estado
        self._red          = None
        self._modo         = None      # "anfitrion" | "cliente"
        self._nombre_propio = ""
        self._nombre_rival  = ""
        self._color_propio  = list(PALETA[0])
        self._color_rival   = list(PALETA[2])
        self._listo_propio  = False
        self._listo_rival   = False

        self.setStyleSheet(estilo_ventana())
        self._construir()

    # ── Construcción ──────────────────────────────────────────

    def _construir(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._pagina_entrada())   # 0 — nombre + modo
        self._stack.addWidget(self._pagina_sala())      # 1 — lobby

        raiz.addWidget(self._stack)

    # ── Página 0: entrada ─────────────────────────────────────

    def _pagina_entrada(self) -> QWidget:
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignCenter)

        # Tarjeta central
        tarjeta = QFrame()
        tarjeta.setFixedWidth(440)
        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {DORADO};
                border-radius: 14px;
            }}
        """)
        t_lay = QVBoxLayout(tarjeta)
        t_lay.setContentsMargins(36, 32, 36, 32)
        t_lay.setSpacing(20)

        # Título
        lbl_titulo = QLabel("🐍  SNAKEVERSE")
        lbl_titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent; border: none;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        t_lay.addWidget(lbl_titulo)

        lbl_sub = QLabel("Nueva partida")
        lbl_sub.setFont(QFont("Segoe UI", 10))
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        t_lay.addWidget(lbl_sub)

        sep = self._separador(DORADO)
        t_lay.addWidget(sep)

        # Campo nombre
        lbl_n = QLabel("Tu nombre")
        lbl_n.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_n.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent; border: none;")
        t_lay.addWidget(lbl_n)

        self._campo_nombre = QLineEdit()
        self._campo_nombre.setPlaceholderText("Escribe tu nombre…")
        self._campo_nombre.setMaxLength(20)
        self._campo_nombre.setStyleSheet(estilo_input())
        self._campo_nombre.setMinimumHeight(40)
        t_lay.addWidget(self._campo_nombre)

        # Botones modo
        lbl_modo = QLabel("¿Cómo vas a jugar?")
        lbl_modo.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_modo.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent; border: none;")
        t_lay.addWidget(lbl_modo)

        fila = QHBoxLayout()
        fila.setSpacing(12)

        self._btn_anfitrion = QPushButton("🏠  ANFITRIÓN")
        self._btn_cliente   = QPushButton("🔗  CLIENTE")

        for btn in [self._btn_anfitrion, self._btn_cliente]:
            btn.setMinimumHeight(46)
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)

        self._btn_anfitrion.setStyleSheet(self._estilo_modo_btn(VERDE, False))
        self._btn_cliente.setStyleSheet(self._estilo_modo_btn(CIAN, False))

        self._btn_anfitrion.clicked.connect(lambda: self._ir_anfitrion())
        self._btn_cliente.clicked.connect(lambda: self._ir_cliente())

        fila.addWidget(self._btn_anfitrion)
        fila.addWidget(self._btn_cliente)
        t_lay.addLayout(fila)

        # Mensaje de error
        self._lbl_error_entrada = QLabel("")
        self._lbl_error_entrada.setFont(QFont("Segoe UI", 9))
        self._lbl_error_entrada.setStyleSheet(f"color: {ROJO}; background: transparent; border: none;")
        self._lbl_error_entrada.setAlignment(Qt.AlignCenter)
        t_lay.addWidget(self._lbl_error_entrada)

        # Botón volver
        btn_volver = QPushButton("← Volver al menú")
        btn_volver.setStyleSheet(estilo_boton_base())
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.clicked.connect(self._volver_menu)
        t_lay.addWidget(btn_volver)

        lay.addWidget(tarjeta, alignment=Qt.AlignCenter)
        return pagina

    # ── Página 1: sala / lobby ────────────────────────────────

    def _pagina_sala(self) -> QWidget:
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(20)

        # Título sala
        self._lbl_titulo_sala = QLabel("SALA DE ESPERA")
        self._lbl_titulo_sala.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self._lbl_titulo_sala.setStyleSheet(f"color: {DORADO}; background: transparent;")
        self._lbl_titulo_sala.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._lbl_titulo_sala)

        # Panel de conexión (IP para anfitrión / campo IP para cliente)
        self._panel_conexion = QFrame()
        self._panel_conexion.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {CIAN};
                border-radius: 10px;
            }}
        """)
        self._lay_conexion = QVBoxLayout(self._panel_conexion)
        self._lay_conexion.setContentsMargins(20, 16, 20, 16)
        self._lay_conexion.setSpacing(10)
        lay.addWidget(self._panel_conexion)

        # Fila de jugadores
        fila_jug = QHBoxLayout()
        fila_jug.setSpacing(16)

        # — Mi panel —
        self._panel_yo = QFrame()
        self._panel_yo.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {VERDE};
                border-radius: 10px;
            }}
        """)
        yo_lay = QVBoxLayout(self._panel_yo)
        yo_lay.setContentsMargins(16, 14, 16, 14)
        yo_lay.setSpacing(10)

        self._lbl_yo_titulo = QLabel("TÚ")
        self._lbl_yo_titulo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._lbl_yo_titulo.setStyleSheet(f"color: {VERDE}; background: transparent; border: none;")
        yo_lay.addWidget(self._lbl_yo_titulo)

        self._lbl_yo_nombre = QLabel("")
        self._lbl_yo_nombre.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._lbl_yo_nombre.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent; border: none;")
        yo_lay.addWidget(self._lbl_yo_nombre)

        self._selector_yo = SelectorColor(list(PALETA[0]), "Color de serpiente", VERDE)
        self._selector_yo.color_cambiado.connect(self._en_cambio_color_propio)
        yo_lay.addWidget(self._selector_yo)

        self._lbl_yo_estado = QLabel("⏳  Esperando…")
        self._lbl_yo_estado.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._lbl_yo_estado.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        self._lbl_yo_estado.setAlignment(Qt.AlignCenter)
        yo_lay.addWidget(self._lbl_yo_estado)

        self._btn_listo = QPushButton("✓  LISTO")
        self._btn_listo.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._btn_listo.setCursor(Qt.PointingHandCursor)
        self._btn_listo.setMinimumHeight(42)
        self._btn_listo.setStyleSheet(self._estilo_modo_btn(VERDE, False))
        self._btn_listo.clicked.connect(self._toggle_listo)
        yo_lay.addWidget(self._btn_listo)

        fila_jug.addWidget(self._panel_yo)

        # — Separador VS —
        vs = QLabel("VS")
        vs.setFont(QFont("Segoe UI", 18, QFont.Bold))
        vs.setStyleSheet(f"color: {DORADO}; background: transparent;")
        vs.setAlignment(Qt.AlignCenter)
        vs.setFixedWidth(40)
        fila_jug.addWidget(vs)

        # — Panel rival —
        self._panel_rival = QFrame()
        self._panel_rival.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {AZUL};
                border-radius: 10px;
            }}
        """)
        rival_lay = QVBoxLayout(self._panel_rival)
        rival_lay.setContentsMargins(16, 14, 16, 14)
        rival_lay.setSpacing(10)

        lbl_rival_titulo = QLabel("RIVAL")
        lbl_rival_titulo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_rival_titulo.setStyleSheet(f"color: {AZUL}; background: transparent; border: none;")
        rival_lay.addWidget(lbl_rival_titulo)

        self._lbl_rival_nombre = QLabel("Esperando conexión…")
        self._lbl_rival_nombre.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._lbl_rival_nombre.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        rival_lay.addWidget(self._lbl_rival_nombre)

        self._selector_rival = SelectorColor(list(PALETA[2]), "Color del rival", AZUL)
        # El rival es de solo lectura — desactivar interacción
        for sw in self._selector_rival._swatches:
            sw.setEnabled(False)
            sw.setCursor(Qt.ArrowCursor)
        rival_lay.addWidget(self._selector_rival)

        self._lbl_rival_estado = QLabel("⏳  Sin conectar")
        self._lbl_rival_estado.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._lbl_rival_estado.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        self._lbl_rival_estado.setAlignment(Qt.AlignCenter)
        rival_lay.addWidget(self._lbl_rival_estado)

        fila_jug.addWidget(self._panel_rival)
        lay.addLayout(fila_jug)

        # Botón iniciar (solo anfitrión)
        self._btn_iniciar = QPushButton("▶  INICIAR PARTIDA")
        self._btn_iniciar.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._btn_iniciar.setCursor(Qt.PointingHandCursor)
        self._btn_iniciar.setMinimumHeight(50)
        self._btn_iniciar.setStyleSheet(estilo_boton_verde())
        self._btn_iniciar.setEnabled(False)
        self._btn_iniciar.clicked.connect(self._iniciar_partida)
        lay.addWidget(self._btn_iniciar)

        # Botón cancelar
        btn_cancelar = QPushButton("✕  Cancelar y volver")
        btn_cancelar.setStyleSheet(estilo_boton_rojo())
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self._cancelar_sala)
        lay.addWidget(btn_cancelar)

        return pagina

    # ── Helpers de estilo ─────────────────────────────────────

    def _estilo_modo_btn(self, color: str, activo: bool) -> str:
        bg = f"rgba({self._hex_a_rgb(color)}, 0.15)" if activo else "transparent"
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba({self._hex_a_rgb(color)}, 0.25);
            }}
        """

    def _hex_a_rgb(self, hex_color: str) -> str:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"

    def _separador(self, color: str) -> QFrame:
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet(f"background-color: {color}; max-height: 1px; border: none;")
        return linea

    # ── Navegación: entrada → sala ────────────────────────────

    def _validar_nombre(self) -> str | None:
        nombre = self._campo_nombre.text().strip()
        if not nombre:
            self._lbl_error_entrada.setText("Escribe tu nombre para continuar.")
            return None
        self._lbl_error_entrada.setText("")
        return nombre

    def _ir_anfitrion(self):
        nombre = self._validar_nombre()
        if not nombre:
            return
        self._nombre_propio = nombre
        self._modo = "anfitrion"
        self._preparar_sala_anfitrion()
        self._stack.setCurrentIndex(1)

    def _ir_cliente(self):
        nombre = self._validar_nombre()
        if not nombre:
            return
        self._nombre_propio = nombre
        self._modo = "cliente"
        self._preparar_sala_cliente()
        self._stack.setCurrentIndex(1)

    # ── Preparación de la sala según modo ────────────────────

    def _limpiar_panel_conexion(self):
        while self._lay_conexion.count():
            item = self._lay_conexion.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _preparar_sala_anfitrion(self):
        self._limpiar_panel_conexion()
        self._lbl_titulo_sala.setText("🏠  SALA DEL ANFITRIÓN")

        # Mostrar IP
        ip = _ip_local()
        lbl_ip_hint = QLabel("Comparte esta IP con tu rival:")
        lbl_ip_hint.setFont(QFont("Segoe UI", 10))
        lbl_ip_hint.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")

        lbl_ip = QLabel(ip)
        lbl_ip.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_ip.setStyleSheet(f"color: {CIAN}; background: transparent; border: none;")
        lbl_ip.setAlignment(Qt.AlignCenter)
        lbl_ip.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._lbl_estado_conexion = QLabel("⏳  Esperando al cliente…")
        self._lbl_estado_conexion.setFont(QFont("Segoe UI", 10))
        self._lbl_estado_conexion.setStyleSheet(f"color: {DORADO}; background: transparent; border: none;")
        self._lbl_estado_conexion.setAlignment(Qt.AlignCenter)

        self._lay_conexion.addWidget(lbl_ip_hint)
        self._lay_conexion.addWidget(lbl_ip)
        self._lay_conexion.addWidget(self._lbl_estado_conexion)

        # Color inicial para anfitrión = paleta[0] (verde)
        self._color_propio = list(PALETA[0])

        # El botón iniciar solo visible para anfitrión
        self._btn_iniciar.show()

        # Actualizar panel "yo"
        self._lbl_yo_titulo.setText("TÚ  (Jugador 1)")
        self._lbl_yo_nombre.setText(self._nombre_propio)
        self._lbl_rival_nombre.setText("Esperando conexión…")
        self._lbl_rival_estado.setText("⏳  Sin conectar")
        self._lbl_yo_estado.setText("⏳  No listo")
        self._btn_listo.setEnabled(False)
        self._btn_iniciar.setEnabled(False)

        # Iniciar escucha
        self._red = LobbyRed("anfitrion")
        self._red.señales.cliente_conectado.connect(self._en_cliente_conectado)
        self._red.señales.color_rival.connect(self._en_color_rival)
        self._red.señales.rival_listo.connect(self._en_rival_listo)
        self._red.señales.error.connect(self._en_error_red)
        self._red.escuchar(self._nombre_propio, self._color_propio)

    def _preparar_sala_cliente(self):
        self._limpiar_panel_conexion()
        self._lbl_titulo_sala.setText("🔗  UNIRSE A SALA")

        lbl_hint = QLabel("IP del anfitrión:")
        lbl_hint.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_hint.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent; border: none;")

        self._campo_ip = QLineEdit()
        self._campo_ip.setPlaceholderText("192.168.1.X")
        self._campo_ip.setStyleSheet(estilo_input())
        self._campo_ip.setMinimumHeight(38)

        self._btn_conectar = QPushButton("🔗  Conectar")
        self._btn_conectar.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._btn_conectar.setCursor(Qt.PointingHandCursor)
        self._btn_conectar.setMinimumHeight(40)
        self._btn_conectar.setStyleSheet(self._estilo_modo_btn(CIAN, True))
        self._btn_conectar.clicked.connect(self._conectar_como_cliente)

        self._lbl_estado_conexion = QLabel("")
        self._lbl_estado_conexion.setFont(QFont("Segoe UI", 10))
        self._lbl_estado_conexion.setStyleSheet(f"color: {DORADO}; background: transparent; border: none;")
        self._lbl_estado_conexion.setAlignment(Qt.AlignCenter)

        self._lay_conexion.addWidget(lbl_hint)
        fila_ip = QHBoxLayout()
        fila_ip.setSpacing(10)
        fila_ip.addWidget(self._campo_ip)
        fila_ip.addWidget(self._btn_conectar)
        self._lay_conexion.addLayout(fila_ip)
        self._lay_conexion.addWidget(self._lbl_estado_conexion)

        # Color inicial para cliente = paleta[2] (azul)
        self._color_propio = list(PALETA[2])

        # El botón iniciar oculto para cliente
        self._btn_iniciar.hide()

        # Actualizar panel "yo"
        self._lbl_yo_titulo.setText("TÚ  (Jugador 2)")
        self._lbl_yo_nombre.setText(self._nombre_propio)
        self._lbl_rival_nombre.setText("Sin conectar")
        self._lbl_rival_estado.setText("⏳  Sin conectar")
        self._lbl_yo_estado.setText("⏳  No listo")
        self._btn_listo.setEnabled(False)

    # ── Acciones del lobby ────────────────────────────────────

    def _conectar_como_cliente(self):
        ip = self._campo_ip.text().strip() if hasattr(self, "_campo_ip") else ""
        if not ip:
            self._lbl_estado_conexion.setText("Escribe la IP del anfitrión.")
            self._lbl_estado_conexion.setStyleSheet(
                f"color: {ROJO}; background: transparent; border: none;"
            )
            return

        self._btn_conectar.setEnabled(False)
        self._lbl_estado_conexion.setText(f"⏳  Conectando a {ip}…")
        self._lbl_estado_conexion.setStyleSheet(
            f"color: {DORADO}; background: transparent; border: none;"
        )

        self._red = LobbyRed("cliente", ip)
        self._red.señales.conectado_ok.connect(self._en_conectado_ok)
        self._red.señales.color_rival.connect(self._en_color_rival)
        self._red.señales.rival_listo.connect(self._en_rival_listo)
        self._red.señales.iniciar_partida.connect(self._en_iniciar_partida)
        self._red.señales.error.connect(self._en_error_red)
        self._red.conectar(ip, self._nombre_propio, self._color_propio)

    def _toggle_listo(self):
        self._listo_propio = not self._listo_propio
        if self._listo_propio:
            self._btn_listo.setText("✓  LISTO  (click para cancelar)")
            self._btn_listo.setStyleSheet(self._estilo_modo_btn(VERDE, True))
            self._lbl_yo_estado.setText("✅  ¡Listo!")
            self._lbl_yo_estado.setStyleSheet(
                f"color: {VERDE}; background: transparent; border: none;"
            )
        else:
            self._btn_listo.setText("✓  LISTO")
            self._btn_listo.setStyleSheet(self._estilo_modo_btn(VERDE, False))
            self._lbl_yo_estado.setText("⏳  No listo")
            self._lbl_yo_estado.setStyleSheet(
                f"color: {GRIS}; background: transparent; border: none;"
            )
        if self._red:
            self._red.enviar_listo(self._listo_propio)
        self._actualizar_btn_iniciar()

    def _en_cambio_color_propio(self, color: list):
        self._color_propio = color
        if self._red:
            self._red.enviar_color(color)

    def _actualizar_btn_iniciar(self):
        """El botón iniciar se activa solo cuando ambos están listos (solo anfitrión)."""
        ambos_listos = self._listo_propio and self._listo_rival and bool(self._nombre_rival)
        self._btn_iniciar.setEnabled(ambos_listos)

    def _iniciar_partida(self):
        """Solo el anfitrión. Envía la config y lanza el juego."""
        if not self._red:
            return
        # Anfitrión = J1, cliente = J2
        config = {
            "nombre_j1": self._nombre_propio,
            "nombre_j2": self._nombre_rival,
            "color_j1":  self._color_propio,
            "color_j2":  self._color_rival,
            "modo_red":  "anfitrion",
        }
        self._red.enviar_iniciar(config)
        self._lanzar_juego(config)

    def _lanzar_juego(self, config: dict):
        """Navega a PantallaJuego pasando el socket ya establecido."""
        from pantalla.juego import PantallaJuego
        musica.pausar()

        # Pasar el socket del lobby al juego para reutilizarlo
        sock = self._red._sock
        ip_red = self._red.ip
        self._red._activo = False  # detener el loop del lobby sin cerrar el socket

        self.ventana.setCentralWidget(
            PantallaJuego(
                self.ventana,
                nombre_j1 = config["nombre_j1"],
                nombre_j2 = config["nombre_j2"],
                color_j1  = config["color_j1"],
                color_j2  = config["color_j2"],
                ip_red    = ip_red,
                modo_red  = config.get("modo_red", "local"),
                sock_existente = sock,
            )
        )

    # ── Slots de señales de red ───────────────────────────────

    def _en_cliente_conectado(self, nombre: str):
        """Anfitrión: el cliente se conectó."""
        self._nombre_rival = nombre
        self._lbl_rival_nombre.setText(nombre)
        self._lbl_rival_nombre.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        self._lbl_rival_estado.setText("⏳  No listo")
        self._lbl_rival_estado.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )
        self._lbl_estado_conexion.setText(f"✅  {nombre} conectado")
        self._lbl_estado_conexion.setStyleSheet(
            f"color: {VERDE}; background: transparent; border: none;"
        )
        self._btn_listo.setEnabled(True)
        self._actualizar_btn_iniciar()

    def _en_conectado_ok(self, nombre_anfitrion: str):
        """Cliente: conexión exitosa al anfitrión."""
        self._nombre_rival = nombre_anfitrion
        self._lbl_rival_nombre.setText(nombre_anfitrion)
        self._lbl_rival_nombre.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )
        self._lbl_rival_estado.setText("⏳  No listo")
        self._lbl_estado_conexion.setText(f"✅  Conectado a {nombre_anfitrion}")
        self._lbl_estado_conexion.setStyleSheet(
            f"color: {VERDE}; background: transparent; border: none;"
        )
        self._btn_listo.setEnabled(True)

    def _en_color_rival(self, color: list):
        self._color_rival = color
        self._selector_rival.set_color(color)

    def _en_rival_listo(self, valor: bool):
        self._listo_rival = valor
        if valor:
            self._lbl_rival_estado.setText("✅  ¡Listo!")
            self._lbl_rival_estado.setStyleSheet(
                f"color: {VERDE}; background: transparent; border: none;"
            )
        else:
            self._lbl_rival_estado.setText("⏳  No listo")
            self._lbl_rival_estado.setStyleSheet(
                f"color: {GRIS}; background: transparent; border: none;"
            )
        self._actualizar_btn_iniciar()

    def _en_iniciar_partida(self, config: dict):
        """Cliente recibe la orden de iniciar del anfitrión."""
        config["modo_red"] = "cliente"
        self._lanzar_juego(config)

    def _en_error_red(self, mensaje: str):
        if hasattr(self, "_lbl_estado_conexion"):
            self._lbl_estado_conexion.setText(f"❌  {mensaje}")
            self._lbl_estado_conexion.setStyleSheet(
                f"color: {ROJO}; background: transparent; border: none;"
            )
        if hasattr(self, "_btn_conectar"):
            self._btn_conectar.setEnabled(True)

    # ── Cancelar / volver ─────────────────────────────────────

    def _cancelar_sala(self):
        if self._red:
            self._red.cancelar()
            self._red = None
        self._listo_propio = False
        self._listo_rival  = False
        self._nombre_rival = ""
        self._stack.setCurrentIndex(0)

    def _volver_menu(self):
        from pantalla.inicio import PantallaInicio
        musica.iniciar()
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))