"""
utilidad/estilos.py — Colores y estilos globales de SNAKEVERSE
Paleta basada en el logo pixel-art oficial del juego.
"""

# ── Colores de fondo ──────────────────────────────────────────
FONDO_OSCURO  = "#0F0F1A"   # negro-azul principal
FONDO_MEDIO   = "#161625"   # tarjetas y paneles
FONDO_CLARO   = "#1C1C30"   # elementos resaltados
BORDE         = "#3A3050"   # borde normal
BORDE_ACTIVO  = "#6A50A0"   # borde morado resaltado

# ── Colores del logo ──────────────────────────────────────────
DORADO        = "#F5A800"   # dorado del texto SNAKEVERSE
DORADO_CLARO  = "#FFD040"   # highlight dorado
VERDE         = "#2ECC40"   # jugador 1 (verde logo)
VERDE_OSCURO  = "#1A8C28"
AZUL          = "#209AE8"   # jugador 2 (azul logo)
AZUL_OSCURO   = "#1464A8"
ROJO          = "#E83030"   # peligro / salir
NARANJA       = "#E87020"   # acento / turbo activo
MORADO        = "#9040E0"   # power-ups
CIAN          = "#20D8E0"   # red / conexión
BLANCO_CALIDO = "#F0EAD8"   # texto principal
GRIS          = "#8878A8"   # texto secundario apagado


# ── Funciones de estilo para botones ─────────────────────────

def estilo_boton_base():
    """Botón estándar gris-morado."""
    return f"""
        QPushButton {{
            background-color: {FONDO_MEDIO};
            color: {BLANCO_CALIDO};
            border: 2px solid {BORDE_ACTIVO};
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            border-color: {DORADO};
            color: {DORADO};
            background-color: #22183A;
        }}
        QPushButton:pressed {{
            background-color: #2E2050;
        }}
    """

def estilo_boton_verde():
    """Botón principal de acción — verde vibrante."""
    return f"""
        QPushButton {{
            background-color: #0A1E10;
            color: {VERDE};
            border: 2px solid {VERDE};
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            padding: 12px 24px;
        }}
        QPushButton:hover {{
            background-color: #0F2A18;
            border-color: {DORADO};
            color: {DORADO};
        }}
        QPushButton:pressed {{
            background-color: #163020;
        }}
    """

def estilo_boton_rojo():
    """Botón de peligro — rojo."""
    return f"""
        QPushButton {{
            background-color: #1E0808;
            color: {ROJO};
            border: 2px solid {ROJO};
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #2E1010;
            color: #FF5555;
            border-color: #FF5555;
        }}
    """

def estilo_boton_dorado():
    """Botón dorado — puntuaciones / resultados."""
    return f"""
        QPushButton {{
            background-color: #1E1400;
            color: {DORADO};
            border: 2px solid {DORADO};
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #2A1E00;
            color: {DORADO_CLARO};
            border-color: {DORADO_CLARO};
        }}
    """

def estilo_boton_azul():
    """Botón azul — música / red."""
    return f"""
        QPushButton {{
            background-color: #081420;
            color: {AZUL};
            border: 2px solid {AZUL};
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #0C1E30;
            color: #40C8FF;
            border-color: #40C8FF;
        }}
    """

def estilo_boton_morado():
    """Botón morado — ajustes / controles."""
    return f"""
        QPushButton {{
            background-color: #120820;
            color: {MORADO};
            border: 2px solid {MORADO};
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #1A0E30;
            color: #C080FF;
            border-color: #C080FF;
        }}
    """

def estilo_input():
    """Campo de texto estilizado."""
    return f"""
        QLineEdit {{
            background-color: {FONDO_MEDIO};
            color: {BLANCO_CALIDO};
            border: 2px solid {BORDE_ACTIVO};
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border-color: {DORADO};
            color: {DORADO_CLARO};
        }}
    """

def estilo_ventana():
    # fondo general de la ventana
    return f"background-color: {FONDO_OSCURO};"