"""
pantalla/puntuaciones.py — Tabla de puntuaciones altas  # Nombre del módulo
""" 

import json  # Importa manejo de archivos JSON
import os  # Importa manejo del sistema operativo

from PySide6.QtWidgets import (  # Importa widgets de PySide6
    QWidget, QVBoxLayout, QHBoxLayout,  # Widgets de contenedores
    QLabel, QPushButton, QTableWidget,  # Widgets de interfaz
    QTableWidgetItem, QHeaderView,  # Widgets de tabla
)  # Fin de importación

from PySide6.QtGui import QFont, QColor  # Importa fuentes y colores
from PySide6.QtCore import Qt  # Importa constantes Qt

from utilidad.estilos import (  # Importa estilos personalizados
    DORADO, GRIS, FONDO_CLARO, BORDE_ACTIVO,  # Colores personalizados
    estilo_ventana, estilo_boton_base, estilo_boton_rojo,  # Funciones de estilos
)  # Fin de importación

ARCHIVO_PUNTUACIONES = "puntuaciones.json"  # Nombre del archivo JSON


def cargar_puntuaciones() -> list:  # Función para cargar puntuaciones
    """Carga del JSON guardado o retorna lista vacía."""  # Descripción de función
    if os.path.exists(ARCHIVO_PUNTUACIONES):  # Verifica si existe el archivo
        try:  # Intenta abrir el archivo
            with open(ARCHIVO_PUNTUACIONES, "r", encoding="utf-8") as f:  # Abre archivo
                datos = json.load(f)  # Carga datos JSON
                if datos and isinstance(datos, list):  # Verifica que sea lista
                    return [d for d in datos if isinstance(d, dict)]  # Retorna solo diccionarios
        except Exception:  # Captura errores
            pass  # Ignora errores
    return []  # Retorna lista vacía


