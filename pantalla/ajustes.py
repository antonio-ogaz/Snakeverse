"""
pantalla/ajustes.py — Pantalla de ajustes del juego
"""  # Comentario descriptivo del archivo

from PySide6.QtWidgets import (  # Importa widgets de interfaz gráfica
    QWidget, QVBoxLayout, QHBoxLayout,  # Widgets y layouts
    QLabel, QPushButton, QSlider,  # Etiquetas, botones y sliders
    QSpacerItem, QSizePolicy, QFrame,  # Espaciadores y contenedores
)

from PySide6.QtGui import QFont  # Importa manejo de fuentes
from PySide6.QtCore import Qt  # Importa constantes de Qt

from utilidad.estilos import (  # Importa colores y estilos personalizados
    DORADO, BLANCO_CALIDO, GRIS,  # Colores principales
    VERDE, AZUL, MORADO, NARANJA, FONDO_MEDIO, BORDE_ACTIVO,  # Más colores
    estilo_ventana, estilo_boton_base,  # Funciones de estilos
)

from utilidad.musica import musica  # Importa controlador de música


class PantallaAjustes(QWidget):  # Clase principal de pantalla de ajustes
    """
    Pantalla de ajustes con opciones de volumen,
    velocidad del juego y personalización.
    """  # Descripción de la clase

    def __init__(self, ventana_principal=None):  # Constructor
        super().__init__(ventana_principal)  # Inicializa QWidget
        self.ventana = ventana_principal  # Guarda referencia a ventana principal
        self.setStyleSheet(estilo_ventana())  # Aplica estilo general
        self._construir_interfaz()  # Construye toda la interfaz

    def _construir_interfaz(self):  # Método que crea la interfaz
        layout = QVBoxLayout(self)  # Layout vertical principal
        layout.setContentsMargins(80, 40, 80, 40)  # Márgenes internos
        layout.setSpacing(0)  # Espaciado entre widgets

        # Título
        lbl_titulo = QLabel("⚙  AJUSTES")  # Etiqueta del título
        lbl_titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))  # Fuente del título
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")  # Color y fondo
        lbl_titulo.setAlignment(Qt.AlignCenter)  # Centra el texto
        layout.addWidget(lbl_titulo)  # Agrega al layout

        lbl_sub = QLabel("Personaliza tu experiencia de juego")  # Subtítulo
        lbl_sub.setFont(QFont("Segoe UI", 11))  # Fuente del subtítulo
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")  # Estilo
        lbl_sub.setAlignment(Qt.AlignCenter)  # Centrado
        layout.addWidget(lbl_sub)  # Agrega subtítulo

        layout.addSpacing(24)  # Espacio vertical

        layout.addWidget(self._tarjeta_audio())  # Agrega tarjeta de audio
        layout.addSpacing(16)  # Espacio vertical
        layout.addWidget(self._tarjeta_juego())  # Agrega tarjeta de juego
        layout.addSpacing(16)  # Espacio vertical
        layout.addWidget(self._tarjeta_personalizacion())  # Agrega tarjeta de personalización

        layout.addSpacerItem(  # Agrega espacio flexible
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        btn_volver = QPushButton("← VOLVER AL MENÚ")  # Botón regresar
        btn_volver.setStyleSheet(estilo_boton_base())  # Aplica estilo
        btn_volver.setMinimumWidth(220)  # Ancho mínimo
        btn_volver.setCursor(Qt.PointingHandCursor)  # Cursor tipo mano
        btn_volver.clicked.connect(self._volver)  # Conecta click al método volver
        layout.addWidget(btn_volver, 0, Qt.AlignCenter)  # Agrega botón centrado

    def _crear_tarjeta(self, titulo_texto, color_borde) -> tuple:  # Crea una tarjeta personalizada
        """Devuelve (frame, layout_interno)."""  # Explicación del método

        frame = QFrame()  # Contenedor visual
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_borde};
                border-radius: 8px;
            }}
        """)  # Estilo visual de la tarjeta

        lay = QVBoxLayout(frame)  # Layout interno vertical
        lay.setContentsMargins(20, 16, 20, 16)  # Márgenes internos
        lay.setSpacing(10)  # Espaciado interno

        lbl = QLabel(titulo_texto)  # Etiqueta del título
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))  # Fuente del título
        lbl.setStyleSheet(
            f"color: {color_borde}; background: transparent; border: none;"
        )  # Estilo del texto

        lay.addWidget(lbl)  # Agrega el título al layout
        return frame, lay  # Retorna frame y layout

    def _tarjeta_audio(self) -> QFrame:  # Crea sección de audio
        frame, lay = self._crear_tarjeta("🔊  AUDIO", AZUL)  # Tarjeta azul

        fila = QHBoxLayout()  # Layout horizontal
        fila.setSpacing(10)  # Espaciado entre widgets

        lbl = QLabel("Volumen de música:")  # Texto descriptivo
        lbl.setFont(QFont("Segoe UI", 12))  # Fuente
        lbl.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )  # Estilo
        lbl.setFixedWidth(200)  # Ancho fijo

        self.slider_volumen = QSlider(Qt.Horizontal)  # Slider horizontal
        self.slider_volumen.setRange(0, 100)  # Rango de volumen
        self.slider_volumen.setValue(musica.obtener_volumen())  # Valor actual

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
        """)  # Estilo visual del slider

        self.lbl_volumen = QLabel(f"{musica.obtener_volumen()}%")  # Texto porcentaje
        self.lbl_volumen.setFont(QFont("Segoe UI", 12, QFont.Bold))  # Fuente
        self.lbl_volumen.setStyleSheet(
            f"color: {AZUL}; background: transparent; border: none;"
        )  # Estilo
        self.lbl_volumen.setFixedWidth(40)  # Ancho fijo

        self.slider_volumen.valueChanged.connect(self._cambiar_volumen)  # Evento cambio

        fila.addWidget(lbl)  # Agrega texto
        fila.addWidget(self.slider_volumen)  # Agrega slider
        fila.addWidget(self.lbl_volumen)  # Agrega porcentaje
        lay.addLayout(fila)  # Agrega fila a tarjeta

        nota = QLabel("Nota: el volumen se ajusta en tiempo real.")  # Nota informativa
        nota.setFont(QFont("Segoe UI", 9))  # Fuente pequeña
        nota.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )  # Estilo
        lay.addWidget(nota)  # Agrega nota

        return frame  # Retorna tarjeta

    def _cambiar_volumen(self, valor: int):  # Cambia volumen
        """Cambia el volumen de la música en tiempo real."""  # Explicación

        self.lbl_volumen.setText(f"{valor}%")  # Actualiza texto
        musica.cambiar_volumen(valor)  # Cambia volumen en música

    def _tarjeta_juego(self) -> QFrame:  # Crea tarjeta de opciones del juego
        frame, lay = self._crear_tarjeta("🎮  JUEGO", VERDE)  # Tarjeta verde

        info = QLabel(
            "Velocidad: Normal  ·  Rondas: Mejor de 5  ·  Tiempo por ronda: 90s\n"
            "Power-ups: Activados  ·  Obstáculos progresivos: Activados"
        )  # Información del juego

        info.setFont(QFont("Segoe UI", 12))  # Fuente
        info.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )  # Estilo

        info.setWordWrap(True)  # Permite salto de línea
        lay.addWidget(info)  # Agrega texto

        return frame  # Retorna tarjeta

    def _tarjeta_personalizacion(self) -> QFrame:  # Tarjeta de personalización
        frame, lay = self._crear_tarjeta("🎨  PERSONALIZACIÓN", MORADO)  # Tarjeta morada

        info = QLabel(
            "Los colores de las serpientes se seleccionan antes de cada partida.\n"
        )  # Información

        info.setFont(QFont("Segoe UI", 12))  # Fuente
        info.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )  # Estilo

        info.setWordWrap(True)  # Ajuste de texto
        lay.addWidget(info)  # Agrega información

        return frame  # Retorna tarjeta

    def _volver(self):  # Método para regresar al menú
        from pantalla.inicio import PantallaInicio  # Importa pantalla inicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))  # Cambia pantalla
