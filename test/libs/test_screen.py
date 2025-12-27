import unittest
from unittest.mock import Mock, patch

from libs.screen import Screen


class TestScreen(unittest.TestCase):
    """Test cases for the Screen class."""

    def setUp(self):
        """Set up test fixtures."""
        self.screen_name = "test_screen"

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_initialization(self, mock_audio, mock_tex):
        """Test screen initialization."""
        screen = Screen(self.screen_name)

        self.assertEqual(screen.screen_name, self.screen_name)
        self.assertFalse(screen.screen_init)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_on_screen_start(self, mock_audio, mock_tex):
        """Test on_screen_start loads textures and sounds."""
        screen = Screen(self.screen_name)
        screen.on_screen_start()

        mock_tex.load_screen_textures.assert_called_once_with(self.screen_name)
        mock_audio.load_screen_sounds.assert_called_once_with(self.screen_name)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_do_screen_start_first_call(self, mock_audio, mock_tex):
        """Test _do_screen_start initializes screen on first call."""
        screen = Screen(self.screen_name)

        self.assertFalse(screen.screen_init)
        screen._do_screen_start()

        self.assertTrue(screen.screen_init)
        mock_tex.load_screen_textures.assert_called_once_with(self.screen_name)
        mock_audio.load_screen_sounds.assert_called_once_with(self.screen_name)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_do_screen_start_subsequent_calls(self, mock_audio, mock_tex):
        """Test _do_screen_start doesn't reinitialize on subsequent calls."""
        screen = Screen(self.screen_name)

        screen._do_screen_start()
        screen._do_screen_start()
        screen._do_screen_start()

        # Should only be called once despite multiple calls
        mock_tex.load_screen_textures.assert_called_once()
        mock_audio.load_screen_sounds.assert_called_once()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_on_screen_end(self, mock_audio, mock_tex):
        """Test on_screen_end unloads resources and returns next screen."""
        screen = Screen(self.screen_name)
        screen.screen_init = True

        next_screen = "next_screen"
        result = screen.on_screen_end(next_screen)

        self.assertEqual(result, next_screen)
        self.assertFalse(screen.screen_init)
        mock_audio.unload_all_sounds.assert_called_once()
        mock_audio.unload_all_music.assert_called_once()
        mock_tex.unload_textures.assert_called_once()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_on_screen_end_unload_order(self, mock_audio, mock_tex):
        """Test that resources are unloaded in correct order."""
        screen = Screen(self.screen_name)
        screen.screen_init = True

        manager = Mock()
        manager.attach_mock(mock_audio.unload_all_sounds, 'unload_sounds')
        manager.attach_mock(mock_audio.unload_all_music, 'unload_music')
        manager.attach_mock(mock_tex.unload_textures, 'unload_textures')

        screen.on_screen_end("next")

        # Verify order: sounds, music, then textures
        calls = manager.mock_calls
        self.assertEqual(calls[0][0], 'unload_sounds')
        self.assertEqual(calls[1][0], 'unload_music')
        self.assertEqual(calls[2][0], 'unload_textures')

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_update_not_initialized(self, mock_audio, mock_tex):
        """Test update initializes screen if not already initialized."""
        screen = Screen(self.screen_name)

        self.assertFalse(screen.screen_init)
        screen.update()

        self.assertTrue(screen.screen_init)
        mock_tex.load_screen_textures.assert_called_once()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_update_already_initialized(self, mock_audio, mock_tex):
        """Test update doesn't reinitialize if already initialized."""
        screen = Screen(self.screen_name)
        screen.screen_init = True

        screen.update()

        # Should not load again
        mock_tex.load_screen_textures.assert_not_called()
        mock_audio.load_screen_sounds.assert_not_called()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_update_returns_value(self, mock_audio, mock_tex):
        """Test update returns value from _do_screen_start."""
        screen = Screen(self.screen_name)

        with patch.object(screen, '_do_screen_start', return_value="test_value"):
            result = screen.update()
            self.assertEqual(result, "test_value")

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_draw_default_implementation(self, mock_audio, mock_tex):
        """Test draw has empty default implementation."""
        screen = Screen(self.screen_name)

        # Should not raise any errors
        screen.draw()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_do_draw_when_initialized(self, mock_audio, mock_tex):
        """Test _do_draw calls draw when screen is initialized."""
        screen = Screen(self.screen_name)
        screen.screen_init = True

        with patch.object(screen, 'draw') as mock_draw:
            screen._do_draw()
            mock_draw.assert_called_once()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_do_draw_when_not_initialized(self, mock_audio, mock_tex):
        """Test _do_draw doesn't call draw when screen is not initialized."""
        screen = Screen(self.screen_name)
        screen.screen_init = False

        with patch.object(screen, 'draw') as mock_draw:
            screen._do_draw()
            mock_draw.assert_not_called()


