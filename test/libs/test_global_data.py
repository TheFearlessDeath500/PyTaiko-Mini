import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from libs.global_data import (
    Camera,
    Crown,
    DanResultData,
    DanResultExam,
    DanResultSong,
    Difficulty,
    GlobalData,
    Modifiers,
    PlayerNum,
    ResultData,
    ScoreMethod,
    SessionData,
    global_data,
    reset_session,
)


class TestPlayerNum(unittest.TestCase):
    """Test cases for the PlayerNum enum."""

    def test_player_num_values(self):
        """Test PlayerNum enum values."""
        self.assertEqual(PlayerNum.ALL, 0)
        self.assertEqual(PlayerNum.P1, 1)
        self.assertEqual(PlayerNum.P2, 2)
        self.assertEqual(PlayerNum.TWO_PLAYER, 3)
        self.assertEqual(PlayerNum.DAN, 4)

    def test_player_num_is_int_enum(self):
        """Test that PlayerNum values are integers."""
        self.assertIsInstance(PlayerNum.P1, int)
        self.assertIsInstance(PlayerNum.P2, int)


class TestScoreMethod(unittest.TestCase):
    """Test cases for the ScoreMethod class."""

    def test_score_method_constants(self):
        """Test ScoreMethod constants."""
        self.assertEqual(ScoreMethod.GEN3, "gen3")
        self.assertEqual(ScoreMethod.SHINUCHI, "shinuchi")


class TestDifficulty(unittest.TestCase):
    """Test cases for the Difficulty enum."""

    def test_difficulty_values(self):
        """Test Difficulty enum values."""
        self.assertEqual(Difficulty.EASY, 0)
        self.assertEqual(Difficulty.NORMAL, 1)
        self.assertEqual(Difficulty.HARD, 2)
        self.assertEqual(Difficulty.ONI, 3)
        self.assertEqual(Difficulty.URA, 4)
        self.assertEqual(Difficulty.TOWER, 5)
        self.assertEqual(Difficulty.DAN, 6)

    def test_difficulty_ordering(self):
        """Test that difficulty levels are ordered correctly."""
        self.assertLess(Difficulty.EASY, Difficulty.NORMAL)
        self.assertLess(Difficulty.NORMAL, Difficulty.HARD)
        self.assertLess(Difficulty.HARD, Difficulty.ONI)
        self.assertLess(Difficulty.ONI, Difficulty.URA)


class TestCrown(unittest.TestCase):
    """Test cases for the Crown enum."""

    def test_crown_values(self):
        """Test Crown enum values."""
        self.assertEqual(Crown.NONE, 0)
        self.assertEqual(Crown.CLEAR, 1)
        self.assertEqual(Crown.FC, 2)
        self.assertEqual(Crown.DFC, 3)

    def test_crown_ordering(self):
        """Test crown achievement ordering."""
        self.assertLess(Crown.NONE, Crown.CLEAR)
        self.assertLess(Crown.CLEAR, Crown.FC)
        self.assertLess(Crown.FC, Crown.DFC)


class TestModifiers(unittest.TestCase):
    """Test cases for the Modifiers dataclass."""

    def test_default_values(self):
        """Test default modifier values."""
        mods = Modifiers()

        self.assertFalse(mods.auto)
        self.assertEqual(mods.speed, 1.0)
        self.assertFalse(mods.display)
        self.assertFalse(mods.inverse)
        self.assertEqual(mods.random, 0)

    def test_custom_values(self):
        """Test custom modifier values."""
        mods = Modifiers(auto=True, speed=2.0, display=True, inverse=True, random=3)

        self.assertTrue(mods.auto)
        self.assertEqual(mods.speed, 2.0)
        self.assertTrue(mods.display)
        self.assertTrue(mods.inverse)
        self.assertEqual(mods.random, 3)

    def test_speed_multiplier(self):
        """Test different speed multiplier values."""
        mods1 = Modifiers(speed=0.5)
        mods2 = Modifiers(speed=1.5)
        mods3 = Modifiers(speed=3.0)

        self.assertEqual(mods1.speed, 0.5)
        self.assertEqual(mods2.speed, 1.5)
        self.assertEqual(mods3.speed, 3.0)


