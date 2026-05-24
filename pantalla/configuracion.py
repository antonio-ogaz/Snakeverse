"""
pantalla/configuracion.py — Configuración de partida  # Archivo de configuración de la pantalla de partida

Incluye:  # Descripción de funcionalidades
  - Nombre de cada jugador  # Permite escribir nombres
  - Selector de color de serpiente (swatches visuales)  # Permite elegir colores
  - Configuración de red con modo ANFITRIÓN / CLIENTE / LOCAL  # Modos de conexión
    Anfitrión: crea la sala, muestra su IP para compartir  # Función del anfitrión
    Cliente:   ingresa la IP del anfitrión y se conecta  # Función del cliente
"""

import socket  # Librería para conexiones de red
import threading  # Librería para manejar hilos
import os  # Librería del sistema operativo

from PySide6.QtWidgets import (  # Importación de widgets de PySide6
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,  # Layouts y contenedores
    QLabel, QLineEdit, QPushButton,  # Widgets básicos
    QSpacerItem, QSizePolicy, QFrame, QButtonGroup,  # Espaciadores y marcos
)

from PySide6.QtGui import QFont, QColor  # Manejo de fuentes y colores
from PySide6.QtCore import Qt, QTimer, Signal, QObject  # Utilidades principales de Qt

from utilidad.estilos import (  # Importación de estilos personalizados
    DORADO, DORADO_CLARO, VERDE, AZUL, CIAN, ROJO,  # Colores principales
    BLANCO_CALIDO, GRIS, NARANJA, MORADO,  # Más colores
    FONDO_MEDIO, FONDO_OSCURO, BORDE_ACTIVO,  # Fondos y bordes
    estilo_ventana, estilo_input,  # Funciones de estilos
    estilo_boton_verde, estilo_boton_base,  # Estilos de botones
    estilo_boton_azul, estilo_boton_rojo,  # Más estilos
)

from utilidad.musica import musica  # Controlador de música del juego

# Colores disponibles para cada jugador  # Comentario descriptivo
COLORES_J1 = [  # Lista de colores para jugador 1
    ("#2ECC40", "#1A8C28"),   # verde vibrante
    ("#40FF60", "#20B040"),   # verde neón
    ("#FFD040", "#C09010"),   # dorado
    ("#80FF40", "#40B020"),   # lima
    ("#20E8A0", "#10A060"),   # turquesa
    ("#40D8FF", "#2090C0"),   # cian
    ("#C060FF", "#7020C0"),   # morado
    ("#FF9040", "#C05020"),   # naranja
]

COLORES_J2 = [  # Lista de colores para jugador 2
    ("#209AE8", "#1464A8"),   # azul eléctrico
    ("#40B8FF", "#1880D0"),   # azul cielo
    ("#E03060", "#A01040"),   # rojo vibrante
    ("#FF4080", "#C02060"),   # magenta
    ("#E8C020", "#A08010"),   # amarillo
    ("#FF6040", "#C03020"),   # rojo-naranja
    ("#A0A8FF", "#6068C8"),   # lavanda
    ("#4DD0E1", "#006064"),   # agua
]

PUERTO_RED = 5555  # Puerto utilizado para conexión en red


def obtener_ip_local() -> str:  # Función para obtener IP local
    """Obtiene la IP local en la red LAN."""  # Descripción de la función
    try:  # Intentar ejecutar
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Crear socket UDP
        s.connect(("8.8.8.8", 80))  # Conectarse temporalmente a Google DNS
        ip = s.getsockname()[0]  # Obtener IP local
        s.close()  # Cerrar socket
        return ip  # Retornar IP
    except Exception:  # Si ocurre error
        return "127.0.0.1"  # Retornar localhost


class SeñalesRed(QObject):  # Clase de señales Qt
    """Señales Qt para comunicar el hilo de red con la UI."""  # Descripción
    conectado = Signal()  # Señal cuando conecta
    error = Signal(str)  # Señal de error
    cliente_listo = Signal(str)  # Señal con IP del cliente conectado


