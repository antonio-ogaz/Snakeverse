"""
pantalla/juego.py — Pantalla principal del juego SNAKEVERSE

Contiene toda la lógica del juego:
  - Clase Serpiente: movimiento, colisiones, power-ups
  - Clase EstadoJuego: mapa, rondas, spawns
  - CanvasJuego: dibuja todo con QPainter
  - PantallaJuego: HUD + canvas + teclado
"""

import random
import json
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy,
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QBrush, QPen,
    QLinearGradient, QRadialGradient,
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF

from utilidad.musica import musica
from utilidad.estilos import (
    DORADO, DORADO_CLARO, VERDE, VERDE_OSCURO,
    AZUL, AZUL_OSCURO, ROJO, NARANJA, MORADO,
    BLANCO_CALIDO, GRIS,
    FONDO_OSCURO, FONDO_MEDIO, BORDE_ACTIVO,
    estilo_ventana,
)

#  CONSTANTES DEL MAPA Y PARTIDA

COLUMNAS = 28  # celdas horizontales del mapa
FILAS = 20  # celdas verticales del mapa
RONDAS_MAX = 3  # victorias para ganar la partida
TIEMPO_RONDA = 90  # segundos por ronda
VELOCIDAD = 135  # milisegundos entre cada tick del juego
COMIDAS = 4  # comidas simultáneas en el mapa

# ── Identificadores de power-ups ──────────────────────────────
PU_CAMUFLAJE = "camuflaje"  # serpiente casi invisible
PU_TURBO = "turbo"  # doble velocidad temporal
PU_ESCUDO = "escudo"  # absorbe una colisión
PU_CORTE = "corte"  # reduce cola del rival

LISTA_POWERUPS = [PU_CAMUFLAJE, PU_TURBO, PU_ESCUDO, PU_CORTE]

PU_ICONO = {
    PU_CAMUFLAJE: "👁",
    PU_TURBO: "⚡",
    PU_ESCUDO: "🛡",
    PU_CORTE: "✂",
}
PU_NOMBRE = {
    PU_CAMUFLAJE: "Camuflaje",
    PU_TURBO: "Turbo",
    PU_ESCUDO: "Escudo",
    PU_CORTE: "Corte",
}
PU_DURACION = {
    PU_CAMUFLAJE: 28,  # ticks de efecto
    PU_TURBO: 22,
    PU_ESCUDO: 16,
    PU_CORTE: 0,  # instantáneo, sin duración
}
PU_COLOR = {
    PU_CAMUFLAJE: QColor("#9060FF"),
    PU_TURBO: QColor("#FFD040"),
    PU_ESCUDO: QColor("#40C0FF"),
    PU_CORTE: QColor("#FF6060"),
}

# Colores disponibles para las serpientes
COLORES_J1 = [
    ("#2ECC40", "#1A8C28"),  # verde vibrante (igual al logo)
    ("#40FF60", "#20B040"),  # verde neón
    ("#FFD040", "#C09010"),  # dorado
    ("#80FF40", "#40B020"),  # verde lima
]
COLORES_J2 = [
    ("#209AE8", "#1464A8"),  # azul eléctrico (igual al logo)
    ("#40B8FF", "#1880D0"),  # azul cielo
    ("#E03060", "#A01040"),  # rojo vibrante
    ("#E8C020", "#A08010"),  # amarillo

]

#  CLASE SERPIENTE

