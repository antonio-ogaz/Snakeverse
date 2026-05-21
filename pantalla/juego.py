from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtCore import Qt, QTimer
import random

class JuegoWindow(QWidget):

    def __init__(self, parent=None, nombre_j1="Jugador 1", nombre_j2="Jugador 2"):
        super().__init__()
        self.parent = parent

        self.nombre_j1 = nombre_j1
        self.nombre_j2 = nombre_j2

        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()

        titulo = QLabel("SNAKEVERSE")
        titulo.setFont(QFont("Arial", 28, QFont.Bold))
        titulo.setStyleSheet("color: darkblue; margin-bottom: 15px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.tiempo = 60
        self.ronda = 1
        self.max_rondas = 3

        self.marcador = QLabel(
            f"Tiempo: {self.tiempo}    Ronda: {self.ronda}/{self.max_rondas}"
        )

        self.marcador.setFont(QFont("Arial", 20, QFont.Bold))

        self.marcador.setStyleSheet("""
            color: black;
            background-color: lightgray;
            padding: 8px;
        """)

        self.marcador.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.marcador)

        self.puntajes = QLabel(
            f"{self.nombre_j1}: 0    {self.nombre_j2}: 0"
        )

        self.puntajes.setFont(QFont("Arial", 18, QFont.Bold))

        self.puntajes.setStyleSheet("""
            color: green;
            background-color: #f0f0f0;
            padding: 6px;
        """)

        self.puntajes.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.puntajes)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)

        btn_volver = QPushButton("VOLVER AL MENÚ")

        btn_volver.setStyleSheet(""" font-size: 16px; padding: 8px; """)

        btn_volver.clicked.connect(self.volver)
        layout.addWidget(btn_volver)

        self.setLayout(layout)

        self.tamano = 20

        self.puntos1 = 0
        self.puntos2 = 0

        self.iniciar_ronda()

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_juego)
        self.timer.start(120)

        self.timer_tiempo = QTimer()
        self.timer_tiempo.timeout.connect(self.actualizar_tiempo)
        self.timer_tiempo.start(1000)

    def iniciar_ronda(self):

        self.snake1 = [(100, 100), (80, 100), (60, 100)]

        self.snake2 = [(500, 300),(520, 300), (540, 300)]

        self.dx1 = 20
        self.dy1 = 0

        self.dx2 = -20
        self.dy2 = 0

        self.comida = self.generar_comida()

    def generar_comida(self):

        x = random.randint(0, 35) * self.tamano
        y = random.randint(0, 20) * self.tamano

        return (x, y)

    def actualizar_tiempo(self):

        self.tiempo -= 1

        self.marcador.setText(
            f"Tiempo: {self.tiempo}    Ronda: {self.ronda}/{self.max_rondas}"
        )

        if self.tiempo <= 0:

            self.ronda += 1

            if self.ronda > self.max_rondas:

                self.timer.stop()
                self.timer_tiempo.stop()

                if self.puntos1 > self.puntos2:
                    ganador = self.nombre_j1

                elif self.puntos2 > self.puntos1:
                    ganador = self.nombre_j2

                else:
                    ganador = "EMPATE"

                self.marcador.setText(
                    f"FIN DEL JUEGO - GANADOR: {ganador}"
                )

            else:

                self.tiempo = 60
                self.iniciar_ronda()

    def actualizar_juego(self):

        cabeza1 = self.snake1[0]

        nueva1 = (
            cabeza1[0] + self.dx1,
            cabeza1[1] + self.dy1
        )

        self.snake1.insert(0, nueva1)

        if nueva1 == self.comida:

            self.puntos1 += 10
            self.comida = self.generar_comida()

        else:
            self.snake1.pop()

        cabeza2 = self.snake2[0]

        nueva2 = (
            cabeza2[0] + self.dx2,
            cabeza2[1] + self.dy2
        )

        self.snake2.insert(0, nueva2)

        if nueva2 == self.comida:

            self.puntos2 += 10
            self.comida = self.generar_comida()

        else:
            self.snake2.pop()

        self.verificar_colisiones()

        self.puntajes.setText(
            f"{self.nombre_j1}: {self.puntos1}    "
            f"{self.nombre_j2}: {self.puntos2}"
        )

        self.update()

    def verificar_colisiones(self):

        x1, y1 = self.snake1[0]
        x2, y2 = self.snake2[0]

        if x1 < 0 or x1 >= 800 or y1 < 0 or y1 >= 600:
            self.iniciar_ronda()

        if x2 < 0 or x2 >= 800 or y2 < 0 or y2 >= 600:
            self.iniciar_ronda()

        if self.snake1[0] in self.snake1[1:]:
            self.iniciar_ronda()

        if self.snake2[0] in self.snake2[1:]:
            self.iniciar_ronda()

        if self.snake1[0] in self.snake2:
            self.iniciar_ronda()

        if self.snake2[0] in self.snake1:
            self.iniciar_ronda()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.fillRect(0, 130, 800, 420, QColor(20, 20, 20) )

        painter.setBrush(QColor("red"))

        painter.drawEllipse(
            self.comida[0],
            self.comida[1] + 130,
            self.tamano,
            self.tamano
        )

        painter.setBrush(QColor("green"))

        for x, y in self.snake1:

            painter.drawRect(x y + 130, self.tamano, self.tamano)

        painter.setBrush(QColor("blue"))

        for x, y in self.snake2:

            painter.drawRect(x, y + 130, self.tamano, self.tamano)

        if self.ronda > self.max_rondas:

            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 26, QFont.Bold))

            if self.puntos1 > self.puntos2:
                ganador = self.nombre_j1

            elif self.puntos2 > self.puntos1:
                ganador = self.nombre_j2

            else:
                ganador = "EMPATE"

            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                f"GANADOR: {ganador}"
            )

    def keyPressEvent(self, event):

        tecla = event.key()

        if tecla == Qt.Key_W and self.dy1 == 0:
            self.dx1 = 0
            self.dy1 = -20

        elif tecla == Qt.Key_S and self.dy1 == 0:
            self.dx1 = 0
            self.dy1 = 20

        elif tecla == Qt.Key_A and self.dx1 == 0:
            self.dx1 = -20
            self.dy1 = 0

        elif tecla == Qt.Key_D and self.dx1 == 0:
            self.dx1 = 20
            self.dy1 = 0

        elif tecla == Qt.Key_Up and self.dy2 == 0:
            self.dx2 = 0
            self.dy2 = -20

        elif tecla == Qt.Key_Down and self.dy2 == 0:
            self.dx2 = 0
            self.dy2 = 20

        elif tecla == Qt.Key_Left and self.dx2 == 0:
            self.dx2 = -20
            self.dy2 = 0

        elif tecla == Qt.Key_Right and self.dx2 == 0:
            self.dx2 = 20
            self.dy2 = 0

    def volver(self):

        from pantalla.inicio import InicioWindow

        self.parent.setCentralWidget(
            InicioWindow(self.parent)
        )
