import unittest
from unittest.mock import patch

from libs.animation import (
    Animation,
    BaseAnimation,
    FadeAnimation,
    MoveAnimation,
    TextStretchAnimation,
    TextureChangeAnimation,
    TextureResizeAnimation,
    parse_animations,
)


class TestBaseAnimation(unittest.TestCase):
    """Test cases for the BaseAnimation class."""

    @patch('libs.animation.get_current_ms')
    @patch('libs.animation.global_data')
    def setUp(self, mock_global_data, mock_get_ms):
        """Set up test fixtures."""
        mock_get_ms.return_value = 0.0
        mock_global_data.input_locked = 0

    @patch('libs.animation.get_current_ms')
    def test_initialization(self, mock_get_ms):
        """Test basic initialization of BaseAnimation."""
        mock_get_ms.return_value = 100.0

        anim = BaseAnimation(duration=1000.0, delay=100.0, loop=True, lock_input=True)

        self.assertEqual(anim.duration, 1000.0)
        self.assertEqual(anim.delay, 100.0)
        self.assertEqual(anim.delay_saved, 100.0)
        self.assertEqual(anim.start_ms, 100.0)
        self.assertFalse(anim.is_finished)
        self.assertEqual(anim.attribute, 0)
        self.assertFalse(anim.is_started)
        self.assertTrue(anim.loop)
        self.assertTrue(anim.lock_input)

    @patch('libs.animation.get_current_ms')
    @patch('libs.animation.global_data')
    def test_start(self, mock_global_data, mock_get_ms):
        """Test starting an animation."""
        mock_get_ms.return_value = 200.0
        mock_global_data.input_locked = 0

        anim = BaseAnimation(duration=1000.0, lock_input=True)
        anim.start()

        self.assertTrue(anim.is_started)
        self.assertFalse(anim.is_finished)
        self.assertEqual(mock_global_data.input_locked, 1)

    @patch('libs.animation.get_current_ms')
    @patch('libs.animation.global_data')
    def test_restart(self, mock_global_data, mock_get_ms):
        """Test restarting an animation."""
        mock_get_ms.side_effect = [0.0, 500.0, 1000.0]
        mock_global_data.input_locked = 0

        anim = BaseAnimation(duration=1000.0, delay=100.0, lock_input=True)
        anim.is_finished = True
        anim.delay = 0.0

        anim.restart()

        self.assertEqual(anim.start_ms, 500.0)
        self.assertFalse(anim.is_finished)
        self.assertEqual(anim.delay, 100.0)
        self.assertEqual(mock_global_data.input_locked, 1)

    @patch('libs.animation.get_current_ms')
    @patch('libs.animation.global_data')
    def test_pause_unpause(self, mock_global_data, mock_get_ms):
        """Test pausing and unpausing."""
        mock_get_ms.return_value = 0.0
        mock_global_data.input_locked = 1

        anim = BaseAnimation(duration=1000.0, lock_input=True)
        anim.is_started = True

        anim.pause()
        self.assertFalse(anim.is_started)
        self.assertEqual(mock_global_data.input_locked, 0)

        anim.unpause()
        self.assertTrue(anim.is_started)
        self.assertEqual(mock_global_data.input_locked, 1)

    @patch('libs.animation.get_current_ms')
    def test_loop_restarts(self, mock_get_ms):
        """Test that looped animations restart when finished."""
        mock_get_ms.side_effect = [0.0, 100.0]

        anim = BaseAnimation(duration=1000.0, loop=True)
        anim.is_finished = True

        with patch.object(anim, 'restart') as mock_restart:
            anim.update(100.0)
            mock_restart.assert_called_once()

    @patch('libs.animation.get_current_ms')
    @patch('libs.animation.global_data')
    def test_input_lock_unlock(self, mock_global_data, mock_get_ms):
        """Test input locking mechanism."""
        mock_get_ms.return_value = 0.0
        mock_global_data.input_locked = 1

        anim = BaseAnimation(duration=1000.0, lock_input=True)
        anim.is_finished = True
        anim.unlocked = False

        anim.update(100.0)

        self.assertTrue(anim.unlocked)
        self.assertEqual(mock_global_data.input_locked, 0)

    def test_easing_functions(self):
        """Test easing functions produce expected values."""
        anim = BaseAnimation(duration=1000.0)

        # Test quadratic ease in
        self.assertAlmostEqual(anim._ease_in(0.5, "quadratic"), 0.25)
        self.assertAlmostEqual(anim._ease_in(1.0, "quadratic"), 1.0)

        # Test cubic ease in
        self.assertAlmostEqual(anim._ease_in(0.5, "cubic"), 0.125)

        # Test exponential ease in
        self.assertEqual(anim._ease_in(0.0, "exponential"), 0)

        # Test quadratic ease out
        self.assertAlmostEqual(anim._ease_out(0.5, "quadratic"), 0.75)

        # Test cubic ease out
        self.assertAlmostEqual(anim._ease_out(0.5, "cubic"), 0.875)

        # Test exponential ease out
        self.assertEqual(anim._ease_out(1.0, "exponential"), 1)


