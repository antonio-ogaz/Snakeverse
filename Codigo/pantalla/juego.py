"""
pantalla/juego.py — Pantalla principal del juego SNAKEVERSE

Contiene toda la lógica del juego:
  - Clase Serpiente: movimiento, colisiones, power-ups
  - Clase EstadoJuego: mapa, rondas, spawns
  - ConexionRed: sincronización anfitrión/cliente por TCP
  - CanvasJuego: dibuja todo con QPainter
  - PantallaJuego: HUD + canvas + teclado
"""

import random
import json
import os
import socket
import threading
import struct
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy,
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QBrush, QPen,
    QLinearGradient, QRadialGradient,
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Signal, QObject

from utilidad.musica import musica
from utilidad.rutas import ruta_datos
from utilidad.estilos import (
    DORADO, DORADO_CLARO, VERDE, VERDE_OSCURO,
    AZUL, AZUL_OSCURO, ROJO, NARANJA, MORADO,
    BLANCO_CALIDO, GRIS,
    FONDO_OSCURO, FONDO_MEDIO, BORDE_ACTIVO,
    estilo_ventana,
)

# ── CONSTANTES ────────────────────────────────────────────────
COLUMNAS     = 28
FILAS        = 20
RONDAS_MAX   = 3
TIEMPO_RONDA = 90
VELOCIDAD    = 135
COMIDAS      = 4
PUERTO_RED   = 5555

PU_CAMUFLAJE   = "camuflaje"
PU_TURBO       = "turbo"
PU_ESCUDO      = "escudo"
PU_CORTE       = "corte"
LISTA_POWERUPS = [PU_CAMUFLAJE, PU_TURBO, PU_ESCUDO, PU_CORTE]

PU_ICONO    = {PU_CAMUFLAJE: "👁", PU_TURBO: "⚡", PU_ESCUDO: "🛡", PU_CORTE: "✂"}
PU_NOMBRE   = {PU_CAMUFLAJE: "Camuflaje", PU_TURBO: "Turbo", PU_ESCUDO: "Escudo", PU_CORTE: "Corte"}
PU_DURACION = {PU_CAMUFLAJE: 28, PU_TURBO: 22, PU_ESCUDO: 16, PU_CORTE: 0}
PU_COLOR    = {
    PU_CAMUFLAJE: QColor("#9060FF"),
    PU_TURBO:     QColor("#FFD040"),
    PU_ESCUDO:    QColor("#40C0FF"),
    PU_CORTE:     QColor("#FF6060"),
}

COLORES_J1 = [("#2ECC40", "#1A8C28"), ("#40FF60", "#20B040"), ("#FFD040", "#C09010"), ("#80FF40", "#40B020")]
COLORES_J2 = [("#209AE8", "#1464A8"), ("#40B8FF", "#1880D0"), ("#E03060", "#A01040"), ("#E8C020", "#A08010")]


