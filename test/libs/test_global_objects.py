import unittest
from unittest.mock import Mock, patch

from libs.global_data import PlayerNum
from libs.global_objects import (
    AllNetIcon,
    CoinOverlay,
    EntryOverlay,
    Indicator,
    Nameplate,
    Timer,
)


class TestNameplate(unittest.TestCase):
    """Test cases for the Nameplate class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock global_tex and its methods
        self.mock_tex = Mock()
        self.mock_tex.skin_config = {
            "nameplate_text_name": Mock(font_size=20, x=100, y=50, width=200),
            "nameplate_text_title": Mock(font_size=16, x=100, y=80, width=150),
            "nameplate_title_offset": Mock(x=10),
            "nameplate_dan_offset": Mock(x=20)
        }
        self.mock_tex.get_animation = Mock(return_value=Mock(start=Mock(), update=Mock(), is_finished=False))

    @patch('libs.global_objects.global_tex')
    @patch('libs.global_objects.OutlinedText')
    def test_initialization_basic(self, mock_text, mock_global_tex):
        """Test basic nameplate initialization."""
        mock_global_tex.skin_config = self.mock_tex.skin_config

        nameplate = Nameplate("TestPlayer", "TestTitle", PlayerNum.P1, 5, False, False, 0)

        self.assertEqual(nameplate.dan_index, 5)
        self.assertEqual(nameplate.player_num, 1)
        self.assertFalse(nameplate.is_gold)
        self.assertFalse(nameplate.is_rainbow)
        self.assertEqual(nameplate.title_bg, 0)

    @patch('libs.global_objects.global_tex')
    @patch('libs.global_objects.OutlinedText')
    def test_initialization_rainbow(self, mock_text, mock_global_tex):
        """Test rainbow nameplate initialization."""
        mock_global_tex.skin_config = self.mock_tex.skin_config
        mock_animation = Mock()
        mock_global_tex.get_animation.return_value = mock_animation

        nameplate = Nameplate("Player", "Title", PlayerNum.P1, 3, False, True, 0)

        self.assertTrue(nameplate.is_rainbow)
        mock_global_tex.get_animation.assert_called_once_with(12)
        mock_animation.start.assert_called_once()

    @patch('libs.global_objects.global_tex')
    def test_update_rainbow_animation(self, mock_global_tex):
        """Test rainbow animation update logic."""
        mock_animation = Mock(is_finished=False, update=Mock())
        mock_global_tex.get_animation.return_value = mock_animation
        mock_global_tex.skin_config = self.mock_tex.skin_config

        with patch('libs.global_objects.OutlinedText'):
            nameplate = Nameplate("P", "T", PlayerNum.P1, 0, False, True, 0)
            nameplate.update(1000.0)

            mock_animation.update.assert_called_once_with(1000.0)

    @patch('libs.global_objects.global_tex')
    def test_update_rainbow_restart(self, mock_global_tex):
        """Test rainbow animation restarts when finished."""
        mock_animation = Mock(is_finished=True, update=Mock(), restart=Mock())
        mock_global_tex.get_animation.return_value = mock_animation
        mock_global_tex.skin_config = self.mock_tex.skin_config

        with patch('libs.global_objects.OutlinedText'):
            nameplate = Nameplate("P", "T", PlayerNum.P1, 0, False, True, 0)
            nameplate.update(1000.0)

            mock_animation.restart.assert_called_once()

    @patch('libs.global_objects.global_tex')
    def test_unload(self, mock_global_tex):
        """Test nameplate resource cleanup."""
        mock_global_tex.skin_config = self.mock_tex.skin_config

        with patch('libs.global_objects.OutlinedText') as mock_text:
            mock_name = Mock()
            mock_title = Mock()
            mock_text.side_effect = [mock_name, mock_title]

            nameplate = Nameplate("P", "T", PlayerNum.P1, 0, False, False, 0)
            nameplate.unload()

            mock_name.unload.assert_called_once()
            mock_title.unload.assert_called_once()


class TestIndicator(unittest.TestCase):
    """Test cases for the Indicator class."""

    @patch('libs.global_objects.global_tex')
    @patch('libs.global_objects.OutlinedText')
    def test_initialization(self, mock_text, mock_global_tex):
        """Test indicator initialization with different states."""
        mock_global_tex.get_animation.return_value = Mock()
        mock_global_tex.skin_config = {"indicator_text": Mock(text={"en": "Select"}, font_size=20)}

        with patch('libs.global_objects.global_data') as mock_data:
            mock_data.config = {"general": {"language": "en"}}

            indicator = Indicator(Indicator.State.SELECT)

            self.assertEqual(indicator.state, Indicator.State.SELECT)
            self.assertEqual(mock_global_tex.get_animation.call_count, 3)

    @patch('libs.global_objects.global_tex')
    def test_update_animations(self, mock_global_tex):
        """Test that all animations update correctly."""
        mock_don_fade = Mock()
        mock_arrow_move = Mock()
        mock_arrow_fade = Mock()
        mock_global_tex.get_animation.side_effect = [mock_don_fade, mock_arrow_move, mock_arrow_fade]
        mock_global_tex.skin_config = {"indicator_text": Mock(text={"en": "S"}, font_size=20)}

        with patch('libs.global_objects.global_data.config', {"general": {"language": "en"}}):
            with patch('libs.global_objects.OutlinedText'):
                indicator = Indicator(Indicator.State.SKIP)
                indicator.update(500.0)

                mock_don_fade.update.assert_called_once_with(500.0)
                mock_arrow_move.update.assert_called_once_with(500.0)
                mock_arrow_fade.update.assert_called_once_with(500.0)


class TestTimer(unittest.TestCase):
    """Test cases for the Timer class."""

    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_initialization(self, mock_tex, mock_config):
        """Test timer initialization."""
        mock_config.return_value = {"general": {"timer_frozen": False}}
        mock_tex.get_animation.return_value = Mock()
        mock_func = Mock()

        timer = Timer(30, 0.0, mock_func)

        self.assertEqual(timer.time, 30)
        self.assertEqual(timer.counter, "30")
        self.assertFalse(timer.is_finished)
        self.assertFalse(timer.is_frozen)

    @patch('libs.global_objects.audio')
    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_countdown_normal(self, mock_tex, mock_config, mock_audio):
        """Test normal countdown behavior."""
        mock_config.return_value = {"general": {"timer_frozen": False}}
        mock_tex.get_animation.return_value = Mock(update=Mock(), start=Mock())
        mock_func = Mock()

        timer = Timer(15, 0.0, mock_func)
        timer.update(1000.0)

        self.assertEqual(timer.time, 14)
        self.assertEqual(timer.counter, "14")

    @patch('libs.global_objects.audio')
    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_countdown_below_ten(self, mock_tex, mock_config, mock_audio):
        """Test countdown triggers animations below 10."""
        mock_config.return_value = {"general": {"timer_frozen": False}}
        mock_animation = Mock(update=Mock(), start=Mock())
        mock_tex.get_animation.return_value = mock_animation
        mock_func = Mock()

        timer = Timer(10, 0.0, mock_func)
        timer.update(1000.0)

        self.assertEqual(timer.time, 9)
        mock_audio.play_sound.assert_called_with('timer_blip', 'sound')
        self.assertEqual(mock_animation.start.call_count, 3)

    @patch('libs.global_objects.audio')
    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_voice_triggers(self, mock_tex, mock_config, mock_audio):
        """Test voice announcements at specific times."""
        mock_config.return_value = {"general": {"timer_frozen": False}}
        mock_tex.get_animation.return_value = Mock(update=Mock(), start=Mock())
        mock_func = Mock()

        # Test 10 second voice
        timer = Timer(11, 0.0, mock_func)
        timer.update(1000.0)
        mock_audio.play_sound.assert_called_with('voice_timer_10', 'voice')

        # Test 5 second voice
        timer = Timer(6, 0.0, mock_func)
        timer.update(1000.0)
        mock_audio.play_sound.assert_called_with('voice_timer_5', 'voice')

    @patch('libs.global_objects.audio')
    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_timer_finish_callback(self, mock_tex, mock_config, mock_audio):
        """Test callback is triggered when timer reaches zero."""
        mock_config.return_value = {"general": {"timer_frozen": False}}
        mock_tex.get_animation.return_value = Mock(update=Mock(), start=Mock())
        mock_audio.is_sound_playing.return_value = False
        mock_func = Mock()

        timer = Timer(1, 0.0, mock_func)
        timer.update(1000.0)
        timer.update(2000.0)

        mock_func.assert_called_once()
        self.assertTrue(timer.is_finished)

    @patch('libs.global_objects.get_config')
    @patch('libs.global_objects.global_tex')
    def test_timer_frozen(self, mock_tex, mock_config):
        """Test frozen timer doesn't count down."""
        mock_config.return_value = {"general": {"timer_frozen": True}}
        mock_tex.get_animation.return_value = Mock(update=Mock())
        mock_func = Mock()

        timer = Timer(10, 0.0, mock_func)
        initial_time = timer.time
        timer.update(1000.0)

        self.assertEqual(timer.time, initial_time)


