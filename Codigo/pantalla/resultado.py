"""  # Descripción del archivo
pantalla/resultado.py — Pantalla de resultados al final de la partida  # Nombre del módulo
"""  # Fin descripción

from PySide6.QtWidgets import (  # Importa widgets de PySide6
    QWidget, QVBoxLayout, QHBoxLayout,  # Layouts y contenedores
    QLabel, QPushButton, QFrame,  # Widgets visuales
)  # Fin importación

from PySide6.QtGui import QFont, QPixmap  # Importa fuentes e imágenes
from PySide6.QtCore import Qt  # Importa constantes Qt

from utilidad.estilos import (  # Importa estilos personalizados
    DORADO, VERDE, AZUL, GRIS, BLANCO_CALIDO,  # Colores personalizados
    FONDO_OSCURO, FONDO_MEDIO,  # Fondos personalizados
    estilo_boton_verde, estilo_boton_rojo,  # Estilos botones
)  # Fin importación


class PantallaResultado(QWidget):  # Clase pantalla resultado
    """  # Documentación clase
    Pantalla que muestra el resultado final de la partida:  # Descripción
    """  # Fin documentación

    def __init__(self, ventana_principal=None,  # Constructor
                 nombre_ganador: str = "",  # Nombre ganador
                 victorias: list = None,  # Lista victorias
                 puntos: list = None,  # Lista puntos
                 nombres: list = None):  # Lista nombres

        super().__init__(ventana_principal)  # Inicializa QWidget

        self.ventana = ventana_principal  # Guarda ventana principal
        self.nombre_ganador = nombre_ganador  # Guarda ganador
        self.victorias = victorias if victorias else [0, 0]  # Guarda victorias
        self.puntos = puntos if puntos else [0, 0]  # Guarda puntos
        self.nombres = nombres if nombres else ["Jugador 1", "Jugador 2"]  # Guarda nombres

        self.setStyleSheet(f"background-color: {FONDO_OSCURO};")  # Fondo ventana
        self._construir_interfaz()  # Construye interfaz

    def _construir_interfaz(self):  # Método interfaz

        layout = QVBoxLayout(self)  # Layout principal vertical
        layout.setContentsMargins(60, 40, 60, 40)  # Márgenes
        layout.setSpacing(20)  # Espaciado

        lbl_titulo = QLabel("RESULTADO FINAL")  # Título principal
        lbl_titulo.setFont(QFont("Segoe UI", 28, QFont.Bold))  # Fuente título
        lbl_titulo.setStyleSheet(f"color: {DORADO};")  # Color título
        lbl_titulo.setAlignment(Qt.AlignCenter)  # Centra texto
        layout.addWidget(lbl_titulo)  # Agrega título

        lbl_ganador = QLabel(f"{self.nombre_ganador.upper()} ES EL CAMPEÓN")  # Texto ganador
        lbl_ganador.setFont(QFont("Segoe UI", 20, QFont.Bold))  # Fuente ganador
        lbl_ganador.setStyleSheet(f"color: {VERDE};")  # Color ganador
        lbl_ganador.setAlignment(Qt.AlignCenter)  # Centra texto
        layout.addWidget(lbl_ganador)  # Agrega texto ganador

        linea = QFrame()  # Línea decorativa
        linea.setFrameShape(QFrame.HLine)  # Línea horizontal
        linea.setStyleSheet(f"background-color: {DORADO}; max-height: 2px;")  # Estilo línea
        layout.addWidget(linea)  # Agrega línea

        layout.addSpacing(20)  # Espacio extra

        frame_puntuaciones = QFrame()  # Frame puntuaciones

        frame_puntuaciones.setStyleSheet(f"""  # Estilo frame
            QFrame {{  # Inicio QFrame
                background-color: {FONDO_MEDIO};  # Fondo frame
                border-radius: 15px;  # Bordes redondos
                border: 2px solid {DORADO};  # Borde dorado
            }}  # Fin QFrame
        """)  # Fin estilos

        layout_punt = QVBoxLayout(frame_puntuaciones)  # Layout puntuaciones
        layout_punt.setContentsMargins(30, 20, 30, 20)  # Márgenes internos
        layout_punt.setSpacing(15)  # Espaciado interno

        lbl_sub = QLabel("ESTADÍSTICAS DE LA PARTIDA")  # Subtítulo
        lbl_sub.setFont(QFont("Segoe UI", 14, QFont.Bold))  # Fuente subtítulo
        lbl_sub.setStyleSheet(f"color: {DORADO};")  # Color subtítulo
        lbl_sub.setAlignment(Qt.AlignCenter)  # Centra texto
        layout_punt.addWidget(lbl_sub)  # Agrega subtítulo

        lbl_j1 = QLabel(  # Label jugador 1
            f"{self.nombres[0].upper()}  →  "  # Nombre jugador 1
            f"{self.victorias[0]} victorias  |  {self.puntos[0]} puntos"  # Datos jugador 1
        )  # Fin texto

        lbl_j1.setFont(QFont("Segoe UI", 13))  # Fuente jugador 1
        lbl_j1.setStyleSheet(f"color: {VERDE}; padding: 8px;")  # Estilo jugador 1
        lbl_j1.setAlignment(Qt.AlignCenter)  # Centra texto
        layout_punt.addWidget(lbl_j1)  # Agrega jugador 1

        lbl_j2 = QLabel(  # Label jugador 2
            f"{self.nombres[1].upper()}  →  "  # Nombre jugador 2
            f"{self.victorias[1]} victorias  |  {self.puntos[1]} puntos"  # Datos jugador 2
        )  # Fin texto

        lbl_j2.setFont(QFont("Segoe UI", 13))  # Fuente jugador 2
        lbl_j2.setStyleSheet(f"color: {AZUL}; padding: 8px;")  # Estilo jugador 2
        lbl_j2.setAlignment(Qt.AlignCenter)  # Centra texto
        layout_punt.addWidget(lbl_j2)  # Agrega jugador 2

        resultado_texto = f"RESULTADO: {self.victorias[0]} - {self.victorias[1]}"  # Resultado final

        lbl_resultado = QLabel(resultado_texto)  # Label resultado
        lbl_resultado.setFont(QFont("Segoe UI", 16, QFont.Bold))  # Fuente resultado
        lbl_resultado.setStyleSheet(f"color: {DORADO}; padding: 10px;")  # Estilo resultado
        lbl_resultado.setAlignment(Qt.AlignCenter)  # Centra texto
        layout_punt.addWidget(lbl_resultado)  # Agrega resultado

        layout.addWidget(frame_puntuaciones)  # Agrega frame puntuaciones

        layout.addStretch()  # Espaciador flexible

        layout_botones = QHBoxLayout()  # Layout horizontal botones
        layout_botones.setSpacing(20)  # Espaciado botones

        btn_menu = QPushButton("VOLVER AL MENÚ")  # Botón menú
        btn_menu.setStyleSheet(estilo_boton_rojo())  # Estilo botón menú
        btn_menu.setMinimumHeight(50)  # Altura mínima
        btn_menu.setMinimumWidth(200)  # Anchura mínima
        btn_menu.setCursor(Qt.PointingHandCursor)  # Cursor mano
        btn_menu.clicked.connect(self._volver_menu)  # Evento clic

        btn_salir = QPushButton("SALIR")  # Botón salir
        btn_salir.setStyleSheet(estilo_boton_rojo())  # Estilo botón salir
        btn_salir.setMinimumHeight(50)  # Altura mínima
        btn_salir.setMinimumWidth(150)  # Anchura mínima
        btn_salir.setCursor(Qt.PointingHandCursor)  # Cursor mano
        btn_salir.clicked.connect(self._salir)  # Evento clic

        layout_botones.addStretch()  # Espaciador
        layout_botones.addWidget(btn_menu)  # Agrega botón menú
        layout_botones.addWidget(btn_salir)  # Agrega botón salir
        layout_botones.addStretch()  # Espaciador

        layout.addLayout(layout_botones)  # Agrega layout botones

    def _volver_menu(self):  # Método volver menú
        from pantalla.inicio import PantallaInicio  # Importa pantalla inicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))  # Cambia pantalla

    def _salir(self):  # Método salir
        self.ventana.close()  # Cierra ventana
    