class TestScreenSubclass(unittest.TestCase):
    """Test cases for Screen subclass behavior."""

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_subclass_custom_on_screen_start(self, mock_audio, mock_tex):
        """Test that subclass can override on_screen_start."""
        class CustomScreen(Screen):
            def __init__(self, name):
                super().__init__(name)
                self.custom_init_called = False

            def on_screen_start(self):
                super().on_screen_start()
                self.custom_init_called = True

        screen = CustomScreen("custom")
        screen.on_screen_start()

        self.assertTrue(screen.custom_init_called)
        mock_tex.load_screen_textures.assert_called_once_with("custom")

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_subclass_custom_update(self, mock_audio, mock_tex):
        """Test that subclass can override update."""
        class CustomScreen(Screen):
            def __init__(self, name):
                super().__init__(name)
                self.update_count = 0

            def update(self):
                result = super().update()
                self.update_count += 1
                return result

        screen = CustomScreen("custom")
        screen.update()
        screen.update()

        self.assertEqual(screen.update_count, 2)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_subclass_custom_draw(self, mock_audio, mock_tex):
        """Test that subclass can override draw."""
        class CustomScreen(Screen):
            def __init__(self, name):
                super().__init__(name)
                self.draw_called = False

            def draw(self):
                self.draw_called = True

        screen = CustomScreen("custom")
        screen.screen_init = True
        screen._do_draw()

        self.assertTrue(screen.draw_called)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_subclass_custom_on_screen_end(self, mock_audio, mock_tex):
        """Test that subclass can override on_screen_end."""
        class CustomScreen(Screen):
            def __init__(self, name):
                super().__init__(name)
                self.cleanup_called = False

            def on_screen_end(self, next_screen):
                self.cleanup_called = True
                return super().on_screen_end(next_screen)

        screen = CustomScreen("custom")
        screen.screen_init = True
        result = screen.on_screen_end("next")

        self.assertTrue(screen.cleanup_called)
        self.assertEqual(result, "next")


class TestScreenLifecycle(unittest.TestCase):
    """Test cases for complete screen lifecycle."""

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_full_lifecycle(self, mock_audio, mock_tex):
        """Test complete screen lifecycle from start to end."""
        screen = Screen("lifecycle_test")

        # Initial state
        self.assertFalse(screen.screen_init)

        # Start screen
        screen.update()
        self.assertTrue(screen.screen_init)
        mock_tex.load_screen_textures.assert_called_once_with("lifecycle_test")
        mock_audio.load_screen_sounds.assert_called_once_with("lifecycle_test")

        # Multiple updates don't reinitialize
        screen.update()
        screen.update()
        self.assertEqual(mock_tex.load_screen_textures.call_count, 1)

        # Draw while initialized
        with patch.object(screen, 'draw') as mock_draw:
            screen._do_draw()
            mock_draw.assert_called_once()

        # End screen
        result = screen.on_screen_end("next_screen")
        self.assertEqual(result, "next_screen")
        self.assertFalse(screen.screen_init)
        mock_audio.unload_all_sounds.assert_called_once()
        mock_audio.unload_all_music.assert_called_once()
        mock_tex.unload_textures.assert_called_once()

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_multiple_screen_transitions(self, mock_audio, mock_tex):
        """Test transitioning between multiple screens."""
        screen1 = Screen("screen1")
        screen2 = Screen("screen2")
        screen3 = Screen("screen3")

        # Initialize first screen
        screen1.update()
        self.assertTrue(screen1.screen_init)

        # Transition to second screen
        next_name = screen1.on_screen_end("screen2")
        self.assertEqual(next_name, "screen2")
        self.assertFalse(screen1.screen_init)

        screen2.update()
        self.assertTrue(screen2.screen_init)

        # Transition to third screen
        next_name = screen2.on_screen_end("screen3")
        self.assertEqual(next_name, "screen3")
        self.assertFalse(screen2.screen_init)

        screen3.update()
        self.assertTrue(screen3.screen_init)

    @patch('libs.screen.tex')
    @patch('libs.screen.audio')
    def test_screen_reinitialize_after_end(self, mock_audio, mock_tex):
        """Test that screen can be reinitialized after ending."""
        screen = Screen("reinit_test")

        # First initialization
        screen.update()
        self.assertTrue(screen.screen_init)

        # End screen
        screen.on_screen_end("next")
        self.assertFalse(screen.screen_init)

        # Reinitialize
        mock_tex.load_screen_textures.reset_mock()
        mock_audio.load_screen_sounds.reset_mock()

        screen.update()
        self.assertTrue(screen.screen_init)
        mock_tex.load_screen_textures.assert_called_once()
        mock_audio.load_screen_sounds.assert_called_once()


if __name__ == '__main__':
    unittest.main()