class TestDanResultSong(unittest.TestCase):
    """Test cases for the DanResultSong dataclass."""

    def test_default_values(self):
        """Test default DanResultSong values."""
        song = DanResultSong()

        self.assertEqual(song.selected_difficulty, 0)
        self.assertEqual(song.diff_level, 0)
        self.assertEqual(song.song_title, "default_title")
        self.assertEqual(song.genre_index, 0)
        self.assertEqual(song.good, 0)
        self.assertEqual(song.ok, 0)
        self.assertEqual(song.bad, 0)
        self.assertEqual(song.drumroll, 0)

    def test_custom_values(self):
        """Test custom DanResultSong values."""
        song = DanResultSong(
            selected_difficulty=3,
            diff_level=10,
            song_title="Test Song",
            genre_index=5,
            good=100,
            ok=20,
            bad=5,
            drumroll=15
        )

        self.assertEqual(song.selected_difficulty, 3)
        self.assertEqual(song.diff_level, 10)
        self.assertEqual(song.song_title, "Test Song")
        self.assertEqual(song.genre_index, 5)
        self.assertEqual(song.good, 100)
        self.assertEqual(song.ok, 20)
        self.assertEqual(song.bad, 5)
        self.assertEqual(song.drumroll, 15)


class TestDanResultExam(unittest.TestCase):
    """Test cases for the DanResultExam class."""

    def test_default_values(self):
        """Test default DanResultExam values."""
        exam = DanResultExam()

        self.assertEqual(exam.progress, 0)
        self.assertEqual(exam.counter_value, 0)
        self.assertEqual(exam.bar_texture, "exam_red")
        self.assertFalse(exam.failed)

    def test_custom_values(self):
        """Test custom DanResultExam values."""
        exam = DanResultExam()
        exam.progress = 0.75
        exam.counter_value = 150
        exam.bar_texture = "exam_gold"
        exam.failed = True

        self.assertEqual(exam.progress, 0.75)
        self.assertEqual(exam.counter_value, 150)
        self.assertEqual(exam.bar_texture, "exam_gold")
        self.assertTrue(exam.failed)


class TestDanResultData(unittest.TestCase):
    """Test cases for the DanResultData dataclass."""

    def test_default_values(self):
        """Test default DanResultData values."""
        data = DanResultData()

        self.assertEqual(data.dan_color, 0)
        self.assertEqual(data.dan_title, "default_title")
        self.assertEqual(data.score, 0)
        self.assertEqual(data.gauge_length, 0.0)
        self.assertEqual(data.max_combo, 0)
        self.assertEqual(data.songs, [])
        self.assertEqual(data.exams, [])
        self.assertEqual(data.exam_data, [])

    def test_with_songs(self):
        """Test DanResultData with songs."""
        song1 = DanResultSong(song_title="Song 1")
        song2 = DanResultSong(song_title="Song 2")

        data = DanResultData(songs=[song1, song2])

        self.assertEqual(len(data.songs), 2)
        self.assertEqual(data.songs[0].song_title, "Song 1")
        self.assertEqual(data.songs[1].song_title, "Song 2")

    def test_with_exam_data(self):
        """Test DanResultData with exam data."""
        exam1 = DanResultExam()
        exam1.progress = 0.5
        exam2 = DanResultExam()
        exam2.progress = 1.0

        data = DanResultData(exam_data=[exam1, exam2])

        self.assertEqual(len(data.exam_data), 2)
        self.assertEqual(data.exam_data[0].progress, 0.5)
        self.assertEqual(data.exam_data[1].progress, 1.0)


class TestResultData(unittest.TestCase):
    """Test cases for the ResultData dataclass."""

    def test_default_values(self):
        """Test default ResultData values."""
        data = ResultData()

        self.assertEqual(data.score, 0)
        self.assertEqual(data.good, 0)
        self.assertEqual(data.ok, 0)
        self.assertEqual(data.bad, 0)
        self.assertEqual(data.max_combo, 0)
        self.assertEqual(data.total_drumroll, 0)
        self.assertEqual(data.gauge_length, 0)
        self.assertEqual(data.prev_score, 0)

    def test_custom_values(self):
        """Test custom ResultData values."""
        data = ResultData(
            score=500000,
            good=150,
            ok=30,
            bad=10,
            max_combo=120,
            total_drumroll=45,
            gauge_length=0.85,
            prev_score=450000
        )

        self.assertEqual(data.score, 500000)
        self.assertEqual(data.good, 150)
        self.assertEqual(data.ok, 30)
        self.assertEqual(data.bad, 10)
        self.assertEqual(data.max_combo, 120)
        self.assertEqual(data.total_drumroll, 45)
        self.assertEqual(data.gauge_length, 0.85)
        self.assertEqual(data.prev_score, 450000)

    def test_total_notes(self):
        """Test calculating total notes from result data."""
        data = ResultData(good=100, ok=50, bad=10)
        total = data.good + data.ok + data.bad

        self.assertEqual(total, 160)


