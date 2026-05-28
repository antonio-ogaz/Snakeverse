"""
utilidad/musica.py — Gestor global de música de fondo
"""
import os
import sys
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


def _ruta_base():
    """Obtiene la ruta base, funciona en desarrollo y empaquetado"""
    try:
        # Cuando está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # Cuando se ejecuta desde el código fuente
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_path


def _ruta_musica() -> str:
    # Ruta de musica
    return os.path.join(_ruta_base(), "recursos", "Sonido.mp3")


class GestorMusica:
    """
    Reproductor de música de fondo con ciclo de vida independiente
    a las pantallas. Se inicializa una sola vez y persiste.
    """

    def __init__(self):
        self._reproductor        = None
        self._salida_audio       = None
        self._iniciado           = False
        self._volumen            = 0.70
        self._pausado_por_usuario = False

    def _configurar(self):
        if self._iniciado:
            return
        self._salida_audio = QAudioOutput()
        self._salida_audio.setVolume(self._volumen)
        self._reproductor  = QMediaPlayer()
        self._reproductor.setAudioOutput(self._salida_audio)
        self._reproductor.setSource(QUrl.fromLocalFile(_ruta_musica()))
        self._reproductor.mediaStatusChanged.connect(self._reiniciar)
        self._iniciado = True

    def _reiniciar(self, estado):
        if estado == QMediaPlayer.MediaStatus.EndOfMedia:
            self._reproductor.setPosition(0)
            self._reproductor.play()

    def iniciar(self):
        self._configurar()
        if not self._pausado_por_usuario:
            estado = self._reproductor.playbackState()
            if estado != QMediaPlayer.PlaybackState.PlayingState:
                self._reproductor.play()

    def pausar(self):
        if self._iniciado and self._reproductor:
            self._pausado_por_usuario = True
            self._reproductor.pause()

    def reanudar(self):
        if self._iniciado and self._reproductor:
            self._pausado_por_usuario = False
            self._reproductor.play()

    def alternar(self):
        if not self._iniciado:
            self.iniciar()
            return
        estado = self._reproductor.playbackState()
        if estado == QMediaPlayer.PlaybackState.PlayingState:
            self._pausado_por_usuario = True
            self._reproductor.pause()
        else:
            self._pausado_por_usuario = False
            self._reproductor.play()

    def esta_activa(self) -> bool:
        if not self._iniciado or not self._reproductor:
            return False
        return (self._reproductor.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState)

    def ajustar_volumen(self, valor: float):
        self._volumen = max(0.0, min(1.0, valor))
        if self._salida_audio:
            self._salida_audio.setVolume(self._volumen)

    def cambiar_volumen(self, valor: int):
        volumen_float = valor / 100.0
        self.ajustar_volumen(volumen_float)

    def obtener_volumen(self) -> int:
        return int(self._volumen * 100)


# Instancia global
musica = GestorMusica()