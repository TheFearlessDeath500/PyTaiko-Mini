import logging

from scenes.song_select import SongSelectScreen

logger = logging.getLogger(__name__)

class PracticeSongSelectScreen(SongSelectScreen):
    def on_screen_start(self):
        super().on_screen_start()

    def update_players(self, current_time) -> str:
        self.player_1.update(current_time)
        if self.text_fade_out.is_finished:
            self.player_1.selected_song = True
        next_screen = "GAME_PRACTICE"
        return next_screen