class TestSessionData(unittest.TestCase):
    """Test cases for the SessionData dataclass."""

    def test_default_values(self):
        """Test default SessionData values."""
        session = SessionData()

        self.assertEqual(session.selected_song, Path())
        self.assertEqual(session.song_hash, "")
        self.assertEqual(session.selected_dan, [])
        self.assertEqual(session.selected_dan_exam, [])
        self.assertEqual(session.dan_color, 0)
        self.assertEqual(session.selected_difficulty, 0)
        self.assertEqual(session.song_title, "default_title")
        self.assertEqual(session.genre_index, 0)
        self.assertIsInstance(session.result_data, ResultData)
        self.assertIsInstance(session.dan_result_data, DanResultData)

    def test_custom_song_selection(self):
        """Test custom song selection."""
        song_path = Path("Songs/TestSong/song.tja")
        session = SessionData(
            selected_song=song_path,
            song_hash="abc123",
            selected_difficulty=3,
            song_title="Test Song"
        )

        self.assertEqual(session.selected_song, song_path)
        self.assertEqual(session.song_hash, "abc123")
        self.assertEqual(session.selected_difficulty, 3)
        self.assertEqual(session.song_title, "Test Song")

    def test_dan_selection(self):
        """Test dan course selection."""
        dan_songs = [(Mock(), 0, 3, 10), (Mock(), 1, 3, 10)]
        dan_exams = [Mock(), Mock(), Mock()]

        session = SessionData(
            selected_dan=dan_songs,
            selected_dan_exam=dan_exams,
            dan_color=2
        )

        self.assertEqual(len(session.selected_dan), 2)
        self.assertEqual(len(session.selected_dan_exam), 3)
        self.assertEqual(session.dan_color, 2)

    def test_result_data_independence(self):
        """Test that each session has independent result data."""
        session1 = SessionData()
        session2 = SessionData()

        session1.result_data.score = 100000

        self.assertEqual(session1.result_data.score, 100000)
        self.assertEqual(session2.result_data.score, 0)


class TestCamera(unittest.TestCase):
    """Test cases for the Camera class."""

    @patch('libs.global_data.ray')
    def test_default_values(self, mock_ray):
        """Test default Camera values."""
        mock_ray.Vector2 = Mock(return_value=Mock())
        mock_ray.BLACK = Mock()

        camera = Camera()

        self.assertEqual(camera.zoom, 1.0)
        self.assertEqual(camera.h_scale, 1.0)
        self.assertEqual(camera.v_scale, 1.0)
        self.assertEqual(camera.rotation, 0.0)


class TestGlobalData(unittest.TestCase):
    """Test cases for the GlobalData dataclass."""

    def test_default_values(self):
        """Test default GlobalData values."""
        data = GlobalData()

        self.assertEqual(data.songs_played, 0)
        self.assertIsInstance(data.camera, Camera)
        self.assertEqual(data.song_hashes, {})
        self.assertEqual(data.song_paths, {})
        self.assertEqual(data.score_db, "")
        self.assertEqual(data.song_progress, 0.0)
        self.assertEqual(data.total_songs, 0)
        self.assertEqual(data.hit_sound, [0, 0, 0])
        self.assertEqual(data.player_num, PlayerNum.P1)
        self.assertEqual(data.input_locked, 0)

    def test_modifiers_list(self):
        """Test that modifiers list has correct size."""
        data = GlobalData()

        self.assertEqual(len(data.modifiers), 3)
        self.assertIsInstance(data.modifiers[0], Modifiers)
        self.assertIsInstance(data.modifiers[1], Modifiers)
        self.assertIsInstance(data.modifiers[2], Modifiers)

    def test_session_data_list(self):
        """Test that session data list has correct size."""
        data = GlobalData()

        self.assertEqual(len(data.session_data), 3)
        self.assertIsInstance(data.session_data[0], SessionData)
        self.assertIsInstance(data.session_data[1], SessionData)
        self.assertIsInstance(data.session_data[2], SessionData)

    def test_song_hashes_dict(self):
        """Test song_hashes dictionary operations."""
        data = GlobalData()

        data.song_hashes["hash1"] = [{"path": "Songs/Song1"}]
        data.song_hashes["hash2"] = [{"path": "Songs/Song2"}]

        self.assertEqual(len(data.song_hashes), 2)
        self.assertIn("hash1", data.song_hashes)
        self.assertIn("hash2", data.song_hashes)

    def test_song_paths_dict(self):
        """Test song_paths dictionary operations."""
        data = GlobalData()

        path1 = Path("Songs/Song1/song.tja")
        path2 = Path("Songs/Song2/song.tja")

        data.song_paths[path1] = "hash1"
        data.song_paths[path2] = "hash2"

        self.assertEqual(len(data.song_paths), 2)
        self.assertEqual(data.song_paths[path1], "hash1")
        self.assertEqual(data.song_paths[path2], "hash2")

    def test_input_locked_counter(self):
        """Test input_locked as a counter."""
        data = GlobalData()

        self.assertEqual(data.input_locked, 0)

        data.input_locked += 1
        self.assertEqual(data.input_locked, 1)

        data.input_locked += 1
        self.assertEqual(data.input_locked, 2)

        data.input_locked -= 1
        self.assertEqual(data.input_locked, 1)

    def test_songs_played_counter(self):
        """Test songs_played counter."""
        data = GlobalData()

        self.assertEqual(data.songs_played, 0)

        data.songs_played += 1
        self.assertEqual(data.songs_played, 1)

        data.songs_played += 1
        self.assertEqual(data.songs_played, 2)

    def test_hit_sound_indices(self):
        """Test hit_sound indices list."""
        data = GlobalData()

        self.assertEqual(data.hit_sound, [0, 0, 0])

        data.hit_sound[0] = 1
        data.hit_sound[1] = 2
        data.hit_sound[2] = 3

        self.assertEqual(data.hit_sound, [1, 2, 3])