class PantallaPuntuaciones(QWidget):  # Clase principal de puntuaciones

    def __init__(self, ventana_principal=None):  # Constructor
        super().__init__(ventana_principal)  # Inicializa QWidget
        self.ventana = ventana_principal  # Guarda referencia de ventana
        self.setStyleSheet(estilo_ventana())  # Aplica estilo general
        self._construir_interfaz()  # Construye interfaz

    def _construir_interfaz(self):  # Método para construir interfaz
        layout = QVBoxLayout(self)  # Layout principal vertical
        layout.setContentsMargins(50, 30, 50, 30)  # Márgenes
        layout.setSpacing(14)  # Espaciado

        lbl_titulo = QLabel("PUNTUACIONES ALTAS")  # Etiqueta de título
        lbl_titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))  # Fuente del título
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")  # Estilo
        lbl_titulo.setAlignment(Qt.AlignCenter)  # Centra texto
        layout.addWidget(lbl_titulo)  # Agrega título

        lbl_sub = QLabel("Los mejores jugadores de SNAKEVERSE")  # Subtítulo
        lbl_sub.setFont(QFont("Segoe UI", 11))  # Fuente subtítulo
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")  # Estilo
        lbl_sub.setAlignment(Qt.AlignCenter)  # Centra texto
        layout.addWidget(lbl_sub)  # Agrega subtítulo

        layout.addSpacing(8)  # Espacio extra

        self.tabla = QTableWidget()  # Crea tabla
        self.tabla.setColumnCount(5)  # Define columnas

        self.tabla.setHorizontalHeaderLabels(  # Define encabezados
            ["PUESTO", "JUGADOR", "PUNTOS", "RONDAS", "FECHA"]  # Lista encabezados
        )  # Fin encabezados

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ajusta columnas
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)  # Deshabilita edición
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)  # Selecciona filas
        self.tabla.verticalHeader().setVisible(False)  # Oculta encabezado vertical
        self.tabla.setAlternatingRowColors(True)  # Alterna colores

        self.tabla.setStyleSheet(f"""  # Estilo tabla
            QTableWidget {{  # Tabla principal
                background-color: {FONDO_CLARO};  # Fondo
                border: 2px solid {BORDE_ACTIVO};  # Borde
                border-radius: 8px;  # Bordes redondeados
                gridline-color: #282840;  # Color líneas
                font-size: 13px;  # Tamaño texto
                outline: none;  # Sin borde foco
            }}
            QTableWidget::item {{  # Celdas
                padding: 8px 14px;  # Espaciado interno
                border-bottom: 1px solid #202038;  # Línea inferior
            }}
            QTableWidget::item:selected {{  # Celda seleccionada
                background-color: #2A1E00;  # Fondo selección
                color: {DORADO};  # Color texto
            }}
            QTableWidget::item:alternate {{  # Filas alternas
                background-color: #161625;  # Fondo alterno
            }}
            QHeaderView::section {{  # Encabezados
                background-color: #0C0C1A;  # Fondo encabezado
                color: {DORADO};  # Color texto
                font-size: 11px;  # Tamaño texto
                font-weight: bold;  # Texto negrita
                letter-spacing: 2px;  # Espaciado letras
                padding: 8px 12px;  # Espaciado interno
                border: none;  # Sin borde
                border-bottom: 2px solid {DORADO};  # Línea inferior
            }}
        """)  # Fin estilo tabla

        layout.addWidget(self.tabla)  # Agrega tabla
        self._llenar_tabla()  # Llena tabla

        fila = QHBoxLayout()  # Layout horizontal botones
        fila.setSpacing(14)  # Espaciado botones

        btn_limpiar = QPushButton("LIMPIAR HISTORIAL")  # Botón limpiar
        btn_volver = QPushButton("VOLVER AL MENÚ")  # Botón volver

        btn_limpiar.setStyleSheet(estilo_boton_rojo())  # Estilo botón limpiar
        btn_volver.setStyleSheet(estilo_boton_base())  # Estilo botón volver

        btn_limpiar.setCursor(Qt.PointingHandCursor)  # Cursor mano
        btn_volver.setCursor(Qt.PointingHandCursor)  # Cursor mano

        fila.addStretch()  # Espaciador
        fila.addWidget(btn_limpiar)  # Agrega botón limpiar
        fila.addWidget(btn_volver)  # Agrega botón volver
        fila.addStretch()  # Espaciador

        layout.addLayout(fila)  # Agrega fila botones

        btn_limpiar.clicked.connect(self._limpiar)  # Conecta botón limpiar
        btn_volver.clicked.connect(self._volver)  # Conecta botón volver

    def _llenar_tabla(self):  # Método llenar tabla

        colores = {  # Diccionario colores
            0: QColor(DORADO),  # Primer lugar
            1: QColor("#C8C8C8"),  # Segundo lugar
            2: QColor("#CD7F32"),  # Tercer lugar
        }  # Fin diccionario

        lista = cargar_puntuaciones()  # Carga puntuaciones
        self.tabla.setRowCount(0)  # Reinicia filas

        for pos, entrada in enumerate(lista[:20]):  # Recorre top 20
            self.tabla.insertRow(pos)  # Inserta fila

            if isinstance(entrada, dict):  # Verifica diccionario
                nombre = entrada.get("nombre", "—")  # Obtiene nombre
                puntos = str(entrada.get("puntos", 0))  # Obtiene puntos
                rondas = entrada.get("rondas", "—")  # Obtiene rondas
                fecha = entrada.get("fecha", "—")  # Obtiene fecha
            else:  # Si no es válido
                continue  # Continúa ciclo

            puesto = str(pos + 1)  # Número posición
            valores = [puesto, nombre, puntos, rondas, fecha]  # Lista valores

            for col, valor in enumerate(valores):  # Recorre columnas
                celda = QTableWidgetItem(valor)  # Crea celda
                celda.setTextAlignment(Qt.AlignCenter)  # Centra texto

                if pos in colores:  # Verifica posición especial
                    celda.setForeground(colores[pos])  # Aplica color

                self.tabla.setItem(pos, col, celda)  # Inserta celda

        if len(lista) == 0:  # Si no hay datos
            self.tabla.setRowCount(1)  # Crea una fila

            celda = QTableWidgetItem("No hay puntuaciones registradas")  # Mensaje vacío
            celda.setTextAlignment(Qt.AlignCenter)  # Centra mensaje

            self.tabla.setItem(0, 0, celda)  # Inserta mensaje
            self.tabla.setSpan(0, 0, 1, 5)  # Une columnas

    def _limpiar(self):  # Método limpiar historial
        if os.path.exists(ARCHIVO_PUNTUACIONES):  # Verifica archivo
            os.remove(ARCHIVO_PUNTUACIONES)  # Elimina archivo

        self._llenar_tabla()  # Actualiza tabla

    def _volver(self):  # Método volver
        from pantalla.inicio import PantallaInicio  # Importa pantalla inicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))  # Cambia pantalla
       