class Serpiente:
    """
    Representa una serpiente en el juego.

    Atributos de posición:
        cuerpo          : lista de (col, fila), índice 0 = cabeza
        direccion       : dirección actual como (dcol, dfila)
        dir_siguiente   : próxima dirección solicitada por el jugador

    Atributos visuales:
        color_cabeza    : QColor de la cabeza
        color_cuerpo    : QColor del cuerpo
        nombre          : nombre del jugador dueño

    Atributos de estado:
        viva            : False cuando choca y muere
        puntos          : puntos acumulados en la partida

    Atributos de power-up:
        pu_guardado     : power-up en inventario (str | None)
        pu_activo       : power-up con efecto activo (str | None)
        pu_ticks        : ticks restantes del efecto activo
        invisible       : True mientras Camuflaje está activo
        escudado        : True mientras Escudo está activo
        turbo           : True mientras Turbo está activo
        invertida       : True si comió veneno (controles al revés)
        ticks_invertida : ticks restantes de inversión de controles
    """

    def __init__(self, col_inicio: int, fila_inicio: int,
                 direccion: tuple, colores: tuple, nombre: str):
        # Generar cuerpo inicial (4 segmentos desde la cabeza hacia atrás)
        self.cuerpo = [
            (col_inicio - direccion[0] * i,
             fila_inicio - direccion[1] * i)
            for i in range(4)
        ]
        self.direccion = direccion
        self.dir_siguiente = direccion
        self.color_cabeza = QColor(colores[0])
        self.color_cuerpo = QColor(colores[1])
        self.nombre = nombre

        # Estado
        self.viva = True
        self.puntos = 0

        # Power-up
        self.pu_guardado = None
        self.pu_activo = None
        self.pu_ticks = 0
        self.invisible = False
        self.escudado = False
        self.turbo = False
        self.invertida = False
        self.ticks_invertida = 0

    def cabeza(self) -> tuple:
        """Retorna la posición (col, fila) de la cabeza."""
        return self.cuerpo[0]

    def cambiar_direccion(self, dcol: int, dfila: int):

        """
        Solicita un cambio de dirección.
        - Si está invertida por veneno, invierte dcol y dfila.
        - Ignora el cambio si sería un giro de 180°.
        """
        if self.invertida:
            dcol, dfila = -dcol, -dfila
        # No permitir giro de 180° (dirección opuesta a la actual)
        if (dcol, dfila) != (-self.direccion[0], -self.direccion[1]):
            self.dir_siguiente = (dcol, dfila)

    def avanzar(self, crecer: bool = False):
        """
        Mueve la serpiente un paso en la dirección solicitada.
        Si crecer=True, no elimina la cola (la serpiente crece).
        """
        self.direccion = self.dir_siguiente
        col, fila = self.cuerpo[0]
        nueva_cabeza = (col + self.direccion[0], fila + self.direccion[1])
        self.cuerpo.insert(0, nueva_cabeza)
        if not crecer:
            self.cuerpo.pop()

    def sacar_powerup(self) -> str | None:






        """
        Extrae el power-up del inventario para activarlo.
        Retorna el tipo (str) o None si el inventario está vacío.
        """
        if self.pu_guardado:
            tipo = self.pu_guardado
            self.pu_guardado = None
            return tipo
        return None


    def activar_powerup(self, tipo: str, rival: "Serpiente"):
        """
        Aplica el efecto del power-up indicado.
        PU_CORTE es instantáneo y afecta al rival.
        El resto aplica un efecto temporal a esta serpiente.
        """
        if tipo == PU_CAMUFLAJE:
            self.pu_activo = tipo
            self.pu_ticks = PU_DURACION[tipo]
            self.invisible = True

        elif tipo == PU_TURBO:
            self.pu_activo = tipo
            self.pu_ticks = PU_DURACION[tipo]
            self.turbo = True

        elif tipo == PU_ESCUDO:
            self.pu_activo = tipo
            self.pu_ticks = PU_DURACION[tipo]
            self.escudado = True

        elif tipo == PU_CORTE:
            # Instantáneo: recorta la cola del rival en un tercio
            if len(rival.cuerpo) > 5:
                corte = max(2, len(rival.cuerpo) // 3)
                rival.cuerpo = rival.cuerpo[:-corte]
            # No se asigna pu_activo porque ya terminó

    def actualizar_efectos(self):
        """
        Descuenta un tick de los efectos activos:
        - Veneno (controles invertidos)
        - Power-up con duración
        """
        # Veneno
        if self.ticks_invertida > 0:
            self.ticks_invertida -= 1
            if self.ticks_invertida == 0:
                self.invertida = False

        # Power-up activo
        if self.pu_activo is not None:
            duracion = PU_DURACION.get(self.pu_activo, 0)
            if duracion > 0:
                self.pu_ticks -= 1
                if self.pu_ticks <= 0:
                    self._desactivar_powerup()

    def _desactivar_powerup(self):
        """Quita el efecto del power-up activo."""
        if self.pu_activo == PU_CAMUFLAJE:
            self.invisible = False
        elif self.pu_activo == PU_TURBO:
            self.turbo = False
        elif self.pu_activo == PU_ESCUDO:
            self.escudado = False
        self.pu_activo = None
        self.pu_ticks = 0

    # ── Serialización para envío por red ─────────────────────

    def serializar(self) -> dict:






        return {
            "cuerpo": self.cuerpo,
            "direccion": list(self.direccion),
            "dir_siguiente": list(self.dir_siguiente),
            "viva": self.viva,
            "puntos": self.puntos,
            "nombre": self.nombre,
            "pu_guardado": self.pu_guardado,
            "pu_activo": self.pu_activo,
            "pu_ticks": self.pu_ticks,
            "invisible": self.invisible,
            "escudado": self.escudado,
            "turbo": self.turbo,
            "invertida": self.invertida,
            "ticks_invertida": self.ticks_invertida,
        }

    def cargar_desde_dict(self, datos: dict):
        self.cuerpo = [tuple(p) for p in datos["cuerpo"]]
        self.direccion = tuple(datos["direccion"])
        self.dir_siguiente = tuple(datos["dir_siguiente"])
        self.viva = datos["viva"]
        self.puntos = datos["puntos"]
        self.nombre = datos["nombre"]
        self.pu_guardado = datos["pu_guardado"]
        self.pu_activo = datos["pu_activo"]
        self.pu_ticks = datos["pu_ticks"]
        self.invisible = datos["invisible"]
        self.escudado = datos["escudado"]
        self.turbo = datos["turbo"]
        self.invertida = datos["invertida"]
        self.ticks_invertida = datos["ticks_invertida"]

#  ESTADO DEL JUEGO
class EstadoJuego:

    """
    Contiene toda la lógica de la partida:
    - Posiciones de serpientes, comidas, venenos, power-ups, muros
    - Movimiento y colisiones
    - Control de rondas y victorias
    - Spawn aleatorio de elementos
    """

    def __init__(self, colores_j1: tuple, colores_j2: tuple, nombres: list):
        self.colores_j1 = colores_j1
        self.colores_j2 = colores_j2
        self.nombres = nombres
        self.victorias = [0, 0]
        self.numero_ronda = 1
        self._reiniciar_ronda()

    def _reiniciar_ronda(self):
        """Reinicia el mapa para una nueva ronda."""
        fila_centro = FILAS // 2
        self.serpientes = [
            Serpiente(6, fila_centro, (1, 0), self.colores_j1, self.nombres[0]),
            Serpiente(COLUMNAS - 7, fila_centro, (-1, 0), self.colores_j2, self.nombres[1]),















        ]
        self.comidas = []  # lista de (col, fila)
        self.venenos = []  # lista de (col, fila)
        self.powerups = []  # lista de (col, fila, tipo)
        self.muros = []  # lista de (col, fila)
        self.tiempo = TIEMPO_RONDA
        self.ticks = 0

        self._generar_comidas(COMIDAS)
        self._generar_venenos(1)
        self._generar_muros(max(0, self.numero_ronda - 1) * 3)
        self._generar_powerups(2)  # siempre 2 power-ups al inicio

    # Generación de elementos

    def _celdas_ocupadas(self) -> set:
        """Retorna el conjunto de celdas ya usadas."""
        ocupadas = set()
        for s in self.serpientes:
            ocupadas.update(s.cuerpo)
        ocupadas.update(self.comidas)
        ocupadas.update(self.venenos)
        ocupadas.update((col, fila) for col, fila, _ in self.powerups)
        ocupadas.update(self.muros)
        return ocupadas

    def _celda_libre(self):
        """Devuelve una celda aleatoria que no esté ocupada."""
        ocupadas = self._celdas_ocupadas()
        for _ in range(600):
            col = random.randint(2, COLUMNAS - 3)
            fila = random.randint(2, FILAS - 3)
            if (col, fila) not in ocupadas:
                return (col, fila)
        return None

    def _generar_comidas(self, cantidad: int):
        for _ in range(cantidad):
            celda = self._celda_libre()
            if celda:
                self.comidas.append(celda)

    def _generar_venenos(self, cantidad: int):
        for _ in range(cantidad):
            celda = self._celda_libre()
            if celda:
                self.venenos.append(celda)

    def _generar_muros(self, cantidad: int):
        for _ in range(cantidad):
            celda = self._celda_libre()
            if celda:
                self.muros.append(celda)

    def _generar_powerups(self, cantidad: int = 1):
        for _ in range(cantidad):
            celda = self._celda_libre()
            if celda:
                tipo = random.choice(LISTA_POWERUPS)
                self.powerups.append((celda[0], celda[1], tipo))

    def _spawn_aleatorio(self):
        """Genera elementos aleatoriamente cada tick para mantener el mapa vivo."""
        # Mantener siempre al menos 2 power-ups visibles
        if len(self.powerups) < 2 and random.random() < 0.30:
            self._generar_powerups(1)
        elif len(self.powerups) < 3 and random.random() < 0.03:
            self._generar_powerups(1)

        # Reponer comidas cuando hay menos de las necesarias
        if len(self.comidas) < COMIDAS and random.random() < 0.25:
            self._generar_comidas(1)

        # Muros progresivos: más muros conforme avanza la partida
        limite_muros = (self.numero_ronda - 1) * 3 + self.ticks // 180
        if len(self.muros) < limite_muros and random.random() < 0.02:
            celda = self._celda_libre()
            if celda:
                self.muros.append(celda)

    # Tick principal

    def tick(self):














        """
        Ejecuta un paso de la lógica del juego.
        Retorna:
            None  — la ronda continúa
            0     — ganó el Jugador 1
            1     — ganó el Jugador 2
            -1    — empate (ambas murieron al mismo tiempo o tiempo agotado)
        """
        self.ticks += 1
        self._spawn_aleatorio()

        # Movimiento normal de todas las serpientes vivas
        for idx in range(2):
            if self.serpientes[idx].viva:
                self._mover(idx)



        # Segundo movimiento para serpientes con Turbo activo
        for idx in range(2):
            if self.serpientes[idx].viva and self.serpientes[idx].turbo:
                self._mover_turbo(idx)

        # Actualizar timers de power-ups y veneno
        for s in self.serpientes:
            s.actualizar_efectos()

        # Reducir tiempo de ronda
        if self.ticks % 10 == 0:  # Aprox cada segundo (10 ticks = 1.35s)
            self.tiempo = max(0, self.tiempo - 1)

        return self._revisar_fin_ronda()

    def _mover(self, idx: int):
        """
        Mueve la serpiente idx con comprobación completa de colisiones.
        Si choca y tiene Escudo, absorbe la colisión (no muere).
        Si choca sin Escudo, muere.
        """
        serpiente = self.serpientes[idx]
        rival = self.serpientes[1 - idx]

        serpiente.avanzar()
        col, fila = serpiente.cabeza()

        # 1. Colisión con el borde del mapa
        fuera_del_mapa = not (0 <= col < COLUMNAS and 0 <= fila < FILAS)
        if fuera_del_mapa:
            if serpiente.escudado:
                # El escudo "teletransporta" al lado opuesto
                col = col % COLUMNAS
                fila = fila % FILAS
                serpiente.cuerpo[0] = (col, fila)
                serpiente.escudado = False
                serpiente.pu_activo = None
            else:
                serpiente.viva = False
                return

        # 2. Colisión con un muro
        if (col, fila) in self.muros:
            if serpiente.escudado:
                serpiente.cuerpo.pop(0)  # retrocede el paso
                serpiente.escudado = False
                serpiente.pu_activo = None
            else:
                serpiente.viva = False
                return

        # 3. Colisión con el propio cuerpo
        if (col, fila) in serpiente.cuerpo[1:]:
            if serpiente.escudado:
                serpiente.cuerpo.pop(0)
                serpiente.escudado = False
                serpiente.pu_activo = None
            else:
                serpiente.viva = False
                return

        # 4. Colisión con la serpiente rival
        if (col, fila) in rival.cuerpo:
            if serpiente.escudado:
                serpiente.cuerpo.pop(0)
                serpiente.escudado = False
                serpiente.pu_activo = None
            else:
                serpiente.viva = False
                return

        # 5. Procesar lo que hay en la celda
        self._procesar_celda(serpiente, col, fila)

    def _mover_turbo(self, idx: int):





        """
        Segundo paso de movimiento para serpientes con Turbo.
        No aplica colisiones fatales — si choca simplemente
        retrocede el paso extra para evitar muertes injustas.
        """
        serpiente = self.serpientes[idx]
        rival = self.serpientes[1 - idx]

        # Guardar posición antes de mover
        pos_anterior = serpiente.cuerpo[0]



        serpiente.avanzar()
        col, fila = serpiente.cabeza()

        # Si choca en el paso extra, simplemente retroceder
        choca = (
                not (0 <= col < COLUMNAS and 0 <= fila < FILAS)
                or (col, fila) in self.muros
                or (col, fila) in serpiente.cuerpo[1:]
                or (col, fila) in rival.cuerpo

        )
        if choca:
            serpiente.cuerpo.pop(0)
            return

        self._procesar_celda(serpiente, col, fila)

    def _procesar_celda(self, serpiente: Serpiente, col: int, fila: int):
        """Gestiona comida, veneno y power-ups en la celda (col, fila)."""
        # ¿Comida normal?
        if (col, fila) in self.comidas:
            self.comidas.remove((col, fila))
            serpiente.cuerpo.append(serpiente.cuerpo[-1])  # crecer
            serpiente.puntos += 10

        # ¿Veneno?
        if (col, fila) in self.venenos:
            self.venenos.remove((col, fila))
            serpiente.invertida = True
            serpiente.ticks_invertida = 30
            self._generar_venenos(1)  # reponer el veneno consumido

        # ¿Power-up?
        for pu in self.powerups[:]:
            if (col, fila) == (pu[0], pu[1]):
                self.powerups.remove(pu)
                # Solo guardar si el inventario está vacío
                if serpiente.pu_guardado is None:
                    serpiente.pu_guardado = pu[2]
                break

    def usar_powerup(self, idx: int) -> bool:
        """
        Activa el power-up guardado del jugador idx.
        Retorna True si se activó algo, False si el inventario estaba vacío.
        """
        serpiente = self.serpientes[idx]
        rival = self.serpientes[1 - idx]
        tipo = serpiente.sacar_powerup()
        if tipo:
            serpiente.activar_powerup(tipo, rival)
            return True
        return False

    # Condición de fin de ronda










    def _revisar_fin_ronda(self):


        """
        Comprueba si la ronda terminó.
        Desempate por longitud si el tiempo se agota.
        """
        j0, j1 = self.serpientes

        if not j0.viva and not j1.viva:
            # Ambas murieron: gana la más larga
            return 0 if len(j0.cuerpo) >= len(j1.cuerpo) else 1

        if not j0.viva: return 1
        if not j1.viva: return 0

        if self.tiempo <= 0:
            # Tiempo agotado: desempate por longitud
            if len(j0.cuerpo) > len(j1.cuerpo): return 0
            if len(j1.cuerpo) > len(j0.cuerpo): return 1
            return -1  # empate real

        return None  # la ronda continúa


    def siguiente_ronda(self):
        """Prepara la siguiente ronda sin borrar las victorias."""
        self.numero_ronda += 1
        self.tiempo = TIEMPO_RONDA
        self._reiniciar_ronda()

    #  Serialización para red


    def serializar(self, resultado=None) -> dict:
        return {
            "tipo": "estado",
            "victorias": self.victorias,
            "ronda": self.numero_ronda,
            "tiempo": self.tiempo,
            "ticks": self.ticks,
            "comidas": self.comidas,
            "venenos": self.venenos,
            "powerups": self.powerups,
            "muros": self.muros,
            "j1": self.serpientes[0].serializar(),
            "j2": self.serpientes[1].serializar(),
            "resultado": resultado,
        }

    def cargar_desde_red(self, datos: dict):
        """Aplica el estado recibido del host (modo cliente)."""
        self.victorias = datos["victorias"]
        self.numero_ronda = datos["ronda"]
        self.tiempo = datos["tiempo"]
        self.ticks = datos["ticks"]
        self.comidas = [tuple(c) for c in datos["comidas"]]
        self.venenos = [tuple(v) for v in datos["venenos"]]
        self.powerups = [(p[0], p[1], p[2]) for p in datos["powerups"]]
        self.muros = [tuple(m) for m in datos["muros"]]
        self.serpientes[0].cargar_desde_dict(datos["j1"])
        self.serpientes[1].cargar_desde_dict(datos["j2"])

#  CANVAS DE JUEGO — dibuja con QPainter

class CanvasJuego(QWidget):
    """
    Widget que dibuja el estado completo del juego frame a frame.
    Escala automáticamente al tamaño disponible del widget.
    No contiene lógica de juego — solo renderizado.
    """

    def __init__(self):
        super().__init__()
        self.estado = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(280, 200)
        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")
        self.setFocusPolicy(Qt.StrongFocus)

    def asignar_estado(self, estado: EstadoJuego):
        self.estado = estado
        self.update()

    def tamaño_celda(self) -> float:
        """Calcula el tamaño de celda para llenar el widget."""
        return min(self.width() / COLUMNAS, self.height() / FILAS)

    def desplazamiento(self, celda: float) -> tuple:
        """Calcula el offset para centrar el mapa en el widget."""
        ox = (self.width() - celda * COLUMNAS) / 2
        oy = (self.height() - celda * FILAS) / 2
        return ox, oy

    def paintEvent(self, _):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing, False)

        celda = self.tamaño_celda()
        ox, oy = self.desplazamiento(celda)

        self._dibujar_fondo(pintor, celda, ox, oy)

        if not self.estado:
            return

        e = self.estado

        # Muros (sin AA para look pixel-art)
        for col, fila in e.muros:
            self._dibujar_muro(pintor, col, fila, celda, ox, oy)

        # Comidas, venenos y power-ups (con AA para suavidad)
        pintor.setRenderHint(QPainter.Antialiasing, True)
        for col, fila in e.comidas:
            self._dibujar_comida(pintor, col, fila, celda, ox, oy)
        for col, fila in e.venenos:
            self._dibujar_veneno(pintor, col, fila, celda, ox, oy)
        for col, fila, tipo in e.powerups:
            self._dibujar_powerup(pintor, col, fila, tipo, celda, ox, oy)

        # Serpientes
        for s in e.serpientes:
            if s.viva:
                self._dibujar_serpiente(pintor, s, celda, ox, oy)

    # Helpers de coordenadas

    def _rect_celda(self, col, fila, celda, ox, oy,
                    margen_pct=0.06) -> QRectF:
        """Rectángulo de una celda con margen interior."""
        m = celda * margen_pct
        return QRectF(
            ox + col * celda + m,
            oy + fila * celda + m,
            celda - m * 2,
            celda - m * 2,
        )

    def _centro_celda(self, col, fila, celda, ox, oy) -> QPointF:
        return QPointF(
            ox + col * celda + celda / 2,
            oy + fila * celda + celda / 2,
        )

    # Dibujo del fondo



    def _dibujar_fondo(self, p, celda, ox, oy):
        # Fondo total negro
        p.fillRect(self.rect(), QColor("#0A0A0A"))
        # Zona del mapa ligeramente más clara
        p.fillRect(
            QRectF(ox, oy, celda * COLUMNAS, celda * FILAS),
            QColor("#0D0D0D")
        )
        # Cuadrícula sutil (estética pixel-art)
        lapiz = QPen(QColor(30, 25, 5, 30))
        lapiz.setWidth(1)
        p.setPen(lapiz)
        for col in range(COLUMNAS + 1):
            x = ox + col * celda
            p.drawLine(QPointF(x, oy), QPointF(x, oy + celda * FILAS))
        for fila in range(FILAS + 1):
            y = oy + fila * celda
            p.drawLine(QPointF(ox, y), QPointF(ox + celda * COLUMNAS, y))
        # Borde dorado del mapa
        p.setPen(QPen(QColor(DORADO), 2))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(ox + 1, oy + 1,
                          celda * COLUMNAS - 2, celda * FILAS - 2))

    # Dibujo de elementos del mapa

    def _dibujar_muro(self, p, col, fila, celda, ox, oy):
        r = QRectF(ox + col * celda, oy + fila * celda, celda, celda)
        p.fillRect(r, QColor("#1A1A08"))
        p.setPen(QPen(QColor("#404010"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(r.adjusted(0, 0, -1, -1))
        # Cruz pixelada para textura de muro
        mx = r.left() + celda / 2
        my = r.top() + celda / 2
        p.drawLine(QPointF(r.left(), my), QPointF(r.right(), my))
        p.drawLine(QPointF(mx, r.top()), QPointF(mx, r.bottom()))

    def _dibujar_comida(self, p, col, fila, celda, ox, oy):
        centro = self._centro_celda(col, fila, celda, ox, oy)
        radio = celda * 0.30
        # Halo rojo brillante
        halo = QRadialGradient(centro, radio + celda * 0.22)
        halo.setColorAt(0, QColor(204, 34, 34, 70))
        halo.setColorAt(1, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(centro, radio + celda * 0.22, radio + celda * 0.22)
        # Cuerpo de la manzana
        grad = QRadialGradient(
            centro.x() - radio * 0.3,
            centro.y() - radio * 0.3,
            radio * 1.2
        )
        grad.setColorAt(0.0, QColor("#FF6060"))
        grad.setColorAt(0.5, QColor("#CC2020"))
        grad.setColorAt(1.0, QColor("#881010"))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor("#440808"), max(1, int(celda * 0.05))))
        p.drawEllipse(centro, radio, radio)
        # Tallito verde
        p.setPen(QPen(QColor("#44AA22"), max(1, int(celda * 0.07))))
        p.drawLine(
            centro + QPointF(0, -radio),
            centro + QPointF(celda * 0.12, -radio - celda * 0.18)
        )

    def _dibujar_veneno(self, p, col, fila, celda, ox, oy):
        centro = self._centro_celda(col, fila, celda, ox, oy)
        radio = celda * 0.30
        grad = QRadialGradient(
            centro.x() - radio * 0.3,
            centro.y() - radio * 0.3,
            radio * 1.2
        )
        grad.setColorAt(0, QColor("#CC80FF"))
        grad.setColorAt(0.6, QColor("#7020CC"))
        grad.setColorAt(1, QColor("#300870"))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor("#200050"), 1))
        p.drawEllipse(centro, radio, radio)
        if celda >= 14:
            fuente = p.font()
            fuente.setPixelSize(max(8, int(celda * 0.44)))
            p.setFont(fuente)
            p.setPen(QColor("#FFFFFF"))
            p.drawText(
                QRectF(ox + col * celda, oy + fila * celda, celda, celda),
                Qt.AlignCenter, "☠"
            )

    def _dibujar_powerup(self, p, col, fila, tipo, celda, ox, oy):
        rect = self._rect_celda(col, fila, celda, ox, oy, 0.05)
        color = PU_COLOR[tipo]
        p.setPen(QPen(color, max(1, int(celda * 0.07))))
        p.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
        p.drawRect(rect)
        # Esquinas de píxel brillantes
        sz = max(2, int(celda * 0.12))
        for cx, cy in [
            (rect.left(), rect.top()),
            (rect.right() - sz, rect.top()),
            (rect.left(), rect.bottom() - sz),
            (rect.right() - sz, rect.bottom() - sz),
        ]:
            p.fillRect(QRectF(cx, cy, sz, sz), color)
        # Ícono del power-up
        if celda >= 14:
            fuente = p.font()
            fuente.setPixelSize(max(8, int(celda * 0.50)))
            p.setFont(fuente)
            p.setPen(color)
            p.drawText(rect, Qt.AlignCenter, PU_ICONO[tipo])

    #  Dibujo de serpientes

    def _dibujar_serpiente(self, p, s: Serpiente, celda, ox, oy):
        alpha = 65 if s.invisible else 255
        color_cabeza = QColor(s.color_cabeza)
        color_cabeza.setAlpha(alpha)
        color_cuerpo = QColor(s.color_cuerpo)
        color_cuerpo.setAlpha(alpha)

        # Cuerpo de la cola a la cabeza con degradado de opacidad
        for i in range(len(s.cuerpo) - 1, 0, -1):
            col, fila = s.cuerpo[i]
            factor_fade = max(0.30, 1 - i / len(s.cuerpo) * 0.70)
            color_seg = QColor(
                int(color_cuerpo.red() * factor_fade),
                int(color_cuerpo.green() * factor_fade),
                int(color_cuerpo.blue() * factor_fade),
                alpha,
            )
            margen = 0.07 + (i / len(s.cuerpo)) * 0.07
            rect = self._rect_celda(col, fila, celda, ox, oy, margen)
            color_borde = QColor(
                int(color_seg.red() * 0.5),
                int(color_seg.green() * 0.5),
                int(color_seg.blue() * 0.5),
                alpha,
            )
            p.setBrush(QBrush(color_seg))
            p.setPen(QPen(color_borde, max(1, int(celda * 0.04))))
            p.drawRect(rect)

        # Cabeza con degradado lineal
        col_h, fila_h = s.cuerpo[0]
        rect_cabeza = self._rect_celda(col_h, fila_h, celda, ox, oy, 0.04)
        grad_cabeza = QLinearGradient(
            rect_cabeza.topLeft(), rect_cabeza.bottomRight()
        )
        grad_cabeza.setColorAt(0, color_cabeza.lighter(150))
        grad_cabeza.setColorAt(1, color_cabeza)
        p.setBrush(QBrush(grad_cabeza))
        p.setPen(QPen(
            QColor(
                int(color_cabeza.red() * 0.4),
                int(color_cabeza.green() * 0.4),
                int(color_cabeza.blue() * 0.4),
                alpha,
            ),
            max(1, int(celda * 0.06))
        ))
        p.drawRect(rect_cabeza)

        # Ojos
        self._dibujar_ojos(p, col_h, fila_h, s.direccion, alpha, celda, ox, oy)

        # Indicador visual del Escudo (borde azul brillante)
        if s.escudado:
            p.setPen(QPen(QColor(96, 192, 255, 200), max(2, int(celda * 0.09))))
            p.setBrush(Qt.NoBrush)
            p.drawRect(rect_cabeza.adjusted(
                -celda * 0.10, -celda * 0.10,
                celda * 0.10, celda * 0.10
            ))

    def _dibujar_ojos(self, p, col, fila, direccion, alpha, celda, ox, oy):
        cx = ox + col * celda + celda / 2
        cy = oy + fila * celda + celda / 2
        dcol, dfila = direccion
        dist = celda * 0.17  # distancia del ojo al centro

        if dcol == 1:
            ojo1, ojo2 = (cx + dist, cy - dist), (cx + dist, cy + dist)
        elif dcol == -1:
            ojo1, ojo2 = (cx - dist, cy - dist), (cx - dist, cy + dist)
        elif dfila == -1:
            ojo1, ojo2 = (cx - dist, cy - dist), (cx + dist, cy - dist)
        else:
            ojo1, ojo2 = (cx - dist, cy + dist), (cx + dist, cy + dist)

        radio_blanco = max(2.0, celda * 0.11)
        radio_pupila = max(1.0, celda * 0.055)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255, alpha)))
        for ex, ey in [ojo1, ojo2]:
            p.drawEllipse(QPointF(ex, ey), radio_blanco, radio_blanco)

        p.setBrush(QBrush(QColor(10, 10, 5, alpha)))
        for ex, ey in [ojo1, ojo2]:
            p.drawEllipse(
                QPointF(ex + dcol * radio_pupila, ey + dfila * radio_pupila),
                radio_pupila, radio_pupila
            )