class PantallaConfiguracion(QWidget):  # Clase principal de configuración
    def __init__(self, ventana_principal=None):  # Constructor
        super().__init__(ventana_principal)  # Inicializar QWidget padre

        self.ventana = ventana_principal  # Guardar referencia de ventana
        self.color_j1 = COLORES_J1[0]  # Color inicial jugador 1
        self.color_j2 = COLORES_J2[0]  # Color inicial jugador 2

        self.modo_red = "local"  # Modo de red inicial
        self._socket_srv = None  # Socket del servidor

        self._señales_red = SeñalesRed()  # Crear objeto de señales
        self._señales_red.conectado.connect(self._en_conectado)  # Conectar señal conectado
        self._señales_red.error.connect(self._en_error_red)  # Conectar señal error

        self.setStyleSheet(estilo_ventana())  # Aplicar estilo ventana
        self._construir_interfaz()  # Construir interfaz

    def _aplicar_estilo_modo(self):
        """Actualiza el estilo visual de los botones segun el modo activo."""
        estilos = {
            "local":     (self.btn_local,     VERDE),
            "anfitrion": (self.btn_anfitrion, CIAN),
            "cliente":   (self.btn_cliente,   NARANJA),
        }
        for modo, (btn, color) in estilos.items():
            activo = (self.modo_red == modo)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'rgba(0,0,0,0)' if not activo else color};
                    color: {color if not activo else '#0D0D1A'};
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: #0D0D1A;
                }}
            """)

    def _cambiar_modo(self, modo: str):
        """Cambia el modo de red y actualiza la UI."""
        self.modo_red = modo
        self.btn_local.setChecked(modo == "local")
        self.btn_anfitrion.setChecked(modo == "anfitrion")
        self.btn_cliente.setChecked(modo == "cliente")
        self._aplicar_estilo_modo()

    # interfaz  # Comentario de sección

    def _construir_interfaz(self):  # Método para crear interfaz
        # Scroll area para pantallas pequeñas  # Comentario
        layout_raiz = QVBoxLayout(self)  # Layout principal vertical
        layout_raiz.setContentsMargins(0, 0, 0, 0)  # Márgenes en cero
        layout_raiz.setSpacing(0)  # Espaciado cero

        # Contenido scrollable  # Comentario
        contenido = QWidget()  # Widget contenedor
        contenido.setStyleSheet("background: transparent;")  # Fondo transparente

        layout = QVBoxLayout(contenido)  # Layout interno
        layout.setContentsMargins(60, 30, 60, 30)  # Márgenes internos
        layout.setSpacing(0)  # Sin separación

        lbl_titulo = QLabel("⚙  CONFIGURAR PARTIDA")  # Etiqueta título
        lbl_titulo.setFont(QFont("Segoe UI", 24, QFont.Bold))  # Fuente título
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")  # Estilo título
        lbl_titulo.setAlignment(Qt.AlignCenter)  # Centrar texto

        layout.addWidget(lbl_titulo)  # Agregar título
        layout.addSpacing(4)  # Espacio

        lbl_sub = QLabel("Nombres, colores y modo de conexión")  # Subtítulo
        lbl_sub.setFont(QFont("Segoe UI", 10))  # Fuente subtítulo
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")  # Estilo subtítulo
        lbl_sub.setAlignment(Qt.AlignCenter)  # Centrar subtítulo

        layout.addWidget(lbl_sub)  # Agregar subtítulo
        layout.addSpacing(20)  # Espacio

        # Jugadores  # Comentario
        fila_jugadores = QHBoxLayout()  # Layout horizontal jugadores
        fila_jugadores.setSpacing(16)  # Espaciado entre tarjetas

        fila_jugadores.addWidget(self._tarjeta_jugador(1))  # Tarjeta jugador 1
        fila_jugadores.addWidget(self._tarjeta_jugador(2))  # Tarjeta jugador 2

        layout.addLayout(fila_jugadores)  # Agregar fila
        layout.addSpacing(16)  # Espacio

        # Configuración de red  # Comentario
        layout.addWidget(self._tarjeta_red())  # Agregar tarjeta red
        layout.addSpacing(20)  # Espacio

        # Botones inferiores  # Comentario
        fila_botones = QHBoxLayout()  # Layout horizontal botones
        fila_botones.setSpacing(14)  # Espaciado

        btn_volver = QPushButton("← VOLVER")  # Botón volver
        btn_iniciar = QPushButton("▶  INICIAR JUEGO")  # Botón iniciar

        btn_volver.setStyleSheet(estilo_boton_base())  # Estilo botón volver
        btn_iniciar.setStyleSheet(estilo_boton_verde())  # Estilo botón iniciar

        btn_volver.setMinimumWidth(160)  # Ancho mínimo volver
        btn_iniciar.setMinimumWidth(200)  # Ancho mínimo iniciar

        btn_volver.setCursor(Qt.PointingHandCursor)  # Cursor tipo mano
        btn_iniciar.setCursor(Qt.PointingHandCursor)  # Cursor tipo mano

        fila_botones.addStretch()  # Espaciador
        fila_botones.addWidget(btn_volver)  # Agregar botón volver
        fila_botones.addWidget(btn_iniciar)  # Agregar botón iniciar
        fila_botones.addStretch()  # Espaciador

        layout.addLayout(fila_botones)  # Agregar layout botones

        btn_volver.clicked.connect(self._volver)  # Conectar botón volver
        btn_iniciar.clicked.connect(self._iniciar)  # Conectar botón iniciar

        layout_raiz.addWidget(contenido)  # Agregar contenido al layout raíz 

    # Tarjeta de jugador con nombre + selector de color  # Comentario de sección

    def _tarjeta_jugador(self, numero: int) -> QFrame:  # Método para crear tarjeta de jugador
        es_j1 = (numero == 1)  # Verificar si es jugador 1
        color_acento = VERDE if es_j1 else AZUL  # Elegir color de borde
        colores = COLORES_J1 if es_j1 else COLORES_J2  # Seleccionar lista de colores
        titulo = "🟢  JUGADOR 1" if es_j1 else "🔵  JUGADOR 2"  # Texto del título
        placeholder = "Nombre J1" if es_j1 else "Nombre J2"  # Placeholder del input
        pista = "WASD + Q" if es_j1 else "↑↓←→ + /"  # Controles del jugador

        frame = QFrame()  # Crear marco principal
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {color_acento};
                border-radius: 8px;
            }}
        """)  # Aplicar estilo visual

        lay = QVBoxLayout(frame)  # Crear layout vertical
        lay.setContentsMargins(16, 14, 16, 14)  # Márgenes internos
        lay.setSpacing(10)  # Espaciado interno

        # Título de la tarjeta  # Comentario
        lbl = QLabel(titulo)  # Crear etiqueta título
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))  # Fuente del título
        lbl.setStyleSheet(
            f"color: {color_acento}; background: transparent; border: none;"
        )  # Estilo del texto

        lay.addWidget(lbl)  # Agregar título al layout

        # Campo de nombre  # Comentario
        campo = QLineEdit()  # Crear campo de texto
        campo.setPlaceholderText(placeholder)  # Texto guía
        campo.setMaxLength(20)  # Límite de caracteres
        campo.setStyleSheet(estilo_input())  # Aplicar estilo
        lay.addWidget(campo)  # Agregar campo al layout

        lbl_controles = QLabel(f"Controles: {pista}")  # Etiqueta de controles
        lbl_controles.setFont(QFont("Segoe UI", 9))  # Fuente pequeña
        lbl_controles.setStyleSheet(
            f"color: {GRIS}; background: transparent; border: none;"
        )  # Estilo controles

        lay.addWidget(lbl_controles)  # Agregar etiqueta controles

        # Selector de color  # Comentario
        lbl_color = QLabel("Color de serpiente:")  # Etiqueta color
        lbl_color.setFont(QFont("Segoe UI", 10, QFont.Bold))  # Fuente
        lbl_color.setStyleSheet(
            f"color: {BLANCO_CALIDO}; background: transparent; border: none;"
        )  # Estilo texto

        lay.addWidget(lbl_color)  # Agregar etiqueta

        # Cuadrícula de swatches  # Comentario
        grid = QGridLayout()  # Crear layout cuadrícula
        grid.setSpacing(6)  # Espaciado
        swatches = []  # Lista de botones color

        for i, (c1, c2) in enumerate(colores):  # Recorrer colores
            swatch = QPushButton()  # Crear botón color
            swatch.setFixedSize(36, 36)  # Tamaño fijo
            swatch.setCursor(Qt.PointingHandCursor)  # Cursor mano

            swatch.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c1};
                    border-radius: 6px;
                    border: 3px solid {'#FFFFFF' if i == 0 else 'transparent'};
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                }}
            """)  # Estilo del swatch

            swatch.setToolTip(f"Color {i+1}")  # Tooltip del color

            grid.addWidget(swatch, i // 4, i % 4)  # Agregar a cuadrícula
            swatches.append(swatch)  # Guardar botón

        lay.addLayout(grid)  # Agregar cuadrícula al layout

        # Preview del color seleccionado  # Comentario
        preview = QLabel()  # Crear preview
        preview.setFixedHeight(14)  # Altura fija

        preview.setStyleSheet(
            f"background-color: {colores[0][0]}; border-radius: 6px; border: none;"
        )  # Mostrar color inicial

        lay.addWidget(preview)  # Agregar preview

        # Guardar referencias  # Comentario
        if es_j1:  # Si es jugador 1
            self.campo_j1 = campo  # Guardar campo jugador 1
            self._sw1 = swatches  # Guardar swatches jugador 1
            self._prev1 = preview  # Guardar preview jugador 1
        else:  # Si es jugador 2
            self.campo_j2 = campo  # Guardar campo jugador 2
            self._sw2 = swatches  # Guardar swatches jugador 2
            self._prev2 = preview  # Guardar preview jugador 2

        # Conectar swatches  # Comentario
        for i, sw in enumerate(swatches):  # Recorrer botones color
            sw.clicked.connect(
                lambda _, idx=i, n=numero: self._seleccionar_color(idx, n)
            )  # Conectar selección de color

        return frame  # Retornar tarjeta completa

    def _seleccionar_color(self, idx: int, numero: int):  # Método para seleccionar color
        """Actualiza el color seleccionado y resalta el swatch elegido."""  # Descripción

        colores = COLORES_J1 if numero == 1 else COLORES_J2  # Lista correcta de colores
        swatches = self._sw1 if numero == 1 else self._sw2  # Lista de botones
        preview = self._prev1 if numero == 1 else self._prev2  # Preview correspondiente

        if numero == 1:  # Si jugador 1
            self.color_j1 = colores[idx]  # Guardar color seleccionado
        else:  # Si jugador 2
            self.color_j2 = colores[idx]  # Guardar color seleccionado

        for i, sw in enumerate(swatches):  # Recorrer swatches
            c1 = colores[i][0]  # Obtener color principal
            borde = "3px solid #FFFFFF" if i == idx else "3px solid transparent"  # Borde activo

            sw.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c1};
                    border-radius: 6px;
                    border: {borde};
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                }}
            """)  # Actualizar estilo visual

        preview.setStyleSheet(
            f"background-color: {colores[idx][0]}; border-radius: 6px; border: none;"
        )  # Actualizar preview

    # Tarjeta de red  # Comentario de sección

    def _tarjeta_red(self) -> QFrame:  # Método para crear tarjeta de red
        frame = QFrame()  # Crear marco
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FONDO_MEDIO};
                border: 2px solid {CIAN};
                border-radius: 8px;
            }}
        """)  # Estilo del marco

        lay = QVBoxLayout(frame)  # Layout vertical
        lay.setContentsMargins(20, 16, 20, 16)  # Márgenes internos
        lay.setSpacing(12)  # Espaciado

        # Título  # Comentario
        lbl_titulo = QLabel("🌐  MODO DE CONEXIÓN")  # Crear título
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Bold))  # Fuente

        lbl_titulo.setStyleSheet(
            f"color: {CIAN}; background: transparent; border: none;"
        )  # Estilo texto

        lay.addWidget(lbl_titulo)  # Agregar título

        # Botones de modo  # Comentario
        fila_modo = QHBoxLayout()  # Layout horizontal
        fila_modo.setSpacing(10)  # Espaciado

        self.btn_local = QPushButton("🌿  LOCAL")  # Botón local
        self.btn_anfitrion = QPushButton("🏠  ANFITRIÓN")  # Botón anfitrión
        self.btn_cliente = QPushButton("🔗  CLIENTE")  # Botón cliente

        for b in [self.btn_local, self.btn_anfitrion, self.btn_cliente]:  # Recorrer botones
            b.setCheckable(True)  # Activar selección
            b.setCursor(Qt.PointingHandCursor)  # Cursor mano
            b.setMinimumHeight(38)  # Altura mínima
            b.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Fuente botones

        self.btn_local.setChecked(True)  # Marcar modo local
        self._aplicar_estilo_modo()  # Aplicar estilos

        self.btn_local.clicked.connect(lambda: self._cambiar_modo("local"))  # Conectar local
        self.btn_anfitrion.clicked.connect(lambda: self._cambiar_modo("anfitrion"))  # Conectar anfitrión
        self.btn_cliente.clicked.connect(lambda: self._cambiar_modo("cliente"))  # Conectar cliente

        fila_modo.addWidget(self.btn_local)  # Agregar botón local
        fila_modo.addWidget(self.btn_anfitrion)  # Agregar botón anfitrión
        fila_modo.addWidget(self.btn_cliente)  # Agregar botón cliente

        lay.addLayout(fila_modo)  # Agregar fila al layout

        return frame

    def _hilo_servidor(self):  # Método que ejecuta el servidor en segundo plano
        """Hilo: escucha conexiones entrantes."""  # Explicación del método
        try:  # Intenta ejecutar el servidor
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP/IP
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar el puerto
            srv.bind(("", PUERTO_RED))  # Asocia el servidor al puerto definido
            srv.listen(1)  # Escucha una conexión entrante
            srv.settimeout(120)  # Tiempo máximo de espera de 120 segundos
            self._socket_srv = srv  # Guarda referencia del servidor
            conn, addr = srv.accept()  # Espera la conexión del cliente
            conn.close()  # Cierra conexión con el cliente
            srv.close()  # Cierra el servidor
            self._socket_srv = None  # Limpia la referencia del servidor
            # Notificar a la UI (desde hilo → señal Qt)  # Comentario explicativo
            self._señales_red.conectado.emit()  # Emite señal de conexión exitosa
        except Exception as e:  # Captura errores
            self._señales_red.error.emit(str(e))  # Envía el mensaje de error

    def _unirse_sala(self):  # Método para conectarse como cliente
        """Modo CLIENTE: conecta al servidor del anfitrión."""  # Explicación del método
        ip = getattr(self, "_campo_ip_cliente", None)  # Obtiene el campo de texto de IP
        ip_texto = ip.text().strip() if ip else ""  # Obtiene y limpia la IP escrita
        if not ip_texto:  # Verifica si no se escribió IP
            self._lbl_estado_red.setText(" Escribe la IP del anfitrión primero.")  # Muestra mensaje de error
            self._lbl_estado_red.setStyleSheet(  # Cambia estilo del mensaje
                f"color: {ROJO}; background: transparent; border: none;"  # Color rojo de error
            )
            return  # Sale del método

        self._btn_unirse.setEnabled(False)  # Desactiva el botón mientras conecta
        self._lbl_estado_red.setText(f"⏳  Conectando a {ip_texto}:{PUERTO_RED}…")  # Mensaje de conexión
        self._lbl_estado_red.setStyleSheet(  # Cambia estilo del mensaje
            f"color: {DORADO}; background: transparent; border: none;"  # Color dorado de espera
        )

        self._ip_anfitrion = ip_texto  # Guarda la IP del anfitrión

        threading.Thread(  # Crea un hilo secundario
            target=self._hilo_cliente,  # Método que ejecutará el hilo
            args=(ip_texto,),  # Argumentos enviados al hilo
            daemon=True,  # El hilo se cierra al terminar el programa
        ).start()  # Inicia el hilo

    def _hilo_cliente(self, ip: str):  # Método que intenta conectar al servidor
        """Hilo: intenta conectar al servidor."""  # Explicación del método
        try:  # Intenta realizar la conexión
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea socket TCP/IP
            s.settimeout(15)  # Tiempo máximo de espera
            s.connect((ip, PUERTO_RED))  # Conecta al servidor usando IP y puerto
            s.close()  # Cierra la conexión
            self._señales_red.conectado.emit()  # Emite señal de conexión exitosa
        except Exception as e:  # Captura errores
            self._señales_red.error.emit(str(e))  # Envía mensaje de error

    def _en_conectado(self):  # Método ejecutado al conectarse correctamente
        """Llamado cuando la conexión TCP se establece (ambos modos)."""  # Explicación del método
        self._lbl_estado_red.setText("✅  ¡Conexión establecida! Iniciando juego…")  # Muestra mensaje de éxito
        self._lbl_estado_red.setStyleSheet(  # Cambia estilo del mensaje
            f"color: {VERDE}; background: transparent; border: none;"  # Color verde de éxito
        )
        QTimer.singleShot(800, self._iniciar)  # Espera 800 ms y ejecuta iniciar juego

    def _en_error_red(self, mensaje: str):  # Método ejecutado cuando ocurre un error
        """Muestra el error de conexión en la UI."""  # Explicación del método
        self._lbl_estado_red.setText(f"❌  Error: {mensaje}")  # Muestra mensaje de error
        self._lbl_estado_red.setStyleSheet(  # Cambia estilo del mensaje
            f"color: {ROJO}; background: transparent; border: none;"  # Color rojo de error
        )

        # Rehabilitar botones  # Comentario explicativo
        btn = getattr(self, "_btn_crear_sala", None) or getattr(self, "_btn_unirse", None)  # Obtiene botón disponible

        if btn:  # Verifica si existe el botón
            btn.setEnabled(True)  # Reactiva el botón

    #  NAVEGACIÓN  # Sección de navegación entre pantallas

    def _volver(self):  # Método para volver al menú principal
        musica.iniciar()  # Reproduce música del menú
        from pantalla.inicio import PantallaInicio  # Importa la pantalla inicial
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))  # Cambia a la pantalla de inicio

    def _iniciar(self):  # Método que inicia el juego
        nombre_j1 = self.campo_j1.text().strip() or "Jugador 1"  # Obtiene nombre del jugador 1
        nombre_j2 = self.campo_j2.text().strip() or "Jugador 2"  # Obtiene nombre del jugador 2
        ip_red    = ""  # Variable para guardar la IP de red

        if self.modo_red == "cliente":  # Verifica si el modo es cliente
            ip_red = getattr(self, "_ip_anfitrion", "")  # Obtiene IP del anfitrión

        from pantalla.juego import PantallaJuego  # Importa la pantalla del juego

        self.ventana.setCentralWidget(  # Cambia la pantalla actual
            PantallaJuego(  # Crea la pantalla del juego
                self.ventana,  # Envía la ventana principal
                nombre_j1  = nombre_j1,  # Envía nombre del jugador 1
                nombre_j2  = nombre_j2,  # Envía nombre del jugador 2
                ip_red     = ip_red,  # Envía IP de red
                modo_red   = self.modo_red,  # Envía modo de red
                color_j1   = self.color_j1,  # Envía color del jugador 1
                color_j2   = self.color_j2,  # Envía color del jugador 2
            )
        ) 