# ── CLASE SERPIENTE ───────────────────────────────────────────
class Serpiente:
    def __init__(self, col_inicio, fila_inicio, direccion, colores, nombre):
        self.cuerpo = [
            (col_inicio - direccion[0] * i, fila_inicio - direccion[1] * i)
            for i in range(4)
        ]
        self.direccion       = direccion
        self.dir_siguiente   = direccion
        self.color_cabeza    = QColor(colores[0])
        self.color_cuerpo    = QColor(colores[1])
        self.nombre          = nombre
        self.viva            = True
        self.puntos          = 0
        self.pu_guardado     = None
        self.pu_activo       = None
        self.pu_ticks        = 0
        self.invisible       = False
        self.escudado        = False
        self.turbo           = False
        self.invertida       = False
        self.ticks_invertida = 0

    def cabeza(self):
        return self.cuerpo[0]

    def cambiar_direccion(self, dcol, dfila):
        if self.invertida:
            dcol, dfila = -dcol, -dfila
        if (dcol, dfila) != (-self.direccion[0], -self.direccion[1]):
            self.dir_siguiente = (dcol, dfila)

    def avanzar(self, crecer=False):
        self.direccion = self.dir_siguiente
        col, fila = self.cuerpo[0]
        self.cuerpo.insert(0, (col + self.direccion[0], fila + self.direccion[1]))
        if not crecer:
            self.cuerpo.pop()

    def sacar_powerup(self):
        if self.pu_guardado:
            tipo = self.pu_guardado
            self.pu_guardado = None
            return tipo
        return None

    def activar_powerup(self, tipo, rival):
        if tipo == PU_CAMUFLAJE:
            self.pu_activo = tipo; self.pu_ticks = PU_DURACION[tipo]; self.invisible = True
        elif tipo == PU_TURBO:
            self.pu_activo = tipo; self.pu_ticks = PU_DURACION[tipo]; self.turbo = True
        elif tipo == PU_ESCUDO:
            self.pu_activo = tipo; self.pu_ticks = PU_DURACION[tipo]; self.escudado = True
        elif tipo == PU_CORTE:
            if len(rival.cuerpo) > 5:
                corte = max(2, len(rival.cuerpo) // 3)
                rival.cuerpo = rival.cuerpo[:-corte]

    def actualizar_efectos(self):
        if self.ticks_invertida > 0:
            self.ticks_invertida -= 1
            if self.ticks_invertida == 0:
                self.invertida = False
        if self.pu_activo is not None and PU_DURACION.get(self.pu_activo, 0) > 0:
            self.pu_ticks -= 1
            if self.pu_ticks <= 0:
                self._desactivar_powerup()

    def _desactivar_powerup(self):
        if self.pu_activo == PU_CAMUFLAJE:  self.invisible = False
        elif self.pu_activo == PU_TURBO:    self.turbo = False
        elif self.pu_activo == PU_ESCUDO:   self.escudado = False
        self.pu_activo = None
        self.pu_ticks  = 0

    def serializar(self):
        return {
            "cuerpo": self.cuerpo, "direccion": list(self.direccion),
            "dir_siguiente": list(self.dir_siguiente), "viva": self.viva,
            "puntos": self.puntos, "nombre": self.nombre,
            "pu_guardado": self.pu_guardado, "pu_activo": self.pu_activo,
            "pu_ticks": self.pu_ticks, "invisible": self.invisible,
            "escudado": self.escudado, "turbo": self.turbo,
            "invertida": self.invertida, "ticks_invertida": self.ticks_invertida,
        }

    def cargar_desde_dict(self, d):
        self.cuerpo          = [tuple(p) for p in d["cuerpo"]]
        self.direccion       = tuple(d["direccion"])
        self.dir_siguiente   = tuple(d["dir_siguiente"])
        self.viva            = d["viva"]
        self.puntos          = d["puntos"]
        self.nombre          = d["nombre"]
        self.pu_guardado     = d["pu_guardado"]
        self.pu_activo       = d["pu_activo"]
        self.pu_ticks        = d["pu_ticks"]
        self.invisible       = d["invisible"]
        self.escudado        = d["escudado"]
        self.turbo           = d["turbo"]
        self.invertida       = d["invertida"]
        self.ticks_invertida = d["ticks_invertida"]


# ── ESTADO DEL JUEGO ──────────────────────────────────────────
class EstadoJuego:
    def __init__(self, colores_j1, colores_j2, nombres):
        self.colores_j1   = colores_j1
        self.colores_j2   = colores_j2
        self.nombres      = nombres
        self.victorias    = [0, 0]
        self.numero_ronda = 1
        self._reiniciar_ronda()

    def _reiniciar_ronda(self):
        fc = FILAS // 2
        self.serpientes = [
            Serpiente(6,            fc, (1, 0),  self.colores_j1, self.nombres[0]),
            Serpiente(COLUMNAS - 7, fc, (-1, 0), self.colores_j2, self.nombres[1]),
        ]
        self.comidas  = []
        self.venenos  = []
        self.powerups = []
        self.muros    = []
        self.tiempo   = TIEMPO_RONDA
        self.ticks    = 0
        self._generar_comidas(COMIDAS)
        self._generar_venenos(1)
        self._generar_muros(max(0, self.numero_ronda - 1) * 3)
        self._generar_powerups(2)

    def _celdas_ocupadas(self):
        ocupadas = set()
        for s in self.serpientes:
            ocupadas.update(s.cuerpo)
        ocupadas.update(self.comidas)
        ocupadas.update(self.venenos)
        ocupadas.update((c, f) for c, f, _ in self.powerups)
        ocupadas.update(self.muros)
        return ocupadas

    def _celda_libre(self):
        ocupadas = self._celdas_ocupadas()
        for _ in range(600):
            col  = random.randint(2, COLUMNAS - 3)
            fila = random.randint(2, FILAS - 3)
            if (col, fila) not in ocupadas:
                return (col, fila)
        return None

    def _generar_comidas(self, n):
        for _ in range(n):
            c = self._celda_libre()
            if c: self.comidas.append(c)

    def _generar_venenos(self, n):
        for _ in range(n):
            c = self._celda_libre()
            if c: self.venenos.append(c)

    def _generar_muros(self, n):
        for _ in range(n):
            c = self._celda_libre()
            if c: self.muros.append(c)

    def _generar_powerups(self, n=1):
        for _ in range(n):
            c = self._celda_libre()
            if c: self.powerups.append((c[0], c[1], random.choice(LISTA_POWERUPS)))

    def _spawn_aleatorio(self):
        if len(self.powerups) < 2 and random.random() < 0.30:
            self._generar_powerups(1)
        elif len(self.powerups) < 3 and random.random() < 0.03:
            self._generar_powerups(1)
        if len(self.comidas) < COMIDAS and random.random() < 0.25:
            self._generar_comidas(1)
        limite = (self.numero_ronda - 1) * 3 + self.ticks // 180
        if len(self.muros) < limite and random.random() < 0.02:
            c = self._celda_libre()
            if c: self.muros.append(c)

    def tick(self):
        self.ticks += 1
        self._spawn_aleatorio()
        for idx in range(2):
            if self.serpientes[idx].viva:
                self._mover(idx)
        for idx in range(2):
            if self.serpientes[idx].viva and self.serpientes[idx].turbo:
                self._mover_turbo(idx)
        for s in self.serpientes:
            s.actualizar_efectos()
        if self.ticks % 10 == 0:
            self.tiempo = max(0, self.tiempo - 1)
        return self._revisar_fin_ronda()

    def _mover(self, idx):
        s = self.serpientes[idx]
        r = self.serpientes[1 - idx]
        s.avanzar()
        col, fila = s.cabeza()
        fuera = not (0 <= col < COLUMNAS and 0 <= fila < FILAS)
        if fuera:
            if s.escudado:
                col = col % COLUMNAS; fila = fila % FILAS
                s.cuerpo[0] = (col, fila); s.escudado = False; s.pu_activo = None
            else:
                s.viva = False; return
        if (col, fila) in self.muros:
            if s.escudado:
                s.cuerpo.pop(0); s.escudado = False; s.pu_activo = None
            else:
                s.viva = False; return
        if (col, fila) in s.cuerpo[1:]:
            if s.escudado:
                s.cuerpo.pop(0); s.escudado = False; s.pu_activo = None
            else:
                s.viva = False; return
        if (col, fila) in r.cuerpo:
            if s.escudado:
                s.cuerpo.pop(0); s.escudado = False; s.pu_activo = None
            else:
                s.viva = False; return
        self._procesar_celda(s, col, fila)

    def _mover_turbo(self, idx):
        s = self.serpientes[idx]
        r = self.serpientes[1 - idx]
        s.avanzar()
        col, fila = s.cabeza()
        choca = (
            not (0 <= col < COLUMNAS and 0 <= fila < FILAS)
            or (col, fila) in self.muros
            or (col, fila) in s.cuerpo[1:]
            or (col, fila) in r.cuerpo
        )
        if choca:
            s.cuerpo.pop(0); return
        self._procesar_celda(s, col, fila)

    def _procesar_celda(self, s, col, fila):
        if (col, fila) in self.comidas:
            self.comidas.remove((col, fila))
            s.cuerpo.append(s.cuerpo[-1])
            s.puntos += 10
        if (col, fila) in self.venenos:
            self.venenos.remove((col, fila))
            s.invertida = True; s.ticks_invertida = 30
            self._generar_venenos(1)
        for pu in self.powerups[:]:
            if (col, fila) == (pu[0], pu[1]):
                self.powerups.remove(pu)
                if s.pu_guardado is None:
                    s.pu_guardado = pu[2]
                break

    def usar_powerup(self, idx):
        s = self.serpientes[idx]
        r = self.serpientes[1 - idx]
        tipo = s.sacar_powerup()
        if tipo:
            s.activar_powerup(tipo, r)
            return True
        return False

    def _revisar_fin_ronda(self):
        j0, j1 = self.serpientes
        if not j0.viva and not j1.viva:
            return 0 if len(j0.cuerpo) >= len(j1.cuerpo) else 1
        if not j0.viva: return 1
        if not j1.viva: return 0
        if self.tiempo <= 0:
            if len(j0.cuerpo) > len(j1.cuerpo): return 0
            if len(j1.cuerpo) > len(j0.cuerpo): return 1
            return -1
        return None

    def siguiente_ronda(self):
        self.numero_ronda += 1
        self.tiempo = TIEMPO_RONDA
        self._reiniciar_ronda()

    def serializar(self, resultado=None):
        return {
            "tipo":      "estado",
            "victorias": self.victorias,
            "ronda":     self.numero_ronda,
            "tiempo":    self.tiempo,
            "ticks":     self.ticks,
            "comidas":   self.comidas,
            "venenos":   self.venenos,
            "powerups":  self.powerups,
            "muros":     self.muros,
            "nombres":   self.nombres,
            "j1":        self.serpientes[0].serializar(),
            "j2":        self.serpientes[1].serializar(),
            "resultado": resultado,
        }

    def cargar_desde_red(self, datos):
        self.victorias    = datos["victorias"]
        self.numero_ronda = datos["ronda"]
        self.tiempo       = datos["tiempo"]
        self.ticks        = datos["ticks"]
        self.comidas      = [tuple(c) for c in datos["comidas"]]
        self.venenos      = [tuple(v) for v in datos["venenos"]]
        self.powerups     = [(p[0], p[1], p[2]) for p in datos["powerups"]]
        self.muros        = [tuple(m) for m in datos["muros"]]
        # Sincronizar nombres desde el anfitrión (incluye el nombre del cliente)
        if "nombres" in datos:
            self.nombres = datos["nombres"]
        self.serpientes[0].cargar_desde_dict(datos["j1"])
        self.serpientes[1].cargar_desde_dict(datos["j2"])


# ── CONEXIÓN DE RED ───────────────────────────────────────────
def _enviar_mensaje(sock, datos: dict):
    raw = json.dumps(datos).encode("utf-8")
    sock.sendall(struct.pack(">I", len(raw)) + raw)

def _recibir_mensaje(sock):
    try:
        header = _recibir_exacto(sock, 4)
        if not header:
            return None
        longitud = struct.unpack(">I", header)[0]
        raw = _recibir_exacto(sock, longitud)
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

def _recibir_exacto(sock, n):
    datos = b""
    while len(datos) < n:
        trozo = sock.recv(n - len(datos))
        if not trozo:
            return None
        datos += trozo
    return datos


class SeñalesRed(QObject):
    estado_recibido = Signal(dict)  # cliente recibe estado del host
    tecla_recibida  = Signal(str)   # host recibe tecla del cliente
    nombre_recibido = Signal(str)   # host recibe nombre del cliente
    desconectado    = Signal()


class ConexionRed:
    def __init__(self, modo, ip_anfitrion="", nombre_cliente="Jugador 2"):
        self.modo           = modo
        self.ip_anfitrion   = ip_anfitrion
        self.nombre_cliente = nombre_cliente
        self._sock          = None
        self._activo        = False
        self.señales        = SeñalesRed()

    def conectar(self):
        # Siempre crear nueva conexión TCP
        threading.Thread(target=self._hilo_conectar, daemon=True).start()

    def _hilo_conectar(self):
        try:
            if self.modo == "anfitrion":
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv.bind(("", PUERTO_RED))
                srv.listen(1)
                srv.settimeout(120)
                print("[JUEGO] Anfitrión esperando cliente en puerto", PUERTO_RED)
                conn, _ = srv.accept()
                srv.close()
                self._sock = conn
                self._activo = True
                print("[JUEGO] Cliente conectado al juego")
                threading.Thread(target=self._hilo_recibir_teclas, daemon=True).start()
            else:
                print("[JUEGO] Cliente conectando a", self.ip_anfitrion)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(15)
                s.connect((self.ip_anfitrion, PUERTO_RED))
                s.settimeout(None)
                self._sock = s
                self._activo = True
                print("[JUEGO] Cliente conectado exitosamente")
                # Enviar nombre propio al anfitrión
                _enviar_mensaje(self._sock, {
                    "tipo": "nombre",
                    "nombre": self.nombre_cliente,
                })
                threading.Thread(target=self._hilo_recibir_estado, daemon=True).start()
        except Exception as e:
            print("[JUEGO] Error de conexión:", str(e))
            self.señales.desconectado.emit()

    def enviar_estado(self, datos):
        if self._activo and self._sock:
            try:
                _enviar_mensaje(self._sock, datos)
            except Exception:
                self._activo = False
                self.señales.desconectado.emit()

    def enviar_tecla(self, codigo):
        if self._activo and self._sock:
            try:
                _enviar_mensaje(self._sock, {"tipo": "tecla", "codigo": codigo})
            except Exception:
                self._activo = False
                self.señales.desconectado.emit()

    def _hilo_recibir_teclas(self):
        """Loop en el anfitrión: lee teclas y nombre enviados por el cliente."""
        while self._activo:
            msg = _recibir_mensaje(self._sock)
            if msg is None:
                self._activo = False
                self.señales.desconectado.emit()
                break
            tipo = msg.get("tipo")
            if tipo == "tecla":
                self.señales.tecla_recibida.emit(msg["codigo"])
            elif tipo == "nombre":
                self.señales.nombre_recibido.emit(msg["nombre"])

    def _hilo_recibir_estado(self):
        """Loop en el cliente: lee estados enviados por el anfitrión."""
        while self._activo:
            msg = _recibir_mensaje(self._sock)
            if msg is None:
                self._activo = False
                self.señales.desconectado.emit()
                break
            # ACEPTAR todos los tipos de mensaje, no solo "estado"
            tipo = msg.get("tipo")
            if tipo in ("estado", "overlay", "fin_partida"):
                self.señales.estado_recibido.emit(msg)

    def cerrar(self):
        self._activo = False
        if self._sock:
            try: self._sock.close()
            except Exception: pass


# ── CANVAS DE JUEGO ───────────────────────────────────────────
class CanvasJuego(QWidget):
    def __init__(self):
        super().__init__()
        self.estado = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(280, 200)
        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")
        self.setFocusPolicy(Qt.StrongFocus)

    def asignar_estado(self, estado):
        self.estado = estado
        self.update()

    def tamaño_celda(self):
        return min(self.width() / COLUMNAS, self.height() / FILAS)

    def desplazamiento(self, celda):
        return (self.width() - celda * COLUMNAS) / 2, (self.height() - celda * FILAS) / 2

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        celda = self.tamaño_celda()
        ox, oy = self.desplazamiento(celda)
        self._dibujar_fondo(p, celda, ox, oy)
        if not self.estado:
            return
        e = self.estado
        for col, fila in e.muros:
            self._dibujar_muro(p, col, fila, celda, ox, oy)
        p.setRenderHint(QPainter.Antialiasing, True)
        for col, fila in e.comidas:
            self._dibujar_comida(p, col, fila, celda, ox, oy)
        for col, fila in e.venenos:
            self._dibujar_veneno(p, col, fila, celda, ox, oy)
        for col, fila, tipo in e.powerups:
            self._dibujar_powerup(p, col, fila, tipo, celda, ox, oy)
        for s in e.serpientes:
            if s.viva:
                self._dibujar_serpiente(p, s, celda, ox, oy)

    def _rect_celda(self, col, fila, celda, ox, oy, m=0.06):
        mg = celda * m
        return QRectF(ox + col*celda + mg, oy + fila*celda + mg, celda - mg*2, celda - mg*2)

    def _centro_celda(self, col, fila, celda, ox, oy):
        return QPointF(ox + col*celda + celda/2, oy + fila*celda + celda/2)

    def _dibujar_fondo(self, p, celda, ox, oy):
        p.fillRect(self.rect(), QColor("#0A0A0A"))
        p.fillRect(QRectF(ox, oy, celda*COLUMNAS, celda*FILAS), QColor("#0D0D0D"))
        lapiz = QPen(QColor(30, 25, 5, 30)); lapiz.setWidth(1); p.setPen(lapiz)
        for col in range(COLUMNAS + 1):
            x = ox + col * celda
            p.drawLine(QPointF(x, oy), QPointF(x, oy + celda*FILAS))
        for fila in range(FILAS + 1):
            y = oy + fila * celda
            p.drawLine(QPointF(ox, y), QPointF(ox + celda*COLUMNAS, y))
        p.setPen(QPen(QColor(DORADO), 2)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(ox+1, oy+1, celda*COLUMNAS-2, celda*FILAS-2))

    def _dibujar_muro(self, p, col, fila, celda, ox, oy):
        r = QRectF(ox+col*celda, oy+fila*celda, celda, celda)
        p.fillRect(r, QColor("#1A1A08"))
        p.setPen(QPen(QColor("#404010"), 1)); p.setBrush(Qt.NoBrush)
        p.drawRect(r.adjusted(0, 0, -1, -1))
        mx = r.left() + celda/2; my = r.top() + celda/2
        p.drawLine(QPointF(r.left(), my), QPointF(r.right(), my))
        p.drawLine(QPointF(mx, r.top()), QPointF(mx, r.bottom()))

    def _dibujar_comida(self, p, col, fila, celda, ox, oy):
        c = self._centro_celda(col, fila, celda, ox, oy)
        r = celda * 0.30
        halo = QRadialGradient(c, r + celda*0.22)
        halo.setColorAt(0, QColor(204,34,34,70)); halo.setColorAt(1, QColor(0,0,0,0))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(halo))
        p.drawEllipse(c, r+celda*0.22, r+celda*0.22)
        grad = QRadialGradient(c.x()-r*0.3, c.y()-r*0.3, r*1.2)
        grad.setColorAt(0, QColor("#FF6060")); grad.setColorAt(0.5, QColor("#CC2020")); grad.setColorAt(1, QColor("#881010"))
        p.setBrush(QBrush(grad)); p.setPen(QPen(QColor("#440808"), max(1, int(celda*0.05))))
        p.drawEllipse(c, r, r)
        p.setPen(QPen(QColor("#44AA22"), max(1, int(celda*0.07))))
        p.drawLine(c+QPointF(0,-r), c+QPointF(celda*0.12, -r-celda*0.18))

    def _dibujar_veneno(self, p, col, fila, celda, ox, oy):
        c = self._centro_celda(col, fila, celda, ox, oy)
        r = celda * 0.30
        grad = QRadialGradient(c.x()-r*0.3, c.y()-r*0.3, r*1.2)
        grad.setColorAt(0, QColor("#CC80FF")); grad.setColorAt(0.6, QColor("#7020CC")); grad.setColorAt(1, QColor("#300870"))
        p.setBrush(QBrush(grad)); p.setPen(QPen(QColor("#200050"), 1))
        p.drawEllipse(c, r, r)
        if celda >= 14:
            f = p.font(); f.setPixelSize(max(8, int(celda*0.44))); p.setFont(f)
            p.setPen(QColor("#FFFFFF"))
            p.drawText(QRectF(ox+col*celda, oy+fila*celda, celda, celda), Qt.AlignCenter, "☠")

    def _dibujar_powerup(self, p, col, fila, tipo, celda, ox, oy):
        rect = self._rect_celda(col, fila, celda, ox, oy, 0.05)
        color = PU_COLOR[tipo]
        p.setPen(QPen(color, max(1, int(celda*0.07))))
        p.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
        p.drawRect(rect)
        sz = max(2, int(celda*0.12))
        for cx, cy in [(rect.left(), rect.top()), (rect.right()-sz, rect.top()),
                       (rect.left(), rect.bottom()-sz), (rect.right()-sz, rect.bottom()-sz)]:
            p.fillRect(QRectF(cx, cy, sz, sz), color)
        if celda >= 14:
            f = p.font(); f.setPixelSize(max(8, int(celda*0.50))); p.setFont(f)
            p.setPen(color)
            p.drawText(rect, Qt.AlignCenter, PU_ICONO[tipo])

    def _dibujar_serpiente(self, p, s, celda, ox, oy):
        alpha = 65 if s.invisible else 255
        cc = QColor(s.color_cabeza); cc.setAlpha(alpha)
        cb = QColor(s.color_cuerpo); cb.setAlpha(alpha)
        for i in range(len(s.cuerpo)-1, 0, -1):
            col, fila = s.cuerpo[i]
            ff = max(0.30, 1 - i/len(s.cuerpo)*0.70)
            cseg = QColor(int(cb.red()*ff), int(cb.green()*ff), int(cb.blue()*ff), alpha)
            mg = 0.07 + (i/len(s.cuerpo))*0.07
            rect = self._rect_celda(col, fila, celda, ox, oy, mg)
            cborde = QColor(int(cseg.red()*0.5), int(cseg.green()*0.5), int(cseg.blue()*0.5), alpha)
            p.setBrush(QBrush(cseg)); p.setPen(QPen(cborde, max(1, int(celda*0.04))))
            p.drawRect(rect)
        col_h, fila_h = s.cuerpo[0]
        rc = self._rect_celda(col_h, fila_h, celda, ox, oy, 0.04)
        grad = QLinearGradient(rc.topLeft(), rc.bottomRight())
        grad.setColorAt(0, cc.lighter(150)); grad.setColorAt(1, cc)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(int(cc.red()*0.4), int(cc.green()*0.4), int(cc.blue()*0.4), alpha), max(1, int(celda*0.06))))
        p.drawRect(rc)
        self._dibujar_ojos(p, col_h, fila_h, s.direccion, alpha, celda, ox, oy)
        if s.escudado:
            p.setPen(QPen(QColor(96, 192, 255, 200), max(2, int(celda*0.09))))
            p.setBrush(Qt.NoBrush)
            p.drawRect(rc.adjusted(-celda*0.10, -celda*0.10, celda*0.10, celda*0.10))

    def _dibujar_ojos(self, p, col, fila, dir, alpha, celda, ox, oy):
        cx = ox + col*celda + celda/2; cy = oy + fila*celda + celda/2
        dcol, dfila = dir; dist = celda*0.17
        if dcol == 1:    oj1, oj2 = (cx+dist, cy-dist), (cx+dist, cy+dist)
        elif dcol == -1: oj1, oj2 = (cx-dist, cy-dist), (cx-dist, cy+dist)
        elif dfila == -1: oj1, oj2 = (cx-dist, cy-dist), (cx+dist, cy-dist)
        else:             oj1, oj2 = (cx-dist, cy+dist), (cx+dist, cy+dist)
        rb = max(2.0, celda*0.11); rp = max(1.0, celda*0.055)
        p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(255, 255, 255, alpha)))
        for ex, ey in [oj1, oj2]: p.drawEllipse(QPointF(ex, ey), rb, rb)
        p.setBrush(QBrush(QColor(10, 10, 5, alpha)))
        for ex, ey in [oj1, oj2]: p.drawEllipse(QPointF(ex+dcol*rp, ey+dfila*rp), rp, rp)


