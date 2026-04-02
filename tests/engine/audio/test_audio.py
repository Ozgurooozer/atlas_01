"""
Tests for Audio Subsystem - Sound and Music playback.

Layer: 2 (Engine)
Dependencies: ISubsystem, pyglet audio (hal)

TDD Phase: RED - Bu testler implementation'dan ÖNCE yazıldı.
"""



class TestAudioBasics:
    """Audio temel özellik testleri."""

    def test_audio_module_exists(self):
        """Audio modülü olmalı."""
        from engine.audio import audio
        assert audio is not None

    def test_audio_system_exists(self):
        """AudioSystem sınıfı olmalı."""
        from engine.audio.audio import AudioSystem
        assert AudioSystem is not None

    def test_audio_system_is_subsystem(self):
        """AudioSystem ISubsystem implemente etmeli."""
        from engine.audio.audio import AudioSystem
        from engine.subsystem import ISubsystem

        # Interface check
        assert issubclass(AudioSystem, ISubsystem)

    def test_audio_system_creation(self):
        """AudioSystem oluşturulabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()
        assert audio is not None


class TestSoundEffects:
    """Sound effect testleri."""

    def test_load_sound(self):
        """Ses dosyası yüklenebilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        # Headless ortamda dummy sound
        sound = audio.load_sound("test.wav")
        assert sound is not None

    def test_play_sound(self):
        """Ses çalınabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        sound = audio.load_sound("test.wav")
        # Headless'ta hata vermemeli
        audio.play(sound)

    def test_sound_volume(self):
        """Ses seviesi ayarlanabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        audio.set_volume(0.5)
        assert audio.volume == 0.5

    def test_stop_all_sounds(self):
        """Tüm sesler durdurulabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        # Headless'ta hata vermemeli
        audio.stop_all()


class TestMusic:
    """Music (arka plan müziği) testleri."""

    def test_load_music(self):
        """Müzik dosyası yüklenebilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        music = audio.load_music("test.ogg")
        assert music is not None

    def test_play_music(self):
        """Müzik çalınabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        music = audio.load_music("test.ogg")
        audio.play_music(music)

    def test_stop_music(self):
        """Müzik durdurulabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        music = audio.load_music("test.ogg")
        audio.play_music(music)
        audio.stop_music()

    def test_music_loop(self):
        """Müzik döngüsel çalınabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        music = audio.load_music("test.ogg")
        audio.play_music(music, loop=True)

    def test_music_volume(self):
        """Müzik seviesi ayrı ayarlanabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        audio.set_music_volume(0.3)
        assert audio.music_volume == 0.3


class TestAudioSubsystem:
    """Audio subsystem interface testleri."""

    def test_initialize(self):
        """Audio initialize edilebilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()
        audio.initialize()

    def test_tick(self):
        """Audio tick çağrılabilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()
        audio.initialize()
        audio.tick(0.016)  # 60 FPS

    def test_shutdown(self):
        """Audio shutdown edilebilmeli."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()
        audio.initialize()
        audio.shutdown()

    def test_name_property(self):
        """Audio subsystem name 'audio' olmalı."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()
        assert audio.name == "audio"


class TestAudioHeadless:
    """Headless ortam testleri."""

    def test_audio_works_without_hardware(self):
        """Headless ortamda ses sistemi çalışmalı."""
        from engine.audio.audio import AudioSystem
        audio = AudioSystem()

        # GPU/ses kartı olmadan çalışmalı
        audio.initialize()
        sound = audio.load_sound("test.wav")
        audio.play(sound)
        audio.tick(0.016)
        audio.shutdown()