class TestCoinOverlay(unittest.TestCase):
    """Test cases for the CoinOverlay class."""

    @patch('libs.global_objects.global_tex')
    @patch('libs.global_objects.global_data')
    @patch('libs.global_objects.OutlinedText')
    def test_initialization(self, mock_text, mock_data, mock_tex):
        """Test coin overlay initialization."""
        mock_tex.skin_config = {
            "free_play": Mock(text={"en": "Free Play"}, font_size=24, y=100)
        }
        mock_data.config = {"general": {"language": "en"}}

        _ = CoinOverlay()

        mock_text.assert_called_once()


class TestAllNetIcon(unittest.TestCase):
    """Test cases for the AllNetIcon class."""

    @patch('libs.global_objects.get_config')
    def test_initialization_offline(self, mock_config):
        """Test AllNet icon initializes offline."""
        mock_config.return_value = {"general": {"fake_online": False}}

        icon = AllNetIcon()

        self.assertFalse(icon.online)

    @patch('libs.global_objects.get_config')
    def test_initialization_online(self, mock_config):
        """Test AllNet icon initializes online."""
        mock_config.return_value = {"general": {"fake_online": True}}

        icon = AllNetIcon()

        self.assertTrue(icon.online)


class TestEntryOverlay(unittest.TestCase):
    """Test cases for the EntryOverlay class."""

    @patch('libs.global_objects.get_config')
    def test_initialization(self, mock_config):
        """Test entry overlay initialization."""
        mock_config.return_value = {"general": {"fake_online": False}}

        overlay = EntryOverlay()

        self.assertFalse(overlay.online)