# ── OVERLAY ───────────────────────────────────────────────────
class OverlayMensaje(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        self.lbl_titulo    = QLabel("")
        self.lbl_subtitulo = QLabel("")
        self.lbl_titulo.setFont(QFont("Segoe UI", 30, QFont.Bold))
        self.lbl_subtitulo.setFont(QFont("Segoe UI", 15))
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_subtitulo.setAlignment(Qt.AlignCenter)
        self.lbl_subtitulo.setStyleSheet(f"color: {GRIS}; background: transparent;")
        lay.addWidget(self.lbl_titulo)
        lay.addWidget(self.lbl_subtitulo)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(8, 8, 20, 200))

    def mostrar(self, titulo, subtitulo, color=DORADO):
        self.lbl_titulo.setText(titulo)
        self.lbl_titulo.setStyleSheet(f"color: {color}; background: transparent;")
        self.lbl_subtitulo.setText(subtitulo)


# ── HUD ───────────────────────────────────────────────────────
class PanelJugador(QWidget):
    def __init__(self, color_acento, alinear_derecha=False):
        super().__init__()
        self.color = color_acento
        self.setStyleSheet(f"background-color: {FONDO_MEDIO}; border-radius: 8px;")
        self.setMinimumWidth(160)
        self.setMaximumHeight(90)
        self._construir()

    def _construir(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 5, 8, 5)
        lay.setSpacing(2)
        self.lbl_nombre    = QLabel("JUGADOR")
        self.lbl_puntos    = QLabel("0 pts | 🐍 4")
        self.lbl_victorias = QLabel("○ ○ ○")
        self.lbl_powerup   = QLabel("— sin power-up")
        self.lbl_nombre.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_puntos.setFont(QFont("Segoe UI", 9))
        self.lbl_victorias.setFont(QFont("Segoe UI", 11))
        self.lbl_powerup.setFont(QFont("Segoe UI", 8))
        self.lbl_nombre.setStyleSheet(f"color: {self.color}; background: transparent;")
        self.lbl_puntos.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent;")
        self.lbl_powerup.setStyleSheet(f"color: {GRIS}; background: transparent;")
        for w in [self.lbl_nombre, self.lbl_puntos, self.lbl_victorias, self.lbl_powerup]:
            w.setAlignment(Qt.AlignCenter)
            lay.addWidget(w)

    def actualizar(self, nombre, puntos, longitud, victorias, pu_guardado, pu_activo, pu_ticks):
        self.lbl_nombre.setText(nombre.upper()[:14])
        self.lbl_puntos.setText(f"{puntos} pts | 🐍 {longitud}")
        texto_v = "".join("● " if i < victorias else "○ " for i in range(RONDAS_MAX)).strip()
        self.lbl_victorias.setText(texto_v)
        self.lbl_victorias.setStyleSheet(f"color: {self.color}; background: transparent;")
        if pu_guardado:
            self.lbl_powerup.setText(f"{PU_ICONO[pu_guardado]} {PU_NOMBRE[pu_guardado]}")
            self.lbl_powerup.setStyleSheet(f"color: {DORADO_CLARO}; background: transparent;")
        elif pu_activo:
            self.lbl_powerup.setText(f"{PU_ICONO[pu_activo]} activo {pu_ticks}s")
            self.lbl_powerup.setStyleSheet(f"color: {NARANJA}; background: transparent; font-weight: bold;")
        else:
            self.lbl_powerup.setText("— sin power-up")
            self.lbl_powerup.setStyleSheet(f"color: {GRIS}; background: transparent;")

    def parpadear_sin_powerup(self):
        orig = self.lbl_powerup.styleSheet()
        self.lbl_powerup.setStyleSheet(f"color: {ROJO}; background: transparent; font-weight: bold;")
        self.lbl_powerup.setText("✗ SIN POWER-UP")
        QTimer.singleShot(400, lambda: self.lbl_powerup.setStyleSheet(orig))