class TestGlobalDataSingleton(unittest.TestCase):
    """Test cases for the global_data singleton."""

    def test_global_data_exists(self):
        """Test that global_data instance exists."""
        self.assertIsInstance(global_data, GlobalData)

    def test_global_data_modifiable(self):
        """Test that global_data can be modified."""
        original_songs_played = global_data.songs_played
        global_data.songs_played += 1

        self.assertEqual(global_data.songs_played, original_songs_played + 1)

        # Reset for other tests
        global_data.songs_played = original_songs_played


class TestResetSession(unittest.TestCase):
    """Test cases for reset_session function."""

    def test_reset_session_clears_p1_data(self):
        """Test that reset_session clears player 1 data."""
        global_data.session_data[1].result_data.score = 100000
        global_data.session_data[1].song_title = "Test Song"

        reset_session()

        self.assertIsInstance(global_data.session_data[1], SessionData)
        self.assertEqual(global_data.session_data[1].song_title, "default_title")

    def test_reset_session_clears_p2_data(self):
        """Test that reset_session clears player 2 data."""
        global_data.session_data[2].result_data.score = 50000
        global_data.session_data[2].selected_difficulty = 3

        reset_session()

        self.assertIsInstance(global_data.session_data[2], SessionData)
        self.assertEqual(global_data.session_data[2].selected_difficulty, 0)

    def test_reset_session_preserves_index_0(self):
        """Test that reset_session doesn't affect index 0."""
        original_data = global_data.session_data[0]
        original_data.song_title = "Should Not Change"

        reset_session()

        self.assertEqual(global_data.session_data[0].song_title, "Should Not Change")

    def test_reset_session_creates_new_instances(self):
        """Test that reset_session creates new SessionData instances."""
        old_p1_session = global_data.session_data[1]
        old_p2_session = global_data.session_data[2]

        reset_session()

        self.assertIsNot(global_data.session_data[1], old_p1_session)
        self.assertIsNot(global_data.session_data[2], old_p2_session)


class TestDataclassIntegration(unittest.TestCase):
    """Integration tests for dataclass interactions."""

    def test_session_with_result_data(self):
        """Test SessionData with populated ResultData."""
        session = SessionData()
        session.result_data.score = 750000
        session.result_data.good = 200
        session.result_data.max_combo = 180

        self.assertEqual(session.result_data.score, 750000)
        self.assertEqual(session.result_data.good, 200)
        self.assertEqual(session.result_data.max_combo, 180)

    def test_session_with_dan_result_data(self):
        """Test SessionData with populated DanResultData."""
        session = SessionData()
        session.dan_result_data.dan_title = "10th Dan"
        session.dan_result_data.dan_color = 5

        song1 = DanResultSong(song_title="Dan Song 1")
        song2 = DanResultSong(song_title="Dan Song 2")
        session.dan_result_data.songs = [song1, song2]

        self.assertEqual(session.dan_result_data.dan_title, "10th Dan")
        self.assertEqual(len(session.dan_result_data.songs), 2)

    def test_modifiers_independent_per_player(self):
        """Test that each player has independent modifiers."""
        data = GlobalData()

        data.modifiers[1].speed = 2.0
        data.modifiers[2].speed = 1.5

        self.assertEqual(data.modifiers[1].speed, 2.0)
        self.assertEqual(data.modifiers[2].speed, 1.5)
        self.assertEqual(data.modifiers[0].speed, 1.0)


if __name__ == '__main__':
    unittest.main()
