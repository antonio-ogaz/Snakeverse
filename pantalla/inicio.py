"""
pantalla/inicio.py — Pantalla de inicio / menú principal  # Descripción del archivo
"""  # Fin del comentario inicial

import os  # Importa funciones del sistema operativo
from PySide6.QtWidgets import (  # Importa widgets de PySide6
    QWidget, QHBoxLayout, QVBoxLayout,  # Widgets y layouts principales
    QPushButton, QLabel, QSizePolicy, QFrame,  # Botones, etiquetas y frames
)
from PySide6.QtGui import QPixmap, QFont  # Importa imágenes y fuentes
from PySide6.QtCore import Qt  # Importa constantes de Qt

from utilidad.estilos import (  # Importa colores y estilos personalizados
    DORADO, GRIS, VERDE,  # Colores principales
    FONDO_OSCURO,  # Color de fondo
    estilo_boton_verde, estilo_boton_rojo,  # Estilos de botones
    estilo_boton_dorado, estilo_boton_azul, estilo_boton_morado,  # Más estilos
)
from utilidad.musica import musica  # Importa controlador de música


def ruta_recurso(nombre: str) -> str:  # Función para obtener la ruta de recursos
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtiene carpeta raíz
    return os.path.join(raiz, "recursos", nombre)  # Devuelve ruta completa