class PanelCentral(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(120)
        self.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignCenter)
        self.lbl_ronda  = QLabel("RONDA 1")
        self.lbl_tiempo = QLabel("90")
        self.lbl_ronda.setFont(QFont("Segoe UI", 9))
        self.lbl_tiempo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.lbl_ronda.setStyleSheet(f"color: {GRIS}; background: transparent;")
        self.lbl_tiempo.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent;")
        for w in [self.lbl_ronda, self.lbl_tiempo]:
            w.setAlignment(Qt.AlignCenter)
            lay.addWidget(w)

    def actualizar(self, ronda, segundos):
        self.lbl_ronda.setText(f"RONDA {ronda}")
        self.lbl_tiempo.setText(str(max(0, segundos)))
        color = ROJO if segundos <= 10 else BLANCO_CALIDO
        self.lbl_tiempo.setStyleSheet(f"color: {color}; background: transparent;")


# ── PANTALLA DE JUEGO ─────────────────────────────────────────
class PantallaJuego(QWidget):
    """
    Modos:
      local     — dos jugadores en la misma máquina
      anfitrion — corre la lógica, envía estado, recibe teclas y nombre
      cliente   — recibe estado, envía teclas y nombre propio
    """

    def __init__(self, ventana_principal=None,
                 nombre_j1="Jugador 1", nombre_j2="Jugador 2",
                 ip_red="", modo_red="local",
                 color_j1=None, color_j2=None,
                 sock_existente=None):
        super().__init__(ventana_principal)
        self.ventana   = ventana_principal
        self.nombre_j1 = nombre_j1
        self.nombre_j2 = nombre_j2
        self.ip_red    = ip_red
        self.modo_red  = modo_red

        c_j1 = color_j1 if color_j1 else COLORES_J1[0]
        c_j2 = color_j2 if color_j2 else COLORES_J2[0]

        self.estado = EstadoJuego(colores_j1=c_j1, colores_j2=c_j2,
                                  nombres=[nombre_j1, nombre_j2])

        self._red               = None
        self._conectado         = (modo_red == "local")
        self._partida_terminada = False

        self.timer_juego   = QTimer(self)
        self.timer_segundo = QTimer(self)
        self.timer_juego.timeout.connect(self._tick_juego)
        self.timer_segundo.timeout.connect(self._tick_segundo)

        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")
        self.setFocusPolicy(Qt.StrongFocus)
        self._construir_interfaz()

        if modo_red in ("anfitrion", "cliente"):
            # SIEMPRE crear nueva conexión
            self._iniciar_red()
        else:
            self._mostrar_overlay(f"RONDA {self.estado.numero_ronda}", "¡Prepárense!", DORADO)
            QTimer.singleShot(1800, self._iniciar_ronda)

    # ── Interfaz ──────────────────────────────────────────────

    def _construir_interfaz(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._crear_hud_superior())
        self.canvas = CanvasJuego()
        self.canvas.asignar_estado(self.estado)
        raiz.addWidget(self.canvas, stretch=1)
        raiz.addWidget(self._crear_barra_inferior())
        self.overlay = OverlayMensaje(self)
        self.overlay.hide()

    def _crear_hud_superior(self):
        panel = QWidget()
        panel.setFixedHeight(100)
        panel.setStyleSheet(f"background-color: {FONDO_MEDIO}; border-bottom: 3px solid {DORADO};")
        lay = QHBoxLayout(panel)
        lay.setContentsMargins(15, 5, 15, 5)
        lay.setSpacing(15)
        self.panel_j1  = PanelJugador(VERDE)
        self.panel_cen = PanelCentral()
        self.panel_j2  = PanelJugador(AZUL)
        lay.addStretch()
        lay.addWidget(self.panel_j1)
        lay.addStretch()
        lay.addWidget(self.panel_cen)
        lay.addStretch()
        lay.addWidget(self.panel_j2)
        lay.addStretch()
        return panel

    def _crear_barra_inferior(self):
        barra = QWidget()
        barra.setFixedHeight(34)
        barra.setStyleSheet(f"background-color: {FONDO_MEDIO}; border-top: 2px solid {DORADO};")
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(16, 0, 16, 0)
        if self.modo_red == "cliente":
            hint = f"J2 (tú): {self.nombre_j2}  ↑↓←→+/"
        elif self.modo_red == "anfitrion":
            hint = f"J1 (tú): {self.nombre_j1}  WASD+Q   │   J2 (cliente): {self.nombre_j2}  ↑↓←→+/"
        else:
            hint = f"J1: {self.nombre_j1}  WASD+Q   │   J2: {self.nombre_j2}  ↑↓←→+/"
        texto = QLabel(hint)
        texto.setFont(QFont("Consolas", 9))
        texto.setStyleSheet(f"color: {GRIS}; background: transparent;")
        texto.setAlignment(Qt.AlignCenter)
        lay.addStretch(); lay.addWidget(texto); lay.addStretch()
        return barra

    # ── Red ───────────────────────────────────────────────────

    def _iniciar_red(self):
        msg = "🏠  Esperando al cliente…" if self.modo_red == "anfitrion" else f"🔗  Conectando a {self.ip_red}…"
        self._mostrar_overlay("CONECTANDO", msg, AZUL)

        # El cliente pasa su nombre propio (nombre_j2 desde su configuración)
        self._red = ConexionRed(self.modo_red, self.ip_red,
                                nombre_cliente=self.nombre_j2)
        self._red.señales.estado_recibido.connect(self._en_estado_recibido)
        self._red.señales.tecla_recibida.connect(self._en_tecla_recibida)
        self._red.señales.nombre_recibido.connect(self._en_nombre_recibido)
        self._red.señales.desconectado.connect(self._en_desconexion)
        self._red.conectar()

        self._timer_espera_red = QTimer(self)
        self._timer_espera_red.timeout.connect(self._verificar_conexion)
        self._timer_espera_red.start(200)

    def _verificar_conexion(self):
        if self._red and self._red._activo:
            self._timer_espera_red.stop()
            self._conectado = True
            self._mostrar_overlay(f"RONDA {self.estado.numero_ronda}", "¡Prepárense!", DORADO)
            QTimer.singleShot(1800, self._iniciar_ronda)

    def _en_estado_recibido(self, datos: dict):
        """Cliente: recibe estado del anfitrión y actualiza la UI."""

        tipo = datos.get("tipo")

        # Mensaje de fin de partida
        if tipo == "fin_partida":
            self._partida_terminada = True
            self.timer_juego.stop()
            self.timer_segundo.stop()
            self._ocultar_overlay()

            if self._red:
                self._red.cerrar()

            musica.iniciar()
            from pantalla.resultado import PantallaResultado
            self.ventana.setCentralWidget(
                PantallaResultado(
                    self.ventana,
                    nombre_ganador=datos["ganador"],
                    victorias=datos["victorias"],
                    puntos=datos["puntos"],
                    nombres=datos["nombres"]
                )
            )
            return

        # Mensaje de overlay (ganador de ronda, siguiente ronda, etc.)
        if tipo == "overlay":
            self._mostrar_overlay(
                datos.get("titulo", ""),
                datos.get("subtitulo", ""),
                datos.get("color", DORADO)
            )
            # Si hay que ocultar después de un tiempo
            if datos.get("auto_ocultar"):
                QTimer.singleShot(datos.get("tiempo", 1800), self._ocultar_overlay)
            return

        # Estado normal del juego
        if tipo == "estado":
            self.estado.cargar_desde_red(datos)
            self.canvas.update()
            self._actualizar_hud()

    def _en_tecla_recibida(self, codigo: str):
        """Anfitrión: aplica la tecla del cliente al Jugador 2."""
        j2 = self.estado.serpientes[1]
        if   codigo == "UP":    j2.cambiar_direccion(0, -1)
        elif codigo == "DOWN":  j2.cambiar_direccion(0, 1)
        elif codigo == "LEFT":  j2.cambiar_direccion(-1, 0)
        elif codigo == "RIGHT": j2.cambiar_direccion(1, 0)
        elif codigo == "PU":    self.estado.usar_powerup(1)

    def _en_nombre_recibido(self, nombre: str):
        """Anfitrión: actualiza el nombre de J2 con el que envió el cliente."""
        self.estado.nombres[1]          = nombre
        self.estado.serpientes[1].nombre = nombre
        self._actualizar_hud()

    def _en_desconexion(self):
        if self._partida_terminada:
            return  # No mostrar nada si ya terminó

        self.timer_juego.stop()
        self.timer_segundo.stop()
        self._mostrar_overlay("❌ DESCONECTADO", "El rival se desconectó", ROJO)

    # ── Lógica ────────────────────────────────────────────────

    def _iniciar_ronda(self):
        self._ocultar_overlay()
        if self.modo_red != "cliente":
            self.timer_juego.start(VELOCIDAD)
            self.timer_segundo.start(1000)
            # Enviar estado inicial al cliente
            if self.modo_red == "anfitrion" and self._red:
                self._red.enviar_estado(self.estado.serializar())
        self.canvas.setFocus()

    def _tick_juego(self):
        resultado = self.estado.tick()
        self.canvas.update()
        self._actualizar_hud()

        if self.modo_red == "anfitrion" and self._red:
            self._red.enviar_estado(self.estado.serializar(resultado))

        if resultado is not None:
            self.timer_juego.stop()
            self.timer_segundo.stop()
            self._fin_ronda(resultado)

    def _tick_segundo(self):
        self._actualizar_hud()

    def _actualizar_hud(self):
        j0, j1 = self.estado.serpientes
        self.panel_j1.actualizar(j0.nombre, j0.puntos, len(j0.cuerpo),
                                  self.estado.victorias[0],
                                  j0.pu_guardado, j0.pu_activo, j0.pu_ticks)
        self.panel_j2.actualizar(j1.nombre, j1.puntos, len(j1.cuerpo),
                                  self.estado.victorias[1],
                                  j1.pu_guardado, j1.pu_activo, j1.pu_ticks)
        self.panel_cen.actualizar(self.estado.numero_ronda, self.estado.tiempo)

    def _fin_ronda(self, ganador, solo_mostrar=False):
        if self._partida_terminada:
            return

        # Actualizar victorias
        if ganador == -1:
            mensaje = "¡EMPATE!"
            color = DORADO
        else:
            nombre = self.estado.serpientes[ganador].nombre
            color = VERDE if ganador == 0 else AZUL
            if not solo_mostrar:
                self.estado.victorias[ganador] += 1
            mensaje = f"🏆 {nombre} gana la ronda"

        self._mostrar_overlay(mensaje, "", color)

        # Enviar overlay al cliente
        if self.modo_red == "anfitrion" and self._red and self._red._activo:
            try:
                self._red.enviar_estado({
                    "tipo": "overlay",
                    "titulo": mensaje,
                    "subtitulo": "",
                    "color": color,
                    "auto_ocultar": False
                })
            except Exception:
                pass

        # Verificar si la partida terminó
        if max(self.estado.victorias) >= RONDAS_MAX:
            if not self._partida_terminada:
                QTimer.singleShot(3000, self._fin_partida)
        else:
            if not solo_mostrar:
                self.estado.siguiente_ronda()

            def mostrar_siguiente_ronda():
                if self._partida_terminada:
                    return
                ronda_msg = f"RONDA {self.estado.numero_ronda}"
                self._mostrar_overlay(ronda_msg, "¡Prepárense!", DORADO)

                if self.modo_red == "anfitrion" and self._red and self._red._activo:
                    try:
                        self._red.enviar_estado({
                            "tipo": "overlay",
                            "titulo": ronda_msg,
                            "subtitulo": "¡Prepárense!",
                            "color": DORADO,
                            "auto_ocultar": True,
                            "tiempo": 1800
                        })
                    except Exception:
                        pass

                QTimer.singleShot(2000, self._iniciar_ronda)

            QTimer.singleShot(2500, mostrar_siguiente_ronda)

    def _fin_partida(self):
        if self._partida_terminada:
            return
        self._partida_terminada = True

        # DETENER todos los timers inmediatamente
        self.timer_juego.stop()
        self.timer_segundo.stop()

        self._ocultar_overlay()

        # Determinar ganador
        if self.estado.victorias[0] > self.estado.victorias[1]:
            ganador_idx = 0
        elif self.estado.victorias[1] > self.estado.victorias[0]:
            ganador_idx = 1
        else:
            ganador_idx = 0

        nombre_ganador = self.estado.nombres[ganador_idx]
        puntos = [self.estado.serpientes[0].puntos, self.estado.serpientes[1].puntos]

        # Solo el anfitrión guarda la puntuación y envía fin de partida
        if self.modo_red == "anfitrion":
            self._guardar_resultado(nombre_ganador, puntos[ganador_idx])

            # Enviar comando de fin de partida al cliente
            if self._red and self._red._activo:
                try:
                    self._red.enviar_estado({
                        "tipo": "fin_partida",
                        "ganador": nombre_ganador,
                        "victorias": self.estado.victorias,
                        "puntos": puntos,
                        "nombres": self.estado.nombres
                    })
                except Exception:
                    pass

            # Cerrar conexión con delay para que el mensaje llegue
            if self._red:
                QTimer.singleShot(1000, self._red.cerrar)

        # Usar QTimer seguro para evitar crash
        QTimer.singleShot(500, lambda: self._mostrar_resultados(nombre_ganador, puntos))

    def _mostrar_resultados(self, nombre_ganador, puntos):
        """Método separado para mostrar resultados de forma segura."""
        try:
            musica.iniciar()
            from pantalla.resultado import PantallaResultado
            self.ventana.setCentralWidget(
                PantallaResultado(
                    self.ventana,
                    nombre_ganador=nombre_ganador,
                    victorias=self.estado.victorias,
                    puntos=puntos,
                    nombres=self.estado.nombres
                )
            )
        except Exception:
            pass

    def _guardar_resultado(self, nombre_ganador, puntos_ganador):
        ruta  = ruta_datos("puntuaciones.json")
        lista = []
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    lista = json.load(f)
            except Exception:
                lista = []
        lista.insert(0, {
            "nombre": nombre_ganador, "puntos": puntos_ganador,
            "rondas": f"{self.estado.victorias[0]}-{self.estado.victorias[1]}",
            "fecha":  datetime.now().strftime("%d/%m/%Y"),
        })
        lista = lista[:50]
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ── Overlay ───────────────────────────────────────────────

    def _mostrar_overlay(self, titulo, subtitulo, color):
        self.overlay.mostrar(titulo, subtitulo, color)
        self.overlay.setGeometry(self.rect())
        self.overlay.show()
        self.overlay.raise_()

    def _ocultar_overlay(self):
        self.overlay.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.overlay.setGeometry(self.rect())

    # ── Teclado ───────────────────────────────────────────────

    def keyPressEvent(self, e):
        if not self.estado:
            return
        j0, j1 = self.estado.serpientes
        tecla  = e.key()

        # SI ES EL CLIENTE: envía teclas al servidor, no ejecuta localmente
        if self.modo_red == "cliente":
            if   tecla == Qt.Key_Up:    self._red.enviar_tecla("UP")
            elif tecla == Qt.Key_Down:  self._red.enviar_tecla("DOWN")
            elif tecla == Qt.Key_Left:  self._red.enviar_tecla("LEFT")
            elif tecla == Qt.Key_Right: self._red.enviar_tecla("RIGHT")
            elif tecla in (Qt.Key_Slash, Qt.Key_Minus, Qt.Key_Period,
                           Qt.Key_0, Qt.Key_Insert, Qt.Key_End,
                           Qt.Key_PageDown, Qt.Key_Delete):
                self._red.enviar_tecla("PU")
            return

        # SI ES ANFITRIÓN O LOCAL: Controles de J1 (WASD+Q)
        if   tecla == Qt.Key_W: j0.cambiar_direccion(0, -1)
        elif tecla == Qt.Key_S: j0.cambiar_direccion(0, 1)
        elif tecla == Qt.Key_A: j0.cambiar_direccion(-1, 0)
        elif tecla == Qt.Key_D: j0.cambiar_direccion(1, 0)
        elif tecla == Qt.Key_Q:
            if not self.estado.usar_powerup(0):
                self.panel_j1.parpadear_sin_powerup()

        # SI ES LOCAL: Controles de J2 (Flechas+/)
        if self.modo_red == "local":
            if   tecla == Qt.Key_Up:    j1.cambiar_direccion(0, -1)
            elif tecla == Qt.Key_Down:  j1.cambiar_direccion(0, 1)
            elif tecla == Qt.Key_Left:  j1.cambiar_direccion(-1, 0)
            elif tecla == Qt.Key_Right: j1.cambiar_direccion(1, 0)
            elif tecla in (Qt.Key_Slash, Qt.Key_Minus, Qt.Key_Period,
                           Qt.Key_0, Qt.Key_Insert, Qt.Key_End,
                           Qt.Key_PageDown, Qt.Key_Delete):
                if not self.estado.usar_powerup(1):
                    self.panel_j2.parpadear_sin_powerup()

        # ESC: volver al menú
        if tecla == Qt.Key_Escape:
            self._partida_terminada = True
            self.timer_juego.stop()
            self.timer_segundo.stop()
            if self._red:
                self._red.cerrar()
            musica.iniciar()
            from pantalla.inicio import PantallaInicio
            self.ventana.setCentralWidget(PantallaInicio(self.ventana))