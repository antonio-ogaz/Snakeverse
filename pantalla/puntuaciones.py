"""
pantalla/puntuaciones.py — Tabla de puntuaciones altas
"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

from utilidad.estilos import (
    DORADO, GRIS, FONDO_CLARO, BORDE_ACTIVO,
    estilo_ventana, estilo_boton_base, estilo_boton_rojo,
)

ARCHIVO_PUNTUACIONES = "puntuaciones.json"


def cargar_puntuaciones() -> list:
    """Carga del JSON guardado o retorna lista vacía."""
    if os.path.exists(ARCHIVO_PUNTUACIONES):
        try:
            with open(ARCHIVO_PUNTUACIONES, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos and isinstance(datos, list):
                    # Filtrar solo entradas que son diccionarios
                    return [d for d in datos if isinstance(d, dict)]
        except Exception:
            pass
    return []


class PantallaPuntuaciones(QWidget):
    def __init__(self, ventana_principal=None):
        super().__init__(ventana_principal)
        self.ventana = ventana_principal
        self.setStyleSheet(estilo_ventana())
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(14)

        # Título
        lbl_titulo = QLabel("⭐  PUNTUACIONES ALTAS")
        lbl_titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))
        lbl_titulo.setStyleSheet(f"color: {DORADO}; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        lbl_sub = QLabel("Los mejores jugadores de SNAKEVERSE")
        lbl_sub.setFont(QFont("Segoe UI", 11))
        lbl_sub.setStyleSheet(f"color: {GRIS}; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        layout.addSpacing(8)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["🏅 PUESTO", "JUGADOR", "PUNTOS", "RONDAS", "FECHA"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {FONDO_CLARO};
                border: 2px solid {BORDE_ACTIVO};
                border-radius: 8px;
                gridline-color: #282840;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 8px 14px;
                border-bottom: 1px solid #202038;
            }}
            QTableWidget::item:selected {{
                background-color: #2A1E00;
                color: {DORADO};
            }}
            QTableWidget::item:alternate {{
                background-color: #161625;
            }}
            QHeaderView::section {{
                background-color: #0C0C1A;
                color: {DORADO};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {DORADO};
            }}
        """)
        layout.addWidget(self.tabla)
        self._llenar_tabla()

        # Botones
        fila = QHBoxLayout()
        fila.setSpacing(14)
        btn_limpiar = QPushButton("🗑  LIMPIAR HISTORIAL")
        btn_volver = QPushButton("← VOLVER AL MENÚ")
        btn_limpiar.setStyleSheet(estilo_boton_rojo())
        btn_volver.setStyleSheet(estilo_boton_base())
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_volver.setCursor(Qt.PointingHandCursor)
        fila.addStretch()
        fila.addWidget(btn_limpiar)
        fila.addWidget(btn_volver)
        fila.addStretch()
        layout.addLayout(fila)

        btn_limpiar.clicked.connect(self._limpiar)
        btn_volver.clicked.connect(self._volver)

    def _llenar_tabla(self):
        medallas = ["🥇", "🥈", "🥉"]
        colores = {
            0: QColor(DORADO),
            1: QColor("#C8C8C8"),
            2: QColor("#CD7F32"),
        }
        lista = cargar_puntuaciones()
        self.tabla.setRowCount(0)

        for pos, entrada in enumerate(lista[:20]):
            self.tabla.insertRow(pos)

            # Asegurar que entrada es un diccionario
            if isinstance(entrada, dict):
                nombre = entrada.get("nombre", "—")
                puntos = str(entrada.get("puntos", 0))
                rondas = entrada.get("rondas", "—")
                fecha = entrada.get("fecha", "—")
            else:
                # Si no es diccionario, ignorar esta entrada
                continue

            puesto = medallas[pos] if pos < 3 else str(pos + 1)
            valores = [puesto, nombre, puntos, rondas, fecha]

            for col, valor in enumerate(valores):
                celda = QTableWidgetItem(valor)
                celda.setTextAlignment(Qt.AlignCenter)
                if pos in colores:
                    celda.setForeground(colores[pos])
                self.tabla.setItem(pos, col, celda)

        # Si no hay datos, mostrar mensaje
        if len(lista) == 0:
            self.tabla.setRowCount(1)
            celda = QTableWidgetItem("📭  No hay puntuaciones registradas  📭")
            celda.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(0, 0, celda)
            # Unir celdas
            self.tabla.setSpan(0, 0, 1, 5)

    def _limpiar(self):
        if os.path.exists(ARCHIVO_PUNTUACIONES):
            os.remove(ARCHIVO_PUNTUACIONES)
        self._llenar_tabla()

    def _volver(self):
        from pantalla.inicio import PantallaInicio
        self.ventana.setCentralWidget(PantallaInicio(self.ventana))