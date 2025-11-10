import logging
from pathlib import Path

from libs.background import Background
from scenes.game import GameScreen, JudgeCounter

logger = logging.getLogger(__name__)

class PracticeGameScreen(GameScreen):
    def on_screen_start(self):
        super().on_screen_start()
        self.background = Background(1, self.bpm, scene_preset='PRACTICE')

    def init_tja(self, song: Path):
        super().init_tja(song)
        self.player_1.judge_counter = JudgeCounter()
