import logging

import pyray as ray

from libs.audio import audio
from libs.global_data import global_data
from libs.utils import get_current_ms
from scenes.game import GameScreen

logger = logging.getLogger(__name__)

class AIBattleGameScreen(GameScreen):
    def global_keys(self):
        if ray.is_key_pressed(global_data.config["keys"]["restart_key"]):
            if self.song_music is not None:
                audio.stop_music_stream(self.song_music)
            self.init_tja(global_data.session_data[global_data.player_num].selected_song)
            audio.play_sound('restart', 'sound')
            self.song_started = False

        if ray.is_key_pressed(global_data.config["keys"]["back_key"]):
            if self.song_music is not None:
                audio.stop_music_stream(self.song_music)
            return self.on_screen_end('AI_SELECT')

        if ray.is_key_pressed(global_data.config["keys"]["pause_key"]):
            self.pause_song()

    def update(self):
        super(GameScreen, self).update()
        current_time = get_current_ms()
        self.transition.update(current_time)
        if not self.paused:
            self.current_ms = current_time - self.start_ms
        if self.transition.is_finished:
            self.start_song(self.current_ms)
        else:
            self.start_ms = current_time - self.tja.metadata.offset*1000
        self.update_background(current_time)

        if self.song_music is not None:
            audio.update_music_stream(self.song_music)

        self.player_1.update(self.current_ms, current_time, self.background)
        self.song_info.update(current_time)
        self.result_transition.update(current_time)
        if self.result_transition.is_finished and not audio.is_sound_playing('result_transition'):
            logger.info("Result transition finished, moving to RESULT screen")
            return self.on_screen_end('AI_SELECT')
        elif self.current_ms >= self.player_1.end_time:
            session_data = global_data.session_data[global_data.player_num]
            session_data.result_data.score, session_data.result_data.good, session_data.result_data.ok, session_data.result_data.bad, session_data.result_data.max_combo, session_data.result_data.total_drumroll = self.player_1.get_result_score()
            if self.player_1.gauge is not None:
                session_data.result_data.gauge_length = self.player_1.gauge.gauge_length
            if self.end_ms != 0:
                if current_time >= self.end_ms + 1000:
                    if self.player_1.ending_anim is None:
                        self.spawn_ending_anims()
                if current_time >= self.end_ms + 8533.34:
                    if not self.result_transition.is_started:
                        self.result_transition.start()
                        audio.play_sound('result_transition', 'voice')
                        logger.info("Result transition started and voice played")
            else:
                self.end_ms = current_time

        return self.global_keys()