class TestFadeAnimation(unittest.TestCase):
    """Test cases for the FadeAnimation class."""

    @patch('libs.animation.get_current_ms')
    def test_initialization(self, mock_get_ms):
        """Test fade animation initialization."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(
            duration=1000.0,
            initial_opacity=1.0,
            final_opacity=0.0,
            delay=100.0,
            ease_in="quadratic"
        )

        self.assertEqual(anim.initial_opacity, 1.0)
        self.assertEqual(anim.final_opacity, 0.0)
        self.assertEqual(anim.attribute, 1.0)
        self.assertEqual(anim.ease_in, "quadratic")

    @patch('libs.animation.get_current_ms')
    def test_fade_during_delay(self, mock_get_ms):
        """Test that opacity stays at initial during delay."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(duration=1000.0, initial_opacity=1.0, final_opacity=0.0, delay=500.0)
        anim.start()

        anim.update(250.0)  # Within delay period

        self.assertEqual(anim.attribute, 1.0)
        self.assertFalse(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_fade_progression(self, mock_get_ms):
        """Test fade progresses correctly."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(duration=1000.0, initial_opacity=1.0, final_opacity=0.0)
        anim.start()

        anim.update(500.0)  # Halfway through

        self.assertAlmostEqual(anim.attribute, 0.5, places=2)
        self.assertFalse(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_fade_completion(self, mock_get_ms):
        """Test fade completes at final opacity."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(duration=1000.0, initial_opacity=1.0, final_opacity=0.0)
        anim.start()

        anim.update(1000.0)  # End of animation

        self.assertEqual(anim.attribute, 0.0)
        self.assertTrue(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_fade_with_reverse_delay(self, mock_get_ms):
        """Test fade reverses after reverse_delay."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(
            duration=1000.0,
            initial_opacity=1.0,
            final_opacity=0.0,
            reverse_delay=200.0
        )
        anim.start()

        anim.update(1000.0)  # Complete first fade

        self.assertEqual(anim.attribute, 0.0)
        self.assertTrue(anim.is_reversing)
        self.assertEqual(anim.initial_opacity, 0.0)
        self.assertEqual(anim.final_opacity, 1.0)
        self.assertFalse(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_fade_with_easing(self, mock_get_ms):
        """Test fade applies easing correctly."""
        mock_get_ms.return_value = 0.0

        anim = FadeAnimation(
            duration=1000.0,
            initial_opacity=0.0,
            final_opacity=1.0,
            ease_in="quadratic"
        )
        anim.start()

        anim.update(500.0)  # Halfway

        # With quadratic ease in, at 0.5 progress we should have 0.25
        self.assertAlmostEqual(anim.attribute, 0.25, places=2)


class TestMoveAnimation(unittest.TestCase):
    """Test cases for the MoveAnimation class."""

    @patch('libs.animation.get_current_ms')
    def test_initialization(self, mock_get_ms):
        """Test move animation initialization."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(
            duration=1000.0,
            start_position=0,
            total_distance=100,
            delay=50.0
        )

        self.assertEqual(anim.start_position, 0)
        self.assertEqual(anim.total_distance, 100)
        self.assertEqual(anim.delay, 50.0)

    @patch('libs.animation.get_current_ms')
    def test_move_during_delay(self, mock_get_ms):
        """Test position stays at start during delay."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(duration=1000.0, start_position=50, total_distance=100, delay=200.0)
        anim.start()

        anim.update(100.0)  # Within delay

        self.assertEqual(anim.attribute, 50)

    @patch('libs.animation.get_current_ms')
    def test_move_progression(self, mock_get_ms):
        """Test move progresses correctly."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(duration=1000.0, start_position=0, total_distance=100)
        anim.start()

        anim.update(500.0)  # Halfway

        self.assertAlmostEqual(anim.attribute, 50.0, places=2)

    @patch('libs.animation.get_current_ms')
    def test_move_completion(self, mock_get_ms):
        """Test move completes at final position."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(duration=1000.0, start_position=0, total_distance=100)
        anim.start()

        anim.update(1000.0)

        self.assertEqual(anim.attribute, 100)
        self.assertTrue(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_move_with_reverse_delay(self, mock_get_ms):
        """Test move reverses after reverse_delay."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(
            duration=1000.0,
            start_position=0,
            total_distance=100,
            reverse_delay=100.0
        )
        anim.start()

        anim.update(1000.0)  # Complete first move

        self.assertEqual(anim.start_position, 100)
        self.assertEqual(anim.total_distance, -100)
        self.assertIsNone(anim.reverse_delay)
        self.assertFalse(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_move_with_easing(self, mock_get_ms):
        """Test move applies easing."""
        mock_get_ms.return_value = 0.0

        anim = MoveAnimation(
            duration=1000.0,
            start_position=0,
            total_distance=100,
            ease_out="quadratic"
        )
        anim.start()

        anim.update(500.0)

        # With quadratic ease out, at 0.5 progress we should have 0.75
        self.assertAlmostEqual(anim.attribute, 75.0, places=2)


class TestTextureChangeAnimation(unittest.TestCase):
    """Test cases for the TextureChangeAnimation class."""

    @patch('libs.animation.get_current_ms')
    def test_initialization(self, mock_get_ms):
        """Test texture change animation initialization."""
        mock_get_ms.return_value = 0.0

        textures = [(0.0, 100.0, 0), (100.0, 200.0, 1), (200.0, 300.0, 2)]
        anim = TextureChangeAnimation(duration=300.0, textures=textures)

        self.assertEqual(anim.textures, textures)
        self.assertEqual(anim.attribute, 0)  # First texture index

    @patch('libs.animation.get_current_ms')
    def test_texture_change_progression(self, mock_get_ms):
        """Test texture changes at correct times."""
        mock_get_ms.return_value = 0.0

        textures = [(0.0, 100.0, 0), (100.0, 200.0, 1), (200.0, 300.0, 2)]
        anim = TextureChangeAnimation(duration=300.0, textures=textures)
        anim.start()

        anim.update(50.0)
        self.assertEqual(anim.attribute, 0)

        anim.update(150.0)
        self.assertEqual(anim.attribute, 1)

        anim.update(250.0)
        self.assertEqual(anim.attribute, 2)

    @patch('libs.animation.get_current_ms')
    def test_texture_change_completion(self, mock_get_ms):
        """Test texture change completes."""
        mock_get_ms.return_value = 0.0

        textures = [(0.0, 100.0, 0), (100.0, 200.0, 1)]
        anim = TextureChangeAnimation(duration=200.0, textures=textures)
        anim.start()

        anim.update(300.0)  # Past duration

        self.assertTrue(anim.is_finished)

    @patch('libs.animation.get_current_ms')
    def test_texture_change_with_delay(self, mock_get_ms):
        """Test texture change respects delay."""
        mock_get_ms.return_value = 0.0

        textures = [(0.0, 100.0, 0), (100.0, 200.0, 1)]
        anim = TextureChangeAnimation(duration=200.0, textures=textures, delay=100.0)
        anim.start()

        anim.update(50.0)  # During delay
        self.assertEqual(anim.attribute, 0)

        anim.update(150.0)  # 50ms into animation (after delay)
        self.assertEqual(anim.attribute, 0)


class TestTextureResizeAnimation(unittest.TestCase):
    """Test cases for the TextureResizeAnimation class."""

    @patch('libs.animation.get_current_ms')
    def test_initialization(self, mock_get_ms):
        """Test texture resize initialization."""
        mock_get_ms.return_value = 0.0

        anim = TextureResizeAnimation(
            duration=1000.0,
            initial_size=1.0,
            final_size=2.0
        )

        self.assertEqual(anim.initial_size, 1.0)
        self.assertEqual(anim.final_size, 2.0)
        self.assertEqual(anim.attribute, 1.0)

    @patch('libs.animation.get_current_ms')
    def test_resize_progression(self, mock_get_ms):
        """Test resize progresses correctly."""
        mock_get_ms.return_value = 0.0

        anim = TextureResizeAnimation(duration=1000.0, initial_size=1.0, final_size=2.0)
        anim.start()

        anim.update(500.0)  # Halfway

        self.assertAlmostEqual(anim.attribute, 1.5, places=2)

    @patch('libs.animation.get_current_ms')
    def test_resize_completion(self, mock_get_ms):
        """Test resize completes."""
        mock_get_ms.return_value = 0.0

        anim = TextureResizeAnimation(duration=1000.0, initial_size=1.0, final_size=0.5)
        anim.start()

        anim.update(1000.0)

        self.assertEqual(anim.attribute, 0.5)
        self.assertTrue(anim.is_finished)


class TestTextStretchAnimation(unittest.TestCase):
    """Test cases for the TextStretchAnimation class."""

    @patch('libs.animation.get_current_ms')
    def test_stretch_phases(self, mock_get_ms):
        """Test text stretch animation phases."""
        mock_get_ms.return_value = 0.0

        anim = TextStretchAnimation(duration=100.0)
        anim.start()

        # Phase 1: Growing
        anim.update(50.0)
        self.assertGreater(anim.attribute, 2)

        # Phase 2: Shrinking back
        anim.update(150.0)
        self.assertGreater(anim.attribute, 0)

        # Phase 3: Finished
        anim.update(300.0)
        self.assertEqual(anim.attribute, 0)
        self.assertTrue(anim.is_finished)


class TestAnimationFactory(unittest.TestCase):
    """Test cases for the Animation factory class."""

    def test_create_fade(self):
        """Test factory creates fade animation."""
        anim = Animation.create_fade(1000.0, initial_opacity=1.0, final_opacity=0.0)

        self.assertIsInstance(anim, FadeAnimation)
        self.assertEqual(anim.duration, 1000.0)
        self.assertEqual(anim.initial_opacity, 1.0)

    def test_create_move(self):
        """Test factory creates move animation."""
        anim = Animation.create_move(1000.0, start_position=0, total_distance=100)

        self.assertIsInstance(anim, MoveAnimation)
        self.assertEqual(anim.duration, 1000.0)
        self.assertEqual(anim.total_distance, 100)

    def test_create_texture_change(self):
        """Test factory creates texture change animation."""
        textures = [(0.0, 100.0, 0)]
        anim = Animation.create_texture_change(1000.0, textures=textures)

        self.assertIsInstance(anim, TextureChangeAnimation)
        self.assertEqual(anim.textures, textures)

    def test_create_texture_resize(self):
        """Test factory creates texture resize animation."""
        anim = Animation.create_texture_resize(1000.0, initial_size=1.0, final_size=2.0)

        self.assertIsInstance(anim, TextureResizeAnimation)
        self.assertEqual(anim.initial_size, 1.0)


class TestParseAnimations(unittest.TestCase):
    """Test cases for parse_animations function."""

    def test_parse_basic_animation(self):
        """Test parsing a simple animation."""
        animation_json = [
            {
                "id": 1,
                "type": "fade",
                "duration": 1000.0,
                "initial_opacity": 1.0,
                "final_opacity": 0.0
            }
        ]

        result = parse_animations(animation_json)

        self.assertIn(1, result)
        self.assertIsInstance(result[1], FadeAnimation)
        self.assertEqual(result[1].duration, 1000.0)

    def test_parse_multiple_animations(self):
        """Test parsing multiple animations."""
        animation_json = [
            {"id": 1, "type": "fade", "duration": 1000.0},
            {"id": 2, "type": "move", "duration": 500.0, "total_distance": 50}
        ]

        result = parse_animations(animation_json)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[1], FadeAnimation)
        self.assertIsInstance(result[2], MoveAnimation)

    def test_parse_with_reference(self):
        """Test parsing animations with references."""
        animation_json = [
            {"id": 1, "type": "fade", "duration": 1000.0, "initial_opacity": 1.0},
            {
                "id": 2,
                "type": "fade",
                "duration": {"reference_id": 1, "property": "duration"},
                "initial_opacity": 0.5
            }
        ]

        result = parse_animations(animation_json)

        self.assertEqual(result[2].duration, 1000.0)
        self.assertEqual(result[2].initial_opacity, 0.5)

    def test_parse_with_reference_and_init_val(self):
        """Test parsing with reference and init_val modifier."""
        animation_json = [
            {"id": 1, "type": "fade", "duration": 1000.0},
            {
                "id": 2,
                "type": "fade",
                "duration": {
                    "reference_id": 1,
                    "property": "duration",
                    "init_val": 500.0
                }
            }
        ]

        result = parse_animations(animation_json)

        self.assertEqual(result[2].duration, 1500.0)

    def test_parse_missing_id_raises_error(self):
        """Test that missing id raises exception."""
        animation_json = [
            {"type": "fade", "duration": 1000.0}
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("requires id", str(context.exception))

    def test_parse_missing_type_raises_error(self):
        """Test that missing type raises exception."""
        animation_json = [
            {"id": 1, "duration": 1000.0}
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("requires type", str(context.exception))

    def test_parse_circular_reference_raises_error(self):
        """Test that circular references are detected."""
        animation_json = [
            {
                "id": 1,
                "type": "fade",
                "duration": {"reference_id": 2, "property": "duration"}
            },
            {
                "id": 2,
                "type": "fade",
                "duration": {"reference_id": 1, "property": "duration"}
            }
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("Circular reference", str(context.exception))

    def test_parse_unknown_type_raises_error(self):
        """Test that unknown animation type raises exception."""
        animation_json = [
            {"id": 1, "type": "unknown_type", "duration": 1000.0}
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("Unknown Animation type", str(context.exception))

    def test_parse_missing_reference_property_raises_error(self):
        """Test that missing reference property raises exception."""
        animation_json = [
            {"id": 1, "type": "fade", "duration": 1000.0},
            {
                "id": 2,
                "type": "fade",
                "duration": {"reference_id": 1}
            }
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("requires 'property'", str(context.exception))

    def test_parse_nonexistent_reference_raises_error(self):
        """Test that referencing nonexistent animation raises exception."""
        animation_json = [
            {
                "id": 1,
                "type": "fade",
                "duration": {"reference_id": 999, "property": "duration"}
            }
        ]

        with self.assertRaises(Exception) as context:
            parse_animations(animation_json)
        self.assertIn("not found", str(context.exception))

    def test_parse_ignores_comments(self):
        """Test that comments are ignored during parsing."""
        animation_json = [
            {
                "id": 1,
                "type": "fade",
                "duration": 1000.0,
                "comment": "This is a fade animation"
            }
        ]

        result = parse_animations(animation_json)

        self.assertIn(1, result)
        self.assertIsInstance(result[1], FadeAnimation)

    def test_parse_nested_references(self):
        """Test parsing nested reference chains."""
        animation_json = [
            {"id": 1, "type": "fade", "duration": 1000.0},
            {
                "id": 2,
                "type": "fade",
                "duration": {"reference_id": 1, "property": "duration"}
            },
            {
                "id": 3,
                "type": "fade",
                "duration": {
                    "reference_id": 2,
                    "property": "duration",
                    "init_val": 500.0
                }
            }
        ]

        result = parse_animations(animation_json)

        self.assertEqual(result[3].duration, 1500.0)


if __name__ == '__main__':
    unittest.main()