#  OVERLAY DE MENSAJES

class OverlayMensaje(QWidget):
    """Capa semitransparente superpuesta con mensajes de ronda/ganador."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        self.lbl_titulo = QLabel("")
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

    def mostrar(self, titulo: str, subtitulo: str, color: str = DORADO):
        self.lbl_titulo.setText(titulo)
        self.lbl_titulo.setStyleSheet(
            f"color: {color}; background: transparent;"
        )
        self.lbl_subtitulo.setText(subtitulo)

#  WIDGETS DEL HUD
class PanelJugador(QWidget):
    """Panel del HUD para un jugador: nombre, puntos, victorias, power-up."""

    def __init__(self, color_acento: str, alinear_derecha: bool = False):
        super().__init__()
        self.color = color_acento
        self.alin_derecha = alinear_derecha
        self.setStyleSheet(f"background-color: {FONDO_MEDIO}; border-radius: 8px;")
        self.setMinimumWidth(160)
        self.setMaximumHeight(90)
        self._construir()

    def _construir(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 5, 8, 5)
        lay.setSpacing(2)

        self.lbl_nombre = QLabel("JUGADOR")
        self.lbl_nombre.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_nombre.setStyleSheet(f"color: {self.color}; background: transparent;")
        self.lbl_nombre.setAlignment(Qt.AlignCenter)

        self.lbl_puntos = QLabel("0 pts | 🐍 4")
        self.lbl_puntos.setFont(QFont("Segoe UI", 9))
        self.lbl_puntos.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent;")
        self.lbl_puntos.setAlignment(Qt.AlignCenter)

        self.lbl_victorias = QLabel("○ ○ ○")
        self.lbl_victorias.setFont(QFont("Segoe UI", 11))
        self.lbl_victorias.setAlignment(Qt.AlignCenter)

        self.lbl_powerup = QLabel("— sin power-up")
        self.lbl_powerup.setFont(QFont("Segoe UI", 8))
        self.lbl_powerup.setStyleSheet(f"color: {GRIS}; background: transparent;")
        self.lbl_powerup.setAlignment(Qt.AlignCenter)

        lay.addWidget(self.lbl_nombre)
        lay.addWidget(self.lbl_puntos)
        lay.addWidget(self.lbl_victorias)
        lay.addWidget(self.lbl_powerup)

    def actualizar(self, nombre, puntos, longitud, victorias,
                   pu_guardado, pu_activo, pu_ticks):
        self.lbl_nombre.setText(nombre.upper()[:14])
        self.lbl_puntos.setText(f"{puntos} pts | 🐍 {longitud}")

        # Victorias usando texto plano sin HTML
        texto_victorias = ""
        for i in range(RONDAS_MAX):
            if i < victorias:
                texto_victorias += "● "
            else:
                texto_victorias += "○ "
        self.lbl_victorias.setText(texto_victorias.strip())
        self.lbl_victorias.setStyleSheet(f"color: {self.color}; background: transparent;")

        # Estado del power-up
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
        estilo_orig = self.lbl_powerup.styleSheet()
        self.lbl_powerup.setStyleSheet(f"color: {ROJO}; background: transparent; font-weight: bold;")
        self.lbl_powerup.setText("✗ SIN POWER-UP")
        QTimer.singleShot(400, lambda: self.lbl_powerup.setStyleSheet(estilo_orig))


class PanelCentral(QWidget):
    """Panel central del HUD: ronda y temporizador."""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(130)
        self.setStyleSheet(f"""
            background-color: {FONDO_MEDIO};
            border-radius: 10px;
            border: 2px solid {DORADO};
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(5, 8, 5, 8)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignCenter)

        self.lbl_ronda = QLabel("RONDA 1")
        self.lbl_tiempo = QLabel("90")

        self.lbl_ronda.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_tiempo.setFont(QFont("Segoe UI", 28, QFont.Bold))

        self.lbl_ronda.setStyleSheet(f"color: {DORADO}; background: transparent;")
        self.lbl_tiempo.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent;")

        self.lbl_ronda.setAlignment(Qt.AlignCenter)
        self.lbl_tiempo.setAlignment(Qt.AlignCenter)

        lay.addWidget(self.lbl_ronda)
        lay.addWidget(self.lbl_tiempo)

    def actualizar(self, numero_ronda: int, segundos: int):
        self.lbl_ronda.setText(f"RONDA {numero_ronda}")
        self.lbl_tiempo.setText(str(max(0, segundos)))

        if segundos <= 10:
            self.lbl_tiempo.setStyleSheet(f"color: {ROJO}; background: transparent; font-weight: bold;")
        elif segundos <= 30:
            self.lbl_tiempo.setStyleSheet(f"color: {NARANJA}; background: transparent;")
        else:
            self.lbl_tiempo.setStyleSheet(f"color: {BLANCO_CALIDO}; background: transparent;")

