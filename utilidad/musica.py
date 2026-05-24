"""
utilidad/musica.py — Gestor global de música de fondo
"""
import os
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


def _ruta_musica() -> str:
    #ruta de musica
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raiz, "recursos", "Sonido.mp3")

class GestorMusica:
    """
    Reproductor de música de fondo con ciclo de vida independiente
    a las pantallas. Se inicializa una sola vez y persiste.
    """

    def __init__(self):
        self._reproductor  = None
        self._salida_audio = None
        self._iniciado     = False
        self._volumen      = 0.70

    def _configurar(self):
        #crea el reproductor
        if self._iniciado:
            return
        self._salida_audio = QAudioOutput()
        self._salida_audio.setVolume(self._volumen)
        self._reproductor  = QMediaPlayer()
        self._reproductor.setAudioOutput(self._salida_audio)
        self._reproductor.setSource(QUrl.fromLocalFile(_ruta_musica()))
        # Loop automático al terminar la canción
        self._reproductor.mediaStatusChanged.connect(self._reiniciar)
        self._iniciado = True

    def _reiniciar(self, estado):
        # Se reinicia la cancion
        if estado == QMediaPlayer.MediaStatus.EndOfMedia:
            self._reproductor.setPosition(0)
            self._reproductor.play()

    def iniciar(self):
        #inicia la reproduccion si no esta
        self._configurar()
        estado = self._reproductor.playbackState()
        if estado != QMediaPlayer.PlaybackState.PlayingState:
            self._reproductor.play()

    def pausar(self):
        #pausa la musica
        if self._iniciado and self._reproductor:
            self._reproductor.pause()

    def reanudar(self):
        #reaunuda la musica
        if self._iniciado and self._reproductor:
            self._reproductor.play()

    def alternar(self):
        #Pausa si estaba reproduciendo, reanuda si estaba pausada.
        if not self._iniciado:
            self.iniciar()
            return
        estado = self._reproductor.playbackState()
        if estado == QMediaPlayer.PlaybackState.PlayingState:
            self._reproductor.pause()
        else:
            self._reproductor.play()

    def esta_activa(self) -> bool:
        #True si la música está reproduciéndose en este momento.
        if not self._iniciado or not self._reproductor:
            return False
        return (self._reproductor.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState)

    def ajustar_volumen(self, valor: float):
        # Ajusta el volumen (0.0 a 1.0)
        self._volumen = max(0.0, min(1.0, valor))
        if self._salida_audio:
            self._salida_audio.setVolume(self._volumen)

    # MÉTODOS PARA COMPATIBILIDAD CON AJUSTES

    def cambiar_volumen(self, valor: int):
        """
        Cambia el volumen usando un valor entero de 0 a 100.
        Convierte a float (0.0-1.0) para QAudioOutput.
        """
        volumen_float = valor / 100.0
        self.ajustar_volumen(volumen_float)

    def obtener_volumen(self) -> int:
        """
        Retorna el volumen actual como entero entre 0 y 100.
        """
        return int(self._volumen * 100)


# Instancia global
musica = GestorMusica()