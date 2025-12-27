import shutil
import struct
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from libs.audio import AudioEngine, audio
from libs.config import VolumeConfig

DEFAULT_CONFIG = VolumeConfig(sound=0.8, music=0.7, voice=0.6, hitsound=0.5, attract_mode=0.4)

class TestAudioEngine(unittest.TestCase):
    """Integration tests using the audio library."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        # Create temporary directory for test audio files
        cls.test_dir = Path().cwd() / Path("temp")
        cls.test_dir.mkdir(exist_ok=True)
        cls.sounds_dir = Path(cls.test_dir) / "Sounds"
        cls.sounds_dir.mkdir(exist_ok=True)

        # Create test WAV files
        cls._create_test_wav(cls.sounds_dir / "don.wav")
        cls._create_test_wav(cls.sounds_dir / "ka.wav")
        cls._create_test_wav(cls.sounds_dir / "test_sound.wav")
        cls._create_test_wav(cls.sounds_dir / "test_music.wav", duration=2.0)

        # Create screen sounds directory
        cls.screen_sounds = cls.sounds_dir / "menu"
        cls.screen_sounds.mkdir()
        cls._create_test_wav(cls.screen_sounds / "click.wav")
        cls._create_test_wav(cls.screen_sounds / "hover.wav")

        # Create global sounds directory
        cls.global_sounds = cls.sounds_dir / "global"
        cls.global_sounds.mkdir()
        cls._create_test_wav(cls.global_sounds / "confirm.wav")

        cls.volume_presets = DEFAULT_CONFIG

    @classmethod
    def tearDownClass(cls):
        """Clean up test files."""
        shutil.rmtree(cls.test_dir)

    @staticmethod
    def _create_test_wav(filepath, duration=0.1, frequency=440):
        """Create a simple test WAV file."""
        sample_rate = 44100
        num_samples = int(sample_rate * duration)

        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            for i in range(num_samples):
                # Generate a simple sine wave
                value = int(32767.0 * 0.3 *
                           (i % (sample_rate // frequency)) /
                           (sample_rate // frequency))
                wav_file.writeframes(struct.pack('h', value))

    def setUp(self):
        """Set up each test."""
        self.mock_config_path = self.sounds_dir
        # Store original audio singleton state to avoid test pollution
        self._original_audio_sounds_path = audio.sounds_path
    
    def tearDown(self):
        """Tear down each test."""
        # Restore original audio singleton state
        audio.sounds_path = self._original_audio_sounds_path
        # Clear any sounds or music loaded during tests
        if hasattr(audio, 'sounds') and isinstance(audio.sounds, dict):
            audio.sounds.clear()
        if hasattr(audio, 'music_streams') and isinstance(audio.music_streams, dict):
            audio.music_streams.clear()

    @patch('libs.audio.get_config')
    def test_initialization(self, mock_config):
        """Test AudioEngine initialization."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}

        engine = AudioEngine(
            device_type=0,
            sample_rate=44100.0,
            buffer_size=512,
            volume_presets=self.volume_presets,
            sounds_path=self.sounds_dir
        )

        self.assertEqual(engine.device_type, 0)
        self.assertEqual(engine.target_sample_rate, 44100.0)
        self.assertEqual(engine.buffer_size, 512)
        self.assertEqual(engine.volume_presets, self.volume_presets)
        self.assertFalse(engine.audio_device_ready)

    @patch('libs.audio.get_config')
    def test_init_and_close_audio_device(self, mock_config):
        """Test initializing and closing audio device."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}

        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        # Initialize
        success = engine.init_audio_device()
        self.assertTrue(success)
        self.assertTrue(engine.audio_device_ready)
        self.assertTrue(engine.is_audio_device_ready())

        # Close
        engine.close_audio_device()
        self.assertFalse(engine.audio_device_ready)

    @patch('libs.audio.get_config')
    def test_master_volume(self, mock_config):
        """Test master volume control."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Set and get master volume
                engine.set_master_volume(0.75)
                volume = engine.get_master_volume()
                self.assertAlmostEqual(volume, 0.75, places=2)

                # Test clamping
                engine.set_master_volume(1.5)
                volume = engine.get_master_volume()
                self.assertLessEqual(volume, 1.0)

                engine.set_master_volume(-0.5)
                volume = engine.get_master_volume()
                self.assertGreaterEqual(volume, 0.0)
            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_load_and_unload_sound(self, mock_config):
        """Test loading and unloading sounds."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Load sound
                sound_path = self.sounds_dir / "test_sound.wav"
                sound_id = engine.load_sound(sound_path, "test")

                self.assertEqual(sound_id, "test")
                self.assertIn("test", engine.sounds)

                # Unload sound
                engine.unload_sound("test")
                self.assertNotIn("test", engine.sounds)
            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_load_nonexistent_sound(self, mock_config):
        """Test loading a non-existent sound file."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                sound_id = engine.load_sound(Path("nonexistent.wav"), "bad")
                self.assertEqual(sound_id, "")
                self.assertNotIn("bad", engine.sounds)
            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_play_and_stop_sound(self, mock_config):
        """Test playing and stopping sounds."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Load and play sound
                sound_path = self.sounds_dir / "test_sound.wav"
                engine.load_sound(sound_path, "test")

                engine.play_sound("test", "sound")

                # Give it a moment to start
                import time
                time.sleep(0.05)

                # Check if playing (might not be if audio is very short)
                # Just verify no exceptions were raised
                is_playing = engine.is_sound_playing("test")
                self.assertIsInstance(is_playing, bool)

                # Stop sound
                engine.stop_sound("test")

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_play_don_and_kat(self, mock_config):
        """Test playing the special don and kat sounds."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Play don
                engine.play_sound("don", "sound")
                is_playing = engine.is_sound_playing("don")
                self.assertIsInstance(is_playing, bool)
                engine.stop_sound("don")

                # Play kat
                engine.play_sound("kat", "sound")
                is_playing = engine.is_sound_playing("kat")
                self.assertIsInstance(is_playing, bool)
                engine.stop_sound("kat")

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_sound_volume_control(self, mock_config):
        """Test setting sound volume."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                sound_path = self.sounds_dir / "test_sound.wav"
                engine.load_sound(sound_path, "test")

                # Set volume (should not raise exception)
                engine.set_sound_volume("test", 0.5)
                engine.play_sound("test", "")

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_sound_pan_control(self, mock_config):
        """Test setting sound pan."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                sound_path = self.sounds_dir / "test_sound.wav"
                engine.load_sound(sound_path, "test")

                # Set pan (should not raise exception)
                engine.set_sound_pan("test", -0.5)  # Left
                engine.set_sound_pan("test", 0.5)   # Right
                engine.set_sound_pan("test", 0.0)   # Center

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_load_screen_sounds(self, mock_config):
        """Test loading sounds for a screen."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                engine.load_screen_sounds("menu")

                # Check that screen sounds were loaded
                self.assertIn("click", engine.sounds)
                self.assertIn("hover", engine.sounds)

                # Check that global sounds were loaded
                self.assertIn("confirm", engine.sounds)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_unload_all_sounds(self, mock_config):
        """Test unloading all sounds."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Load multiple sounds
                engine.load_sound(self.sounds_dir / "test_sound.wav", "s1")
                engine.load_sound(self.sounds_dir / "test_sound.wav", "s2")
                engine.load_sound(self.sounds_dir / "test_sound.wav", "s3")

                self.assertEqual(len(engine.sounds), 3)

                # Unload all
                engine.unload_all_sounds()
                self.assertEqual(len(engine.sounds), 0)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_load_and_play_music_stream(self, mock_config):
        """Test loading and playing music streams."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                music_path = self.sounds_dir / "test_music.wav"
                music_id = engine.load_music_stream(music_path, "bgm")
                print(music_id)

                self.assertEqual(music_id, "bgm")
                self.assertIn("bgm", engine.music_streams)

                # Play music
                engine.play_music_stream("bgm", "music")

                # Update music stream
                engine.update_music_stream("bgm")

                # Check if playing
                is_playing = engine.is_music_stream_playing("bgm")
                self.assertIsInstance(is_playing, bool)

                # Stop music
                engine.stop_music_stream("bgm")

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_music_time_functions(self, mock_config):
        """Test getting music time length and played."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                music_path = self.sounds_dir / "test_music.wav"
                music_file = engine.load_music_stream(music_path, "bgm")

                # Get time length
                length = engine.get_music_time_length(music_file)
                self.assertGreater(length, 0.0)
                self.assertLess(length, 10.0)  # Should be around 2 seconds

                # Play and get time played
                engine.play_music_stream(music_file, "music")
                engine.update_music_stream(music_file)

                import time
                time.sleep(0.1)
                engine.update_music_stream(music_file)

                played = engine.get_music_time_played(music_file)
                self.assertGreaterEqual(played, 0.0)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_music_volume_control(self, mock_config):
        """Test setting music volume."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                music_path = self.sounds_dir / "test_music.wav"
                engine.load_music_stream(music_path, "bgm")

                # Set volume (should not raise exception)
                engine.set_music_volume("bgm", 0.6)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_seek_music_stream(self, mock_config):
        """Test seeking in music stream."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                music_path = self.sounds_dir / "test_music.wav"
                engine.load_music_stream(music_path, "bgm")

                # Seek to position (should not raise exception)
                engine.seek_music_stream("bgm", 0.5)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_unload_music_stream(self, mock_config):
        """Test unloading music stream."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)


        if engine.init_audio_device():
            try:
                music_path = self.sounds_dir / "test_music.wav"
                engine.load_music_stream(music_path, "bgm")

                self.assertIn("bgm", engine.music_streams)

                engine.unload_music_stream("bgm")
                self.assertNotIn("bgm", engine.music_streams)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_unload_all_music(self, mock_config):
        """Test unloading all music streams."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Load multiple music streams
                music_path = self.sounds_dir / "test_music.wav"
                engine.load_music_stream(music_path, "bgm1")
                engine.load_music_stream(music_path, "bgm2")

                self.assertEqual(len(engine.music_streams), 2)

                engine.unload_all_music()
                self.assertEqual(len(engine.music_streams), 0)

            finally:
                engine.close_audio_device()

    @patch('libs.audio.get_config')
    def test_host_api_functions(self, mock_config):
        """Test host API query functions."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)
        engine.init_audio_device()

        # List host APIs (should not crash)
        engine.list_host_apis()

        # Get host API name
        name = engine.get_host_api_name(0)
        self.assertIsInstance(name, str)

    @patch('libs.audio.get_config')
    def test_full_lifecycle(self, mock_config):
        """Test complete audio engine lifecycle."""
        mock_config.return_value = {"paths": {"skin": f"{self.sounds_dir}"}}
        engine = AudioEngine(0, 44100.0, 512, self.volume_presets, sounds_path=self.sounds_dir)
        engine.set_log_level(10)

        if engine.init_audio_device():
            try:
                # Load sounds and music
                engine.load_sound(self.sounds_dir / "test_sound.wav", "sfx")
                engine.load_music_stream(self.sounds_dir / "test_music.wav", "bgm")

                # Set volumes
                engine.set_master_volume(0.8)
                engine.set_sound_volume("sfx", 0.7)
                engine.set_music_volume("bgm", 0.6)

                # Play audio
                engine.play_sound("sfx", "sound")
                engine.play_music_stream("bgm", "music")

                import time
                time.sleep(0.1)

                # Update music
                engine.update_music_stream("bgm")

                # Stop
                engine.stop_sound("sfx")
                engine.stop_music_stream("bgm")

                # Cleanup
                engine.unload_sound("sfx")
                engine.unload_music_stream("bgm")

            finally:
                engine.close_audio_device()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