class PanelCentral(QWidget):
    """Panel central del HUD: ronda y temporizador."""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(120)
        self.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignCenter)

        self.lbl_ronda = QLabel("RONDA 1")
        self.lbl_tiempo = QLabel("90")
        self.lbl_ronda.setFont(QFont("Segoe UI", 9))
        self.lbl_tiempo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.lbl_ronda.setStyleSheet(f"color: {GRIS}; background: transparent;")
        self.lbl_tiempo.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent;"
        )
        for w in [self.lbl_ronda, self.lbl_tiempo]:
            w.setAlignment(Qt.AlignCenter)
            lay.addWidget(w)

    def actualizar(self, numero_ronda: int, segundos: int):
        self.lbl_ronda.setText(f"RONDA {numero_ronda}")
        self.lbl_tiempo.setText(str(max(0, segundos)))
        color = ROJO if segundos <= 10 else BLANCO_CALIDO
        self.lbl_tiempo.setStyleSheet(f"color: {color}; background: transparent;")

#  PANTALLA DE JUEGO COMPLETA

class PantallaJuego(QWidget):
    """
    Pantalla completa del juego con HUD y canvas.
    Recibe los nombres de los jugadores desde PantallaConfiguracion.
    """

    def __init__(self, ventana_principal=None,
                 nombre_j1: str = "Jugador 1",
                 nombre_j2: str = "Jugador 2",
                 ip_red: str = "",
                 modo_red: str = "local",
                 color_j1: tuple = None,
                 color_j2: tuple = None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal
        self.nombre_j1 = nombre_j1
        self.nombre_j2 = nombre_j2
        self.ip_red = ip_red
        self.modo_red = modo_red

        # Usar colores elegidos en configuración o los predeterminados
        c_j1 = color_j1 if color_j1 else COLORES_J1[0]
        c_j2 = color_j2 if color_j2 else COLORES_J2[0]

        self.estado = EstadoJuego(
            colores_j1=c_j1,
            colores_j2=c_j2,
            nombres=[nombre_j1, nombre_j2],
        )

        # Timers: uno para la lógica, otro para el tiempo de ronda
        self.timer_juego = QTimer(self)
        self.timer_segundo = QTimer(self)
        self.timer_juego.timeout.connect(self._tick_juego)
        self.timer_segundo.timeout.connect(self._tick_segundo)

        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")
        self._construir_interfaz()



    # Construcción de la interfaz



    def _construir_interfaz(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        raiz.addWidget(self._crear_hud_superior())
        self.canvas = CanvasJuego()
        self.canvas.asignar_estado(self.estado)
        raiz.addWidget(self.canvas, stretch=1)
        raiz.addWidget(self._crear_barra_inferior())

        # Overlay (superpuesto sobre todo el widget)
        self.overlay = OverlayMensaje(self)
        self.overlay.hide()

        # Mostrar mensaje de inicio y comenzar
        self._mostrar_overlay(
            f"RONDA {self.estado.numero_ronda}", "¡Prepárense!", DORADO
        )
        QTimer.singleShot(1800, self._iniciar_ronda)

    def _crear_hud_superior(self) -> QWidget:
        panel = QWidget()
        panel.setFixedHeight(100)
        panel.setStyleSheet(f"""
            background-color: {FONDO_MEDIO};
            border-bottom: 3px solid {DORADO};
        """)
        lay = QHBoxLayout(panel)
        lay.setContentsMargins(15, 5, 15, 5)
        lay.setSpacing(15)

        self.panel_j1 = PanelJugador(VERDE, alinear_derecha=False)
        self.panel_cen = PanelCentral()
        self.panel_j2 = PanelJugador(AZUL, alinear_derecha=True)

        lay.addStretch()
        lay.addWidget(self.panel_j1)
        lay.addStretch()
        lay.addWidget(self.panel_cen)
        lay.addStretch()
        lay.addWidget(self.panel_j2)
        lay.addStretch()

        return panel

    def _sep_vertical(self) -> QFrame:
        linea = QFrame()
        linea.setFrameShape(QFrame.VLine)
        linea.setStyleSheet(
            f"color: {BORDE_ACTIVO}; background: {BORDE_ACTIVO};"
            f"max-width: 1px; margin: 8px 6px;"
        )
        return linea

    def _crear_barra_inferior(self) -> QWidget:
        barra = QWidget()
        barra.setFixedHeight(34)
        barra.setStyleSheet(
            f"background-color: {FONDO_MEDIO}; border-top: 2px solid {DORADO};"
        )
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(16, 0, 16, 0)
        texto = QLabel(
            f"J1: {self.nombre_j1}  WASD+Q   │   J2: {self.nombre_j2}  ↑↓←→+/"
        )
        texto.setFont(QFont("Consolas", 9))
        texto.setStyleSheet(f"color: {GRIS}; background: transparent;")
        texto.setAlignment(Qt.AlignCenter)
        lay.addStretch()
        lay.addWidget(texto)
        lay.addStretch()
        return barra

    # Lógica del juego

    def _iniciar_ronda(self):
        self._ocultar_overlay()
        self.timer_juego.start(VELOCIDAD)
        self.timer_segundo.start(1000)
        self.canvas.setFocus()

    def _tick_juego(self):
        resultado = self.estado.tick()
        self.canvas.update()
        self._actualizar_hud()
        if resultado is not None:
            self.timer_juego.stop()
            self.timer_segundo.stop()
            self._fin_ronda(resultado)

    def _tick_segundo(self):
        # El tiempo se maneja dentro de tick() ahora
        self._actualizar_hud()

    def _actualizar_hud(self):
        j0, j1 = self.estado.serpientes
        self.panel_j1.actualizar(
            j0.nombre, j0.puntos, len(j0.cuerpo),
            self.estado.victorias[0],
            j0.pu_guardado, j0.pu_activo, j0.pu_ticks,
        )
        self.panel_j2.actualizar(
            j1.nombre, j1.puntos, len(j1.cuerpo),
            self.estado.victorias[1],
            j1.pu_guardado, j1.pu_activo, j1.pu_ticks,
        )
        self.panel_cen.actualizar(self.estado.numero_ronda, self.estado.tiempo)

    def _fin_ronda(self, ganador: int):
        if ganador == -1:
            mensaje, color = "¡EMPATE!", DORADO
        else:
            nombre = self.estado.serpientes[ganador].nombre
            color = VERDE if ganador == 0 else AZUL
            self.estado.victorias[ganador] += 1
            mensaje = f"🏆 {nombre} gana la ronda"

        self._mostrar_overlay(mensaje, "", color)

        if max(self.estado.victorias) >= RONDAS_MAX:
            QTimer.singleShot(2200, self._fin_partida)
        else:
            self.estado.siguiente_ronda()
            QTimer.singleShot(2200, lambda: (
                self._mostrar_overlay(
                    f"RONDA {self.estado.numero_ronda}",
                    "¡Prepárense!", DORADO
                ),
                QTimer.singleShot(1800, self._iniciar_ronda),
            ))

    def _fin_partida(self):
        self._ocultar_overlay()
        ganador = 0 if self.estado.victorias[0] > self.estado.victorias[1] else 1
        nombre = self.estado.serpientes[ganador].nombre
        puntos = [self.estado.serpientes[i].puntos for i in range(2)]
        self._guardar_resultado(nombre, puntos[ganador])

        musica.iniciar()
        from pantalla.resultado import PantallaResultado
        self.ventana.setCentralWidget(
            PantallaResultado(
                self.ventana,
                nombre_ganador=nombre,
                victorias=self.estado.victorias,
                puntos=puntos,
                nombres=self.estado.nombres,
            )
        )

    def _guardar_resultado(self, nombre_ganador: str, puntos_ganador: int):
        """Guarda el resultado en puntuaciones.json."""
        ruta = "puntuaciones.json"
        lista = []
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    lista = json.load(f)
            except Exception:
                lista = []
        lista.insert(0, {
            "nombre": nombre_ganador,
            "puntos": puntos_ganador,
            "rondas": f"{self.estado.victorias[0]}-{self.estado.victorias[1]}",
            "fecha": datetime.now().strftime("%d/%m/%Y"),
        })
        lista = lista[:50]
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # Overlay

    def _mostrar_overlay(self, titulo: str, subtitulo: str, color: str):
        self.overlay.mostrar(titulo, subtitulo, color)
        self.overlay.setGeometry(self.rect())
        self.overlay.show()
        self.overlay.raise_()

    def _ocultar_overlay(self):
        self.overlay.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.overlay.setGeometry(self.rect())

    #  Teclado

    def keyPressEvent(self, e):
        if not self.estado:
            return
        j0, j1 = self.estado.serpientes
        tecla = e.key()

        # Jugador 1 — WASD + Q
        if tecla == Qt.Key_W:
            j0.cambiar_direccion(0, -1)
        elif tecla == Qt.Key_S:
            j0.cambiar_direccion(0, 1)
        elif tecla == Qt.Key_A:
            j0.cambiar_direccion(-1, 0)
        elif tecla == Qt.Key_D:
            j0.cambiar_direccion(1, 0)
        elif tecla == Qt.Key_Q:
            if not self.estado.usar_powerup(0):
                self.panel_j1.parpadear_sin_powerup()

        # Jugador 2 — Flechas + teclas alternativas para teclado español
        elif tecla == Qt.Key_Up:
            j1.cambiar_direccion(0, -1)
        elif tecla == Qt.Key_Down:
            j1.cambiar_direccion(0, 1)
        elif tecla == Qt.Key_Left:
            j1.cambiar_direccion(-1, 0)
        elif tecla == Qt.Key_Right:
            j1.cambiar_direccion(1, 0)
        elif tecla in (Qt.Key_Slash, Qt.Key_Minus, Qt.Key_Period,
                       Qt.Key_0, Qt.Key_Insert, Qt.Key_End,
                       Qt.Key_PageDown, Qt.Key_Delete):
            if not self.estado.usar_powerup(1):
                self.panel_j2.parpadear_sin_powerup()

        elif tecla == Qt.Key_Escape:
            self.timer_juego.stop()
            self.timer_segundo.stop()
            musica.iniciar()
            from pantalla.inicio import PantallaInicio
            self.ventana.setCentralWidget(PantallaInicio(self.ventana))