class PantallaInicio(QWidget):  # Clase principal de pantalla de inicio
    def __init__(self, ventana_principal=None):  # Constructor de la clase
        super().__init__(ventana_principal)  # Inicializa QWidget
        self.ventana = ventana_principal  # Guarda referencia de ventana principal

        # Fondo UNIFORME en toda la pantalla  # Comentario descriptivo
        self.setStyleSheet(f"""  # Aplica estilos generales
            QWidget {{  # Estilo para widgets
                background-color: {FONDO_OSCURO};  # Fondo oscuro
            }}
            QFrame {{  # Estilo para frames
                background-color: {FONDO_OSCURO};  # Fondo oscuro en frames
                border: none;  # Sin bordes
            }}
            QLabel {{  # Estilo para etiquetas
                background: transparent;  # Fondo transparente
            }}
        """)

        musica.iniciar()  # Inicia música del menú
        self._construir_interfaz()  # Construye interfaz gráfica

    def _construir_interfaz(self):  # Método para construir la interfaz
        # Layout principal  # Comentario descriptivo
        raiz = QHBoxLayout(self)  # Layout horizontal principal
        raiz.setContentsMargins(30, 30, 30, 30)  # Márgenes internos
        raiz.setSpacing(40)  # Espaciado entre elementos

        # Columna izquierda: logo  # Comentario descriptivo
        col_logo = self._columna_logo()  # Obtiene columna del logo
        raiz.addLayout(col_logo, 50)  # Agrega columna al layout

        # Separador vertical  # Comentario descriptivo
        separador = QFrame()  # Crea frame separador
        separador.setFrameShape(QFrame.VLine)  # Define línea vertical
        separador.setStyleSheet(f"""  # Aplica estilos al separador
            background-color: {DORADO};  # Color dorado
            max-width: 2px;  # Ancho máximo
            min-width: 2px;  # Ancho mínimo
            margin: 50px 0;  # Márgenes verticales
            border: none;  # Sin bordes
        """)
        raiz.addWidget(separador, 0)  # Agrega separador

        # Columna derecha: botones  # Comentario descriptivo
        col_botones = self._columna_botones()  # Obtiene columna de botones
        raiz.addLayout(col_botones, 50)  # Agrega columna al layout

    def _columna_logo(self) -> QVBoxLayout:  # Método para crear columna del logo
        col = QVBoxLayout()  # Layout vertical
        col.setContentsMargins(0, 0, 0, 0)  # Márgenes internos
        col.setSpacing(20)  # Espaciado entre widgets
        col.setAlignment(Qt.AlignCenter)  # Centra contenido

        # Título  # Comentario descriptivo
        lbl_title = QLabel("SNAKEVERSE")  # Etiqueta del título
        lbl_title.setFont(QFont("Consolas", 32, QFont.Bold))  # Fuente y tamaño
        lbl_title.setStyleSheet(f"color: {DORADO}; background: transparent;")  # Estilo visual
        lbl_title.setAlignment(Qt.AlignCenter)  # Centra texto
        col.addWidget(lbl_title)  # Agrega etiqueta

        col.addStretch()  # Espacio flexible

        # Logo  # Comentario descriptivo
        self._lbl_logo = QLabel()  # Etiqueta para imagen
        self._lbl_logo.setAlignment(Qt.AlignCenter)  # Centra imagen
        self._lbl_logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Expansión automática
        self._lbl_logo.setMinimumHeight(250)  # Altura mínima
        self._lbl_logo.setStyleSheet("background: transparent;")  # Fondo transparente
        self._ruta_logo = ruta_recurso("logo.png")  # Guarda ruta del logo
        self._cargar_logo()  # Carga la imagen
        col.addWidget(self._lbl_logo, stretch=2)  # Agrega logo al layout

        col.addStretch()  # Espacio flexible

        return col  # Devuelve layout        

    def _cargar_logo(self):  # Método que carga el logo
        """Carga el logo."""  # Descripción del método
        pixmap = QPixmap(self._ruta_logo)  # Carga la imagen desde la ruta

        if not pixmap.isNull():  # Verifica si la imagen existe correctamente
            self._pixmap_original = pixmap  # Guarda imagen original
            self._lbl_logo.setScaledContents(False)  # Desactiva escalado automático
        else:  # Si no se encuentra la imagen
            self._pixmap_original = None  # Borra referencia de imagen
            self._lbl_logo.setText("🐍")  # Muestra emoji de serpiente
            self._lbl_logo.setFont(QFont("Segoe UI", 80))  # Define tamaño de fuente
            self._lbl_logo.setStyleSheet(f"color: {DORADO}; background: transparent;")  # Estilo visual

    def resizeEvent(self, e):  # Evento ejecutado al cambiar tamaño de ventana
        """Reescala el logo."""  # Descripción del método
        super().resizeEvent(e)  # Ejecuta resizeEvent original

        if hasattr(self, '_pixmap_original') and self._pixmap_original:  # Verifica existencia del logo
            w = self._lbl_logo.width()  # Obtiene ancho del label
            h = self._lbl_logo.height()  # Obtiene alto del label

            if w > 10 and h > 10:  # Verifica tamaño válido
                scaled = self._pixmap_original.scaled(  # Escala imagen proporcionalmente
                    w, h,  # Nuevo ancho y alto
                    Qt.KeepAspectRatio,  # Mantiene proporción
                    Qt.SmoothTransformation,  # Escalado suave
                )
                self._lbl_logo.setPixmap(scaled)  # Asigna imagen escalada

    def _columna_botones(self) -> QVBoxLayout:  # Método para crear columna de botones
        col = QVBoxLayout()  # Layout vertical
        col.setContentsMargins(0, 0, 0, 0)  # Márgenes internos
        col.setSpacing(14)  # Espaciado entre botones
        col.setAlignment(Qt.AlignVCenter)  # Centra verticalmente

        # Título menú  # Comentario descriptivo
        lbl_menu = QLabel("MENÚ PRINCIPAL")  # Etiqueta del menú
        lbl_menu.setFont(QFont("Consolas", 12, QFont.Bold))  # Fuente y tamaño
        lbl_menu.setStyleSheet(f"color: {DORADO}; background: transparent; letter-spacing: 4px;")  # Estilo visual
        lbl_menu.setAlignment(Qt.AlignCenter)  # Centra el texto
        col.addWidget(lbl_menu)  # Agrega etiqueta

        col.addSpacing(20)  # Espacio adicional

        # Botones con sus estilos originales  # Comentario descriptivo
        btn_jugar = QPushButton("▶   JUGAR")  # Botón jugar
        btn_ajustes = QPushButton("⚙   AJUSTES")  # Botón ajustes
        btn_puntuaciones = QPushButton("⭐   PUNTUACIONES")  # Botón puntuaciones
        btn_salir = QPushButton("✕   SALIR")  # Botón salir

        self.btn_musica = QPushButton(  # Botón de música
            "🔊   MÚSICA: ON" if musica.esta_activa() else "🔇   MÚSICA: OFF"  # Texto según estado
        )

        # Aplicar estilos originales  # Comentario descriptivo
        btn_jugar.setStyleSheet(estilo_boton_verde())  # Aplica estilo verde
        btn_ajustes.setStyleSheet(estilo_boton_morado())  # Aplica estilo morado
        btn_puntuaciones.setStyleSheet(estilo_boton_dorado())  # Aplica estilo dorado
        btn_salir.setStyleSheet(estilo_boton_rojo())  # Aplica estilo rojo
        self.btn_musica.setStyleSheet(estilo_boton_azul())  # Aplica estilo azul

        # Configurar tamaños como estaban originalmente  # Comentario descriptivo
        for boton in [btn_jugar, btn_ajustes, btn_puntuaciones, btn_salir, self.btn_musica]:  # Recorre botones
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ajusta política de tamaño
            boton.setMinimumHeight(52)  # Altura mínima
            boton.setCursor(Qt.PointingHandCursor)  # Cursor tipo mano
            col.addWidget(boton)  # Agrega botón al layout

        col.addStretch()  # Espacio flexible

        # Versión  # Comentario descriptivo
        lbl_version = QLabel("v1.0")  # Etiqueta de versión
        lbl_version.setFont(QFont("Segoe UI", 9))  # Fuente y tamaño
        lbl_version.setStyleSheet(f"color: {GRIS}; background: transparent;")  # Estilo visual
        lbl_version.setAlignment(Qt.AlignRight)  # Alinea a la derecha
        col.addWidget(lbl_version)  # Agrega etiqueta

        # Conexiones  # Comentario descriptivo
        btn_jugar.clicked.connect(self._ir_configuracion)  # Conecta botón jugar
        btn_puntuaciones.clicked.connect(self._ir_puntuaciones)  # Conecta botón puntuaciones
        btn_ajustes.clicked.connect(self._ir_ajustes)  # Conecta botón ajustes
        btn_salir.clicked.connect(self.ventana.close)  # Conecta botón salir
        self.btn_musica.clicked.connect(self._alternar_musica)  # Conecta botón música

        return col  # Devuelve layout

    def _ir_configuracion(self):  # Método para abrir configuración
        from pantalla.configuracion import PantallaConfiguracion  # Importa pantalla configuración
        self.ventana.setCentralWidget(PantallaConfiguracion(self.ventana))  # Cambia pantalla

    def _ir_puntuaciones(self):  # Método para abrir puntuaciones
        from pantalla.puntuaciones import PantallaPuntuaciones  # Importa pantalla puntuaciones
        self.ventana.setCentralWidget(PantallaPuntuaciones(self.ventana))  # Cambia pantalla

    def _ir_ajustes(self):  # Método para abrir ajustes
        from pantalla.ajustes import PantallaAjustes  # Importa pantalla ajustes
        self.ventana.setCentralWidget(PantallaAjustes(self.ventana))  # Cambia pantalla

    def _alternar_musica(self):  # Método para activar/desactivar música
        musica.alternar()  # Cambia estado de música

        if musica.esta_activa():  # Verifica si música está activa
            self.btn_musica.setText("🔊   MÚSICA: ON")  # Cambia texto a ON
        else:  # Si la música está apagada
            self.btn_musica.setText("🔇   MÚSICA: OFF")  # Cambia texto a OFF
