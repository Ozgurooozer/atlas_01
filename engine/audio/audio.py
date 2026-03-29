"""
Audio Subsystem - Sound and Music playback.

pyglet audio backend kullanarak ses efektleri ve müzik çalar.

Layer: 2 (Engine)
Dependencies: ISubsystem (Layer 2), pyglet (Layer 0)
"""

from __future__ import annotations

from typing import Dict, Optional

from engine.subsystem import ISubsystem


class Sound:
    """
    Kısa ses efekti.

    Bellekte tutulur, hızlı erişim için.
    pyglet.media.StaticSource kullanır.
    """

    def __init__(self, source=None):
        """Sound oluştur."""
        self._source = source
        self._player = None

    @property
    def source(self):
        """pyglet source."""
        return self._source


class Music:
    """
    Uzun müzik dosyası.

    Streaming olarak çalınır, bellek dostu.
    pyglet.media.Source kullanır.
    """

    def __init__(self, source=None):
        """Music oluştur."""
        self._source = source

    @property
    def source(self):
        """pyglet source."""
        return self._source


class AudioSystem(ISubsystem):
    """
    Ses sistemi.

    Sound effect'ler ve background music yönetir.
    pyglet.media backend kullanır.

    Example:
        >>> audio = AudioSystem()
        >>> audio.initialize()
        >>> sound = audio.load_sound("explosion.wav")
        >>> audio.play(sound)
    """

    def __init__(self):
        """AudioSystem oluştur."""
        self._initialized = False
        self._volume: float = 1.0
        self._music_volume: float = 1.0
        self._sounds: Dict[str, Sound] = {}
        self._music: Dict[str, Music] = {}
        self._current_music_player = None
        self._sound_players = []

    @property
    def name(self) -> str:
        """Subsystem adı."""
        return "audio"

    @property
    def volume(self) -> float:
        """Genel ses seviyesi (0.0 - 1.0)."""
        return self._volume

    @property
    def music_volume(self) -> float:
        """Müzik ses seviyesi (0.0 - 1.0)."""
        return self._music_volume

    def initialize(self, engine=None) -> None:
        """Audio sistemini başlat."""
        self._initialized = True

    def shutdown(self) -> None:
        """Audio sistemini kapat."""
        self.stop_all()
        self.stop_music()
        self._initialized = False

    def tick(self, dt: float) -> None:
        """
        Audio tick.

        Args:
            dt: Delta time (saniye).
        """
        # pyglet sesleri otomatik yönetir
        pass

    def load_sound(self, path: str) -> Sound:
        """
        Ses efekti yükle.

        Args:
            path: Ses dosyası yolu.

        Returns:
            Sound nesnesi.
        """
        if path in self._sounds:
            return self._sounds[path]

        try:
            import pyglet.media as media

            source = media.load(path, streaming=False)
            sound = Sound(source)
            self._sounds[path] = sound
            return sound
        except Exception:
            # Headless veya dosya yok - dummy sound
            return Sound(None)

    def load_music(self, path: str) -> Music:
        """
        Müzik dosyası yükle.

        Args:
            path: Müzik dosyası yolu.

        Returns:
            Music nesnesi.
        """
        if path in self._music:
            return self._music[path]

        try:
            import pyglet.media as media

            source = media.load(path, streaming=True)
            music = Music(source)
            self._music[path] = music
            return music
        except Exception:
            # Headless veya dosya yok - dummy music
            return Music(None)

    def play(self, sound: Sound) -> None:
        """
        Ses efekti çal.

        Args:
            sound: Sound nesnesi.
        """
        if sound._source is None:
            return

        try:
            import pyglet.media as media

            player = media.Player()
            player.volume = self._volume
            player.queue(sound._source)
            player.play()
            self._sound_players.append(player)
        except Exception:
            pass

    def play_music(self, music: Music, loop: bool = False) -> None:
        """
        Müzik çal.

        Args:
            music: Music nesnesi.
            loop: Döngüsel çalsın mı?
        """
        # Önceki müziği durdur
        self.stop_music()

        if music._source is None:
            return

        try:
            import pyglet.media as media

            self._current_music_player = media.Player()
            self._current_music_player.volume = self._music_volume
            self._current_music_player.queue(music._source)

            if loop:
                self._current_music_player.loop = True

            self._current_music_player.play()
        except Exception:
            pass

    def stop_music(self) -> None:
        """Müziği durdur."""
        if self._current_music_player:
            try:
                self._current_music_player.pause()
                self._current_music_player.delete()
            except Exception:
                pass
            self._current_music_player = None

    def stop_all(self) -> None:
        """Tüm sesleri durdur."""
        for player in self._sound_players:
            try:
                player.pause()
                player.delete()
            except Exception:
                pass
        self._sound_players.clear()
        self.stop_music()

    def set_volume(self, volume: float) -> None:
        """
        Genel ses seviyesini ayarla.

        Args:
            volume: Seviye (0.0 - 1.0).
        """
        self._volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float) -> None:
        """
        Müzik ses seviyesini ayarla.

        Args:
            volume: Seviye (0.0 - 1.0).
        """
        self._music_volume = max(0.0, min(1.0, volume))
        if self._current_music_player:
            try:
                self._current_music_player.volume = self._music_volume
            except Exception:
                pass


__all__ = ['AudioSystem', 'Sound', 'Music']
