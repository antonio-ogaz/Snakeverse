"""
pantalla/juego.py — Pantalla principal del juego SNAKEVERSE  # Docstring del archivo

Contiene toda la lógica del juego:  # Explica el contenido
  - Clase Serpiente: movimiento, colisiones, power-ups  # Clase de serpiente
  - Clase EstadoJuego: mapa, rondas, spawns  # Clase del estado del juego
  - CanvasJuego: dibuja todo con QPainter  # Clase del canvas
  - PantallaJuego: HUD + canvas + teclado  # Clase principal
"""

import random  # Importa funciones aleatorias
import json  # Importa manejo de JSON
import os  # Importa utilidades del sistema operativo
from datetime import datetime  # Importa fecha y hora

from PySide6.QtWidgets import (  # Importa widgets de Qt
    QWidget, QVBoxLayout, QHBoxLayout,  # Widgets y layouts
    QLabel, QPushButton, QFrame, QSizePolicy,  # Widgets visuales
)
from PySide6.QtGui import (  # Importa clases gráficas
    QPainter, QColor, QFont, QBrush, QPen,  # Herramientas de dibujo
    QLinearGradient, QRadialGradient,  # Gradientes
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF  # Importa clases del núcleo Qt

from utilidad.musica import musica  # Importa controlador de música
from utilidad.estilos import (  # Importa colores y estilos
    DORADO, DORADO_CLARO, VERDE, VERDE_OSCURO,  # Colores verdes y dorados
    AZUL, AZUL_OSCURO, ROJO, NARANJA, MORADO,  # Otros colores
    BLANCO_CALIDO, GRIS,  # Colores neutros
    FONDO_OSCURO, FONDO_MEDIO, BORDE_ACTIVO,  # Colores de fondo
    estilo_ventana,  # Estilo de ventana
)

#  CONSTANTES DEL MAPA Y PARTIDA  # Sección de constantes

COLUMNAS = 28  # Número de columnas del mapa
FILAS = 20  # Número de filas del mapa
RONDAS_MAX = 3  # Rondas necesarias para ganar
TIEMPO_RONDA = 90  # Tiempo máximo de ronda
VELOCIDAD = 135  # Velocidad del juego en milisegundos
COMIDAS = 4  # Cantidad de comidas simultáneas

# ── Identificadores de power-ups ──────────────────────────────  # Sección de power-ups
PU_CAMUFLAJE = "camuflaje"  # Power-up de invisibilidad
PU_TURBO = "turbo"  # Power-up de velocidad
PU_ESCUDO = "escudo"  # Power-up de protección
PU_CORTE = "corte"  # Power-up que corta cola rival

LISTA_POWERUPS = [PU_CAMUFLAJE, PU_TURBO, PU_ESCUDO, PU_CORTE]  # Lista de power-ups

PU_ICONO = {  # Diccionario de íconos
    PU_CAMUFLAJE: "👁",  # Ícono de camuflaje
    PU_TURBO: "⚡",  # Ícono de turbo
    PU_ESCUDO: "🛡",  # Ícono de escudo
    PU_CORTE: "✂",  # Ícono de corte
}
PU_NOMBRE = {  # Diccionario de nombres
    PU_CAMUFLAJE: "Camuflaje",  # Nombre de camuflaje
    PU_TURBO: "Turbo",  # Nombre de turbo
    PU_ESCUDO: "Escudo",  # Nombre de escudo
    PU_CORTE: "Corte",  # Nombre de corte
}
PU_DURACION = {  # Duraciones de efectos
    PU_CAMUFLAJE: 28,  # Duración de camuflaje
    PU_TURBO: 22,  # Duración de turbo
    PU_ESCUDO: 16,  # Duración de escudo
    PU_CORTE: 0,  # Corte es instantáneo
}
PU_COLOR = {  # Colores de cada power-up
    PU_CAMUFLAJE: QColor("#9060FF"),  # Color morado
    PU_TURBO: QColor("#FFD040"),  # Color amarillo
    PU_ESCUDO: QColor("#40C0FF"),  # Color azul
    PU_CORTE: QColor("#FF6060"),  # Color rojo
}

# Colores disponibles para las serpientes  # Colores jugador 1
COLORES_J1 = [
    ("#2ECC40", "#1A8C28"),  # Verde vibrante
    ("#40FF60", "#20B040"),  # Verde neón
    ("#FFD040", "#C09010"),  # Dorado
    ("#80FF40", "#40B020"),  # Verde lima
]

COLORES_J2 = [  # Colores jugador 2
    ("#209AE8", "#1464A8"),  # Azul eléctrico
    ("#40B8FF", "#1880D0"),  # Azul cielo
    ("#E03060", "#A01040"),  # Rojo vibrante
    ("#E8C020", "#A08010"),  # Amarillo
]

#  CLASE SERPIENTE  # Inicio clase Serpiente

class Serpiente:  # Clase que representa una serpiente
    """
    Representa una serpiente en el juego.  # Explicación de la clase
    """

    def __init__(self, col_inicio: int, fila_inicio: int,  # Constructor
                 direccion: tuple, colores: tuple, nombre: str):

        self.cuerpo = [  # Genera cuerpo inicial
            (col_inicio - direccion[0] * i,  # Calcula columna
             fila_inicio - direccion[1] * i)  # Calcula fila
            for i in range(4)  # Crea 4 segmentos
        ]

        self.direccion = direccion  # Dirección actual
        self.dir_siguiente = direccion  # Próxima dirección
        self.color_cabeza = QColor(colores[0])  # Color cabeza
        self.color_cuerpo = QColor(colores[1])  # Color cuerpo
        self.nombre = nombre  # Nombre del jugador

        # Estado  # Variables de estado
        self.viva = True  # Indica si sigue viva
        self.puntos = 0  # Puntos acumulados

        # Power-up  # Variables de power-up
        self.pu_guardado = None  # Power-up almacenado
        self.pu_activo = None  # Power-up activo
        self.pu_ticks = 0  # Tiempo restante del power-up
        self.invisible = False  # Estado invisible
        self.escudado = False  # Estado con escudo
        self.turbo = False  # Estado turbo
        self.invertida = False  # Controles invertidos
        self.ticks_invertida = 0  # Tiempo de inversión

    def cabeza(self) -> tuple:  # Retorna cabeza
        """Retorna la posición (col, fila) de la cabeza."""  # Docstring
        return self.cuerpo[0]  # Devuelve cabeza

    def cambiar_direccion(self, dcol: int, dfila: int):  # Cambia dirección
        """
        Solicita un cambio de dirección.  # Explica función
        """
        if self.invertida:  # Si controles invertidos
            dcol, dfila = -dcol, -dfila  # Invierte dirección

        if (dcol, dfila) != (-self.direccion[0], -self.direccion[1]):  # Evita giro 180°
            self.dir_siguiente = (dcol, dfila)  # Guarda nueva dirección

    def avanzar(self, crecer: bool = False):  # Mueve serpiente
        """
        Mueve la serpiente un paso.  # Explica método
        """
        self.direccion = self.dir_siguiente  # Actualiza dirección
        col, fila = self.cuerpo[0]  # Obtiene cabeza actual

        nueva_cabeza = (  # Calcula nueva cabeza
            col + self.direccion[0],  # Nueva columna
            fila + self.direccion[1]  # Nueva fila
        )

        self.cuerpo.insert(0, nueva_cabeza)  # Inserta nueva cabeza

        if not crecer:  # Si no debe crecer
            self.cuerpo.pop()  # Elimina cola

    def sacar_powerup(self) -> str | None:  # Extrae power-up
        """
        Extrae el power-up del inventario.  # Explicación
        """
        if self.pu_guardado:  # Si tiene power-up
            tipo = self.pu_guardado  # Guarda tipo
            self.pu_guardado = None  # Vacía inventario
            return tipo  # Retorna power-up

        return None  # No había power-up

    def activar_powerup(self, tipo: str, rival: "Serpiente"):  # Activa power-up
        """
        Aplica el efecto del power-up.  # Explica función
        """

        if tipo == PU_CAMUFLAJE:  # Si es camuflaje
            self.pu_activo = tipo  # Activa efecto
            self.pu_ticks = PU_DURACION[tipo]  # Asigna duración
            self.invisible = True  # Activa invisibilidad

        elif tipo == PU_TURBO:  # Si es turbo
            self.pu_activo = tipo  # Activa turbo
            self.pu_ticks = PU_DURACION[tipo]  # Duración
            self.turbo = True  # Activa turbo

        elif tipo == PU_ESCUDO:  # Si es escudo
            self.pu_activo = tipo  # Activa escudo
            self.pu_ticks = PU_DURACION[tipo]  # Duración
            self.escudado = True  # Activa protección

        elif tipo == PU_CORTE:  # Si es corte
            if len(rival.cuerpo) > 5:  # Si rival tiene cola suficiente
                corte = max(2, len(rival.cuerpo) // 3)  # Calcula corte
                rival.cuerpo = rival.cuerpo[:-corte]  # Reduce cola

    def actualizar_efectos(self):  # Actualiza efectos activos
        """
        Descuenta un tick de los efectos activos.  # Explicación
        """

        if self.ticks_invertida > 0:  # Si sigue invertida
            self.ticks_invertida -= 1  # Reduce tiempo

            if self.ticks_invertida == 0:  # Si terminó el efecto
                self.invertida = False  # Desactiva inversión

        if self.pu_activo is not None:  # Si hay power-up activo
            duracion = PU_DURACION.get(self.pu_activo, 0)  # Obtiene duración

            if duracion > 0:  # Si tiene duración válida
                self.pu_ticks -= 1  # Reduce ticks

                if self.pu_ticks <= 0:  # Si terminó el efecto
                    self._desactivar_powerup()  # Lo desactiva

    def _desactivar_powerup(self):  # Desactiva power-up
        """Quita el efecto del power-up activo."""  # Explicación

        if self.pu_activo == PU_CAMUFLAJE:  # Si es camuflaje
            self.invisible = False  # Desactiva invisibilidad

        elif self.pu_activo == PU_TURBO:  # Si es turbo
            self.turbo = False  # Desactiva turbo

        elif self.pu_activo == PU_ESCUDO:  # Si es escudo
            self.escudado = False  # Desactiva escudo

        self.pu_activo = None  # Limpia power-up activo
        self.pu_ticks = 0  # Reinicia contador

    # ── Serialización para envío por red ─────────────────────  # Sección de red

    def serializar(self) -> dict:  # Convierte datos a diccionario
        return {
            "cuerpo": self.cuerpo,  # Guarda cuerpo
            "direccion": list(self.direccion),  # Guarda dirección
            "dir_siguiente": list(self.dir_siguiente),  # Guarda próxima dirección
            "viva": self.viva,  # Guarda estado viva
            "puntos": self.puntos,  # Guarda puntos
            "nombre": self.nombre,  # Guarda nombre
            "pu_guardado": self.pu_guardado,  # Guarda power-up guardado
            "pu_activo": self.pu_activo,  # Guarda power-up activo
            "pu_ticks": self.pu_ticks,  # Guarda ticks del power-up
            "invisible": self.invisible,  # Guarda invisibilidad
            "escudado": self.escudado,  # Guarda escudo
            "turbo": self.turbo,  # Guarda turbo
            "invertida": self.invertida,  # Guarda inversión
            "ticks_invertida": self.ticks_invertida,  # Guarda tiempo invertido
        }

    def cargar_desde_dict(self, datos: dict):  # Carga datos recibidos
        self.cuerpo = [tuple(p) for p in datos["cuerpo"]]  # Reconstruye cuerpo
        self.direccion = tuple(datos["direccion"])  # Recupera dirección
        self.dir_siguiente = tuple(datos["dir_siguiente"])  # Recupera próxima dirección
        self.viva = datos["viva"]  # Recupera estado viva
        self.puntos = datos["puntos"]  # Recupera puntos
        self.nombre = datos["nombre"]  # Recupera nombre
        self.pu_guardado = datos["pu_guardado"]  # Recupera power-up guardado
        self.pu_activo = datos["pu_activo"]  # Recupera power-up activo
        self.pu_ticks = datos["pu_ticks"]  # Recupera ticks
        self.invisible = datos["invisible"]  # Recupera invisibilidad
        self.escudado = datos["escudado"]  # Recupera escudo
        self.turbo = datos["turbo"]  # Recupera turbo
        self.invertida = datos["invertida"]  # Recupera inversión
        self.ticks_invertida = datos["ticks_invertida"]  # Recupera tiempo invertido

#  ESTADO DEL JUEGO  # Inicio de EstadoJuego

class EstadoJuego:  # Clase que maneja lógica principal
    """
    Contiene toda la lógica de la partida.  # Explicación
    """

    def __init__(self, colores_j1: tuple, colores_j2: tuple, nombres: list):  # Constructor
        self.colores_j1 = colores_j1  # Guarda colores jugador 1
        self.colores_j2 = colores_j2  # Guarda colores jugador 2
        self.nombres = nombres  # Guarda nombres
        self.victorias = [0, 0]  # Contador de victorias
        self.numero_ronda = 1  # Ronda inicial
        self._reiniciar_ronda()  # Inicia primera ronda

    def _reiniciar_ronda(self):  # Reinicia mapa
        """Reinicia el mapa para una nueva ronda."""  # Explicación

        fila_centro = FILAS // 2  # Calcula fila central

        self.serpientes = [  # Crea serpientes
            Serpiente(  # Jugador 1
                6,  # Columna inicial
                fila_centro,  # Fila inicial
                (1, 0),  # Dirección derecha
                self.colores_j1,  # Colores jugador 1
                self.nombres[0],  # Nombre jugador 1
            ),

            Serpiente(  # Jugador 2
                COLUMNAS - 7,  # Columna inicial
                fila_centro,  # Fila inicial
                (-1, 0),  # Dirección izquierda
                self.colores_j2,  # Colores jugador 2
                self.nombres[1],  # Nombre jugador 2
            ),
        ]

        self.comidas = []  # Lista de comidas
        self.venenos = []  # Lista de venenos
        self.powerups = []  # Lista de power-ups
        self.muros = []  # Lista de muros
        self.tiempo = TIEMPO_RONDA  # Reinicia tiempo
        self.ticks = 0  # Reinicia ticks

        self._generar_comidas(COMIDAS)  # Genera comidas
        self._generar_venenos(1)  # Genera veneno
        self._generar_muros(max(0, self.numero_ronda - 1) * 3)  # Genera muros
        self._generar_powerups(2)  # Genera power-ups

    # Generación de elementos  # Sección generación

    def _celdas_ocupadas(self) -> set:  # Obtiene celdas usadas
        """Retorna el conjunto de celdas ya usadas."""  # Explicación

        ocupadas = set()  # Crea conjunto vacío

        for s in self.serpientes:  # Recorre serpientes
            ocupadas.update(s.cuerpo)  # Agrega cuerpo

        ocupadas.update(self.comidas)  # Agrega comidas
        ocupadas.update(self.venenos)  # Agrega venenos
        ocupadas.update((col, fila) for col, fila, _ in self.powerups)  # Agrega power-ups
        ocupadas.update(self.muros)  # Agrega muros

        return ocupadas  # Devuelve conjunto

    def _celda_libre(self):  # Busca celda vacía
        """Devuelve una celda aleatoria que no esté ocupada."""  # Explicación

        ocupadas = self._celdas_ocupadas()  # Obtiene ocupadas

        for _ in range(600):  # Intenta 600 veces
            col = random.randint(2, COLUMNAS - 3)  # Columna aleatoria
            fila = random.randint(2, FILAS - 3)  # Fila aleatoria

            if (col, fila) not in ocupadas:  # Si está libre
                return (col, fila)  # Retorna posición

        return None  # No encontró celda

    def _generar_comidas(self, cantidad: int):  # Genera comidas
        for _ in range(cantidad):  # Repite cantidad
            celda = self._celda_libre()  # Busca celda libre

            if celda:  # Si encontró celda
                self.comidas.append(celda)  # Agrega comida

    def _generar_venenos(self, cantidad: int):  # Genera venenos
        for _ in range(cantidad):  # Repite cantidad
            celda = self._celda_libre()  # Busca celda

            if celda:  # Si encontró celda
                self.venenos.append(celda)  # Agrega veneno

    def _generar_muros(self, cantidad: int):  # Genera muros
        for _ in range(cantidad):  # Repite cantidad
            celda = self._celda_libre()  # Busca celda

            if celda:  # Si encontró celda
                self.muros.append(celda)  # Agrega muro

    def _generar_powerups(self, cantidad: int = 1):  # Genera power-ups
        for _ in range(cantidad):  # Repite cantidad
            celda = self._celda_libre()  # Busca celda

            if celda:  # Si encontró celda
                tipo = random.choice(LISTA_POWERUPS)  # Elige power-up aleatorio
                self.powerups.append((celda[0], celda[1], tipo))  # Agrega power-up

    def _spawn_aleatorio(self):  # Genera elementos dinámicamente
        """Genera elementos aleatoriamente."""  # Explicación

        if len(self.powerups) < 2 and random.random() < 0.30:  # Si hay pocos power-ups
            self._generar_powerups(1)  # Genera uno

        elif len(self.powerups) < 3 and random.random() < 0.03:  # Si hay menos de 3
            self._generar_powerups(1)  # Genera uno

        if len(self.comidas) < COMIDAS and random.random() < 0.25:  # Si faltan comidas
            self._generar_comidas(1)  # Genera comida

        limite_muros = (self.numero_ronda - 1) * 3 + self.ticks // 180  # Calcula límite

        if len(self.muros) < limite_muros and random.random() < 0.02:  # Si puede generar muro
            celda = self._celda_libre()  # Busca celda

            if celda:  # Si encontró espacio
                self.muros.append(celda)  # Agrega muro 

    # Tick principal  # Sección principal de lógica

    def tick(self):  # Ejecuta lógica de un tick
        """
        Ejecuta un paso de la lógica del juego.  # Explicación
        """

        self.ticks += 1  # Incrementa contador de ticks
        self._spawn_aleatorio()  # Genera elementos aleatorios

        for idx in range(2):  # Recorre serpientes
            if self.serpientes[idx].viva:  # Si está viva
                self._mover(idx)  # Mueve serpiente

        for idx in range(2):  # Recorre serpientes
            if self.serpientes[idx].viva and self.serpientes[idx].turbo:  # Si tiene turbo
                self._mover_turbo(idx)  # Movimiento extra

        for s in self.serpientes:  # Recorre serpientes
            s.actualizar_efectos()  # Actualiza efectos

        if self.ticks % 10 == 0:  # Aproximadamente cada segundo
            self.tiempo = max(0, self.tiempo - 1)  # Reduce tiempo

        return self._revisar_fin_ronda()  # Revisa si terminó ronda

    def _mover(self, idx: int):  # Movimiento normal
        """
        Mueve la serpiente con colisiones.  # Explicación
        """

        serpiente = self.serpientes[idx]  # Obtiene serpiente
        rival = self.serpientes[1 - idx]  # Obtiene rival

        serpiente.avanzar()  # Avanza serpiente

        col, fila = serpiente.cabeza()  # Obtiene cabeza

        fuera_del_mapa = not (0 <= col < COLUMNAS and 0 <= fila < FILAS)  # Detecta borde

        if fuera_del_mapa:  # Si salió del mapa

            if serpiente.escudado:  # Si tiene escudo
                col = col % COLUMNAS  # Teletransporta columna
                fila = fila % FILAS  # Teletransporta fila
                serpiente.cuerpo[0] = (col, fila)  # Actualiza cabeza
                serpiente.escudado = False  # Consume escudo
                serpiente.pu_activo = None  # Limpia power-up

            else:  # Si no tiene escudo
                serpiente.viva = False  # Muere
                return  # Termina función

        if (col, fila) in self.muros:  # Si chocó con muro

            if serpiente.escudado:  # Si tiene escudo
                serpiente.cuerpo.pop(0)  # Retrocede
                serpiente.escudado = False  # Consume escudo
                serpiente.pu_activo = None  # Limpia power-up

            else:  # Sin escudo
                serpiente.viva = False  # Muere
                return  # Sale

        if (col, fila) in serpiente.cuerpo[1:]:  # Si chocó consigo misma

            if serpiente.escudado:  # Si tiene escudo
                serpiente.cuerpo.pop(0)  # Retrocede
                serpiente.escudado = False  # Consume escudo
                serpiente.pu_activo = None  # Limpia efecto

            else:  # Sin escudo
                serpiente.viva = False  # Muere
                return  # Sale

        if (col, fila) in rival.cuerpo:  # Si chocó con rival

            if serpiente.escudado:  # Si tiene escudo
                serpiente.cuerpo.pop(0)  # Retrocede
                serpiente.escudado = False  # Consume escudo
                serpiente.pu_activo = None  # Limpia efecto

            else:  # Sin escudo
                serpiente.viva = False  # Muere
                return  # Sale

        self._procesar_celda(serpiente, col, fila)  # Procesa contenido celda

    def _mover_turbo(self, idx: int):  # Movimiento extra turbo
        """
        Movimiento extra para turbo.  # Explicación
        """

        serpiente = self.serpientes[idx]  # Obtiene serpiente
        rival = self.serpientes[1 - idx]  # Obtiene rival

        pos_anterior = serpiente.cuerpo[0]  # Guarda posición anterior

        serpiente.avanzar()  # Avanza serpiente

        col, fila = serpiente.cabeza()  # Obtiene cabeza

        choca = (  # Verifica colisiones
            not (0 <= col < COLUMNAS and 0 <= fila < FILAS)  # Fuera del mapa
            or (col, fila) in self.muros  # Choca muro
            or (col, fila) in serpiente.cuerpo[1:]  # Choca consigo
            or (col, fila) in rival.cuerpo  # Choca rival
        )

        if choca:  # Si chocó
            serpiente.cuerpo.pop(0)  # Retrocede
            return  # Sale

        self._procesar_celda(serpiente, col, fila)  # Procesa celda

    def _procesar_celda(self, serpiente: Serpiente, col: int, fila: int):  # Procesa objetos
        """Gestiona comida, veneno y power-ups."""  # Explicación

        if (col, fila) in self.comidas:  # Si encontró comida
            self.comidas.remove((col, fila))  # Elimina comida
            serpiente.cuerpo.append(serpiente.cuerpo[-1])  # Hace crecer cola
            serpiente.puntos += 10  # Suma puntos

        if (col, fila) in self.venenos:  # Si encontró veneno
            self.venenos.remove((col, fila))  # Elimina veneno
            serpiente.invertida = True  # Invierte controles
            serpiente.ticks_invertida = 30  # Tiempo invertido
            self._generar_venenos(1)  # Repone veneno

        for pu in self.powerups[:]:  # Recorre power-ups
            if (col, fila) == (pu[0], pu[1]):  # Si coincide posición
                self.powerups.remove(pu)  # Elimina power-up

                if serpiente.pu_guardado is None:  # Si inventario vacío
                    serpiente.pu_guardado = pu[2]  # Guarda power-up

                break  # Sale del ciclo

    def usar_powerup(self, idx: int) -> bool:  # Usa power-up
        """
        Activa el power-up guardado.  # Explicación
        """

        serpiente = self.serpientes[idx]  # Obtiene serpiente
        rival = self.serpientes[1 - idx]  # Obtiene rival

        tipo = serpiente.sacar_powerup()  # Extrae power-up

        if tipo:  # Si había power-up
            serpiente.activar_powerup(tipo, rival)  # Activa efecto
            return True  # Indica éxito

        return False  # No había power-up

    # Condición de fin de ronda  # Sección fin de ronda

    def _revisar_fin_ronda(self):  # Revisa ganador
        """
        Comprueba si la ronda terminó.  # Explicación
        """

        j0, j1 = self.serpientes  # Obtiene serpientes

        if not j0.viva and not j1.viva:  # Si ambas murieron
            return 0 if len(j0.cuerpo) >= len(j1.cuerpo) else 1  # Gana más larga

        if not j0.viva:  # Si murió jugador 1
            return 1  # Gana jugador 2

        if not j1.viva:  # Si murió jugador 2
            return 0  # Gana jugador 1

        if self.tiempo <= 0:  # Si se acabó el tiempo

            if len(j0.cuerpo) > len(j1.cuerpo):  # Si jugador 1 es más largo
                return 0  # Gana jugador 1

            if len(j1.cuerpo) > len(j0.cuerpo):  # Si jugador 2 es más largo
                return 1  # Gana jugador 2

            return -1  # Empate

        return None  # La ronda continúa

    def siguiente_ronda(self):  # Inicia siguiente ronda
        """Prepara la siguiente ronda."""  # Explicación

        self.numero_ronda += 1  # Incrementa ronda
        self.tiempo = TIEMPO_RONDA  # Reinicia tiempo
        self._reiniciar_ronda()  # Reinicia mapa

    #  Serialización para red  # Sección red

    def serializar(self, resultado=None) -> dict:  # Serializa estado
        return {
            "tipo": "estado",  # Tipo de mensaje
            "victorias": self.victorias,  # Victorias
            "ronda": self.numero_ronda,  # Número de ronda
            "tiempo": self.tiempo,  # Tiempo restante
            "ticks": self.ticks,  # Cantidad de ticks
            "comidas": self.comidas,  # Lista de comidas
            "venenos": self.venenos,  # Lista de venenos
            "powerups": self.powerups,  # Lista de power-ups
            "muros": self.muros,  # Lista de muros
            "j1": self.serpientes[0].serializar(),  # Estado jugador 1
            "j2": self.serpientes[1].serializar(),  # Estado jugador 2
            "resultado": resultado,  # Resultado actual
        }

    def cargar_desde_red(self, datos: dict):  # Carga estado remoto
        """Aplica el estado recibido del host."""  # Explicación

        self.victorias = datos["victorias"]  # Carga victorias
        self.numero_ronda = datos["ronda"]  # Carga ronda
        self.tiempo = datos["tiempo"]  # Carga tiempo
        self.ticks = datos["ticks"]  # Carga ticks

        self.comidas = [tuple(c) for c in datos["comidas"]]  # Reconstruye comidas
        self.venenos = [tuple(v) for v in datos["venenos"]]  # Reconstruye venenos
        self.powerups = [(p[0], p[1], p[2]) for p in datos["powerups"]]  # Reconstruye power-ups
        self.muros = [tuple(m) for m in datos["muros"]]  # Reconstruye muros

        self.serpientes[0].cargar_desde_dict(datos["j1"])  # Carga jugador 1
        self.serpientes[1].cargar_desde_dict(datos["j2"])  # Carga jugador 2

#  CANVAS DE JUEGO — dibuja con QPainter  # Inicio CanvasJuego

class CanvasJuego(QWidget):  # Clase del canvas
    """
    Widget que dibuja el estado del juego.  # Explicación
    """

    def __init__(self):  # Constructor
        super().__init__()  # Inicializa QWidget

        self.estado = None  # Estado del juego

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Expande widget
        self.setMinimumSize(280, 200)  # Tamaño mínimo
        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")  # Fondo oscuro
        self.setFocusPolicy(Qt.StrongFocus)  # Permite recibir teclado

    def asignar_estado(self, estado: EstadoJuego):  # Asigna estado
        self.estado = estado  # Guarda estado
        self.update()  # Redibuja

    def tamaño_celda(self) -> float:  # Calcula tamaño de celda
        """Calcula tamaño de celda."""  # Explicación
        return min(self.width() / COLUMNAS, self.height() / FILAS)  # Retorna tamaño

    def desplazamiento(self, celda: float) -> tuple:  # Calcula offset
        """Calcula offset para centrar mapa."""  # Explicación

        ox = (self.width() - celda * COLUMNAS) / 2  # Offset horizontal
        oy = (self.height() - celda * FILAS) / 2  # Offset vertical

        return ox, oy  # Devuelve offsets

    def _crear_barra_inferior(self) -> QWidget:  # crea la barra inferior
        barra = QWidget()  # widget contenedor
        barra.setFixedHeight(34)  # altura fija de la barra
        barra.setStyleSheet(  # aplica estilos CSS
            f"background-color: {FONDO_MEDIO}; border-top: 2px solid {DORADO};"  # fondo y borde superior
        )
        lay = QHBoxLayout(barra)  # layout horizontal
        lay.setContentsMargins(16, 0, 16, 0)  # márgenes internos
        texto = QLabel(  # etiqueta de controles
            f"J1: {self.nombre_j1}  WASD+Q   │   J2: {self.nombre_j2}  ↑↓←→+/"  # texto mostrado
        )
        texto.setFont(QFont("Consolas", 9))  # fuente del texto
        texto.setStyleSheet(f"color: {GRIS}; background: transparent;")  # color y fondo
        texto.setAlignment(Qt.AlignCenter)  # alineación centrada
        lay.addStretch()  # espacio flexible izquierdo
        lay.addWidget(texto)  # agrega el texto
        lay.addStretch()  # espacio flexible derecho
        return barra  # retorna la barra

    # Lógica del juego

    def _iniciar_ronda(self):  # inicia la ronda
        self._ocultar_overlay()  # oculta overlay
        self.timer_juego.start(VELOCIDAD)  # inicia timer principal
        self.timer_segundo.start(1000)  # inicia timer de segundos
        self.canvas.setFocus()  # da foco al canvas

    def _tick_juego(self):  # tick principal del juego
        resultado = self.estado.tick()  # ejecuta lógica
        self.canvas.update()  # actualiza dibujo
        self._actualizar_hud()  # actualiza HUD
        if resultado is not None:  # si terminó ronda
            self.timer_juego.stop()  # detiene timer principal
            self.timer_segundo.stop()  # detiene timer secundario
            self._fin_ronda(resultado)  # procesa fin de ronda

    def _tick_segundo(self):  # tick de tiempo
        # El tiempo se maneja dentro de tick() ahora
        self._actualizar_hud()  # actualiza HUD

    def _actualizar_hud(self):  # actualiza paneles HUD
        j0, j1 = self.estado.serpientes  # obtiene serpientes
        self.panel_j1.actualizar(  # actualiza panel jugador 1
            j0.nombre, j0.puntos, len(j0.cuerpo),  # datos principales
            self.estado.victorias[0],  # victorias J1
            j0.pu_guardado, j0.pu_activo, j0.pu_ticks,  # powerups
        )
        self.panel_j2.actualizar(  # actualiza panel jugador 2
            j1.nombre, j1.puntos, len(j1.cuerpo),  # datos principales
            self.estado.victorias[1],  # victorias J2
            j1.pu_guardado, j1.pu_activo, j1.pu_ticks,  # powerups
        )
        self.panel_cen.actualizar(self.estado.numero_ronda, self.estado.tiempo)  # actualiza panel central

    def _fin_ronda(self, ganador: int):  # maneja final de ronda
        if ganador == -1:  # si empate
            mensaje, color = "¡EMPATE!", DORADO  # mensaje y color
        else:  # si hubo ganador
            nombre = self.estado.serpientes[ganador].nombre  # obtiene nombre
            color = VERDE if ganador == 0 else AZUL  # color según jugador
            self.estado.victorias[ganador] += 1  # suma victoria
            mensaje = f"🏆 {nombre} gana la ronda"  # mensaje ganador

        self._mostrar_overlay(mensaje, "", color)  # muestra overlay

        if max(self.estado.victorias) >= RONDAS_MAX:  # si alguien ganó partida
            QTimer.singleShot(2200, self._fin_partida)  # espera y finaliza
        else:  # si sigue partida
            self.estado.siguiente_ronda()  # inicia siguiente ronda
            QTimer.singleShot(2200, lambda: (  # espera antes de iniciar
                self._mostrar_overlay(  # muestra mensaje ronda
                    f"RONDA {self.estado.numero_ronda}",  # texto ronda
                    "¡Prepárense!", DORADO  # subtítulo y color
                ),
                QTimer.singleShot(1800, self._iniciar_ronda),  # inicia ronda
            ))

    def _fin_partida(self):  # finaliza partida
        self._ocultar_overlay()  # oculta overlay
        ganador = 0 if self.estado.victorias[0] > self.estado.victorias[1] else 1  # determina ganador
        nombre = self.estado.serpientes[ganador].nombre  # nombre ganador
        puntos = [self.estado.serpientes[i].puntos for i in range(2)]  # lista puntos
        self._guardar_resultado(nombre, puntos[ganador])  # guarda resultado

        musica.iniciar()  # reproduce música
        from pantalla.resultado import PantallaResultado  # importa pantalla resultado
        self.ventana.setCentralWidget(  # cambia pantalla
            PantallaResultado(  # crea pantalla resultado
                self.ventana,  # ventana principal
                nombre_ganador=nombre,  # nombre ganador
                victorias=self.estado.victorias,  # victorias finales
                puntos=puntos,  # puntos jugadores
                nombres=self.estado.nombres,  # nombres jugadores
            )
        )

    def _guardar_resultado(self, nombre_ganador: str, puntos_ganador: int):  # guarda resultado JSON
        """Guarda el resultado en puntuaciones.json."""  # documentación
        ruta = "puntuaciones.json"  # ruta archivo
        lista = []  # lista vacía
        if os.path.exists(ruta):  # si existe archivo
            try:  # intenta leer
                with open(ruta, "r", encoding="utf-8") as f:  # abre archivo
                    lista = json.load(f)  # carga JSON
            except Exception:  # si ocurre error
                lista = []  # reinicia lista
        lista.insert(0, {  # inserta nuevo resultado
            "nombre": nombre_ganador,  # nombre ganador
            "puntos": puntos_ganador,  # puntos ganador
            "rondas": f"{self.estado.victorias[0]}-{self.estado.victorias[1]}",  # marcador rondas
            "fecha": datetime.now().strftime("%d/%m/%Y"),  # fecha actual
        })
        lista = lista[:50]  # limita a 50 registros
        try:  # intenta guardar
            with open(ruta, "w", encoding="utf-8") as f:  # abre archivo escritura
                json.dump(lista, f, ensure_ascii=False, indent=2)  # guarda JSON
        except Exception:  # si ocurre error
            pass  # ignora error

    # Overlay

    def _mostrar_overlay(self, titulo: str, subtitulo: str, color: str):  # muestra overlay
        self.overlay.mostrar(titulo, subtitulo, color)  # configura overlay
        self.overlay.setGeometry(self.rect())  # ajusta tamaño
        self.overlay.show()  # muestra overlay
        self.overlay.raise_()  # pone overlay al frente

    def _ocultar_overlay(self):  # oculta overlay
        self.overlay.hide()  # oculta widget

    def resizeEvent(self, e):  # evento redimensionar
        super().resizeEvent(e)  # ejecuta evento padre
        self.overlay.setGeometry(self.rect())  # reajusta overlay

    #  Teclado

    def keyPressEvent(self, e):  # evento teclado
        if not self.estado:  # si no existe estado
            return  # sale función
        j0, j1 = self.estado.serpientes  # obtiene serpientes
        tecla = e.key()  # obtiene tecla

        # Jugador 1 — WASD + Q
        if tecla == Qt.Key_W:  # mover arriba
            j0.cambiar_direccion(0, -1)  # cambia dirección
        elif tecla == Qt.Key_S:  # mover abajo
            j0.cambiar_direccion(0, 1)  # cambia dirección
        elif tecla == Qt.Key_A:  # mover izquierda
            j0.cambiar_direccion(-1, 0)  # cambia dirección
        elif tecla == Qt.Key_D:  # mover derecha
            j0.cambiar_direccion(1, 0)  # cambia dirección
        elif tecla == Qt.Key_Q:  # usar powerup
            if not self.estado.usar_powerup(0):  # si no tiene powerup
                self.panel_j1.parpadear_sin_powerup()  # muestra aviso

        # Jugador 2 — Flechas + teclas alternativas para teclado español
        elif tecla == Qt.Key_Up:  # mover arriba
            j1.cambiar_direccion(0, -1)  # cambia dirección
        elif tecla == Qt.Key_Down:  # mover abajo
            j1.cambiar_direccion(0, 1)  # cambia dirección
        elif tecla == Qt.Key_Left:  # mover izquierda
            j1.cambiar_direccion(-1, 0)  # cambia dirección
        elif tecla == Qt.Key_Right:  # mover derecha
            j1.cambiar_direccion(1, 0)  # cambia dirección
        elif tecla in (Qt.Key_Slash, Qt.Key_Minus, Qt.Key_Period,  # teclas powerup
                       Qt.Key_0, Qt.Key_Insert, Qt.Key_End,  # teclas alternativas
                       Qt.Key_PageDown, Qt.Key_Delete):  # más teclas alternativas
            if not self.estado.usar_powerup(1):  # si no tiene powerup
                self.panel_j2.parpadear_sin_powerup()  # muestra aviso

        elif tecla == Qt.Key_Escape:  # tecla escape
            self.timer_juego.stop()  # detiene timer principal
            self.timer_segundo.stop()  # detiene timer secundario
            musica.iniciar()  # reproduce música
            from pantalla.inicio import PantallaInicio  # importa inicio
            self.ventana.setCentralWidget(PantallaInicio(self.ventana))  # vuelve al menú
