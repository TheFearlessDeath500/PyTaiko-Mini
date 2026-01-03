import json
import logging

import pyray as ray

from libs.audio import audio
from libs.config import save_config
from libs.global_objects import Indicator
from libs.screen import Screen
from libs.texture import tex
from libs.utils import (
    OutlinedText,
    get_current_ms,
    global_data,
    is_l_don_pressed,
    is_l_kat_pressed,
    is_r_don_pressed,
    is_r_kat_pressed,
)

logger = logging.getLogger(__name__)

class BaseOptionBox:
    def __init__(self, name: str, description: str):
        self.name = OutlinedText(name, 30, ray.WHITE)
        self.description = description
        self.is_highlighted = False

    def draw(self):
        if self.is_highlighted:
            tex.draw_texture('background', 'title_highlight')
        else:
            tex.draw_texture('background', 'title')
        text_x = tex.textures['background']['title'].x[0] + (tex.textures['background']['title'].width//2) - (self.name.texture.width//2)
        text_y = tex.textures['background']['title'].y[0]
        self.name.draw(outline_color=ray.BLACK, x=text_x, y=text_y)

class Box:
    """Box class for the entry screen"""
    def __init__(self, text: OutlinedText, box_options: dict):
        self.text = text
        self.x = 10 * tex.screen_scale
        self.y = -50 * tex.screen_scale
        self.move = tex.get_animation(0)
        self.is_selected = False
        self.outline_color = ray.Color(109, 68, 24, 255)
        self.direction = 1
        self.target_position = float('inf')
        self.start_position = self.y
        language = global_data.config["general"]["language"]
        self.options = [BaseOptionBox(box_options[option]["name"][language], box_options[option]["description"][language]) for option in box_options]

    def __repr__(self):
        return str(self.__dict__)

    def move_left(self):
        """Move the box left"""
        if self.y != self.target_position and self.target_position != float('inf'):
            return False
        self.move.start()
        self.direction = 1
        self.start_position = self.y
        self.target_position = self.y + (100 * tex.screen_scale * self.direction)

        if self.target_position >= 650:
            self.target_position = -50 + (self.target_position - 650)

        return True

    def move_right(self):
        """Move the box right"""
        if self.y != self.target_position and self.target_position != float('inf'):
            return False
        self.move.start()
        self.start_position = self.y
        self.direction = -1
        self.target_position = self.y + (100 * tex.screen_scale * self.direction)

        if self.target_position < -50:
            self.target_position = 650 + (self.target_position + 50)

        return True

    def update(self, current_time_ms: float, is_selected: bool):
        self.move.update(current_time_ms)
        self.is_selected = is_selected
        if self.move.is_finished:
            self.y = self.target_position
        else:
            self.y = self.start_position + (self.move.attribute * self.direction)

    def _draw_highlighted(self):
        tex.draw_texture('box', 'box_highlight', x=self.x, y=self.y)

    def _draw_text(self):
        text_x = self.x + (tex.textures['box']['box'].width//2) - (self.text.texture.width//2)
        text_y = self.y + (tex.textures['box']['box'].height//2) - (self.text.texture.height//2)
        if self.is_selected:
            self.text.draw(outline_color=ray.BLACK, x=text_x, y=text_y)
        else:
            self.text.draw(outline_color=self.outline_color, x=text_x, y=text_y)

    def draw(self):
        tex.draw_texture('box', 'box', x=self.x, y=self.y)
        if self.is_selected:
            self._draw_highlighted()
        self._draw_text()

class BoxManager:
    """BoxManager class for the entry screen"""
    def __init__(self, settings_template: dict):
        language = global_data.config["general"]["language"]
        self.boxes = [Box(OutlinedText(settings_template[config_name]["name"][language], tex.skin_config["entry_box_text"].font_size - int(5*tex.screen_scale), ray.WHITE, outline_thickness=5), settings_template[config_name]["options"]) for config_name in settings_template]
        self.num_boxes = len(self.boxes)
        self.selected_box_index = 3
        self.is_2p = False

        for i, box in enumerate(self.boxes):
            box.y += 100*i
            box.start_position += 100*i

    def move_left(self):
        """Move the cursor to the left"""
        moved = True
        for box in self.boxes:
            if not box.move_left():
                moved = False

        if moved:
            self.selected_box_index = (self.selected_box_index - 1) % self.num_boxes

    def move_right(self):
        """Move the cursor to the right"""
        moved = True
        for box in self.boxes:
            if not box.move_right():
                moved = False

        if moved:
            self.selected_box_index = (self.selected_box_index + 1) % self.num_boxes

    def update(self, current_time_ms: float):
        for i, box in enumerate(self.boxes):
            is_selected = i == self.selected_box_index
            box.update(current_time_ms, is_selected)

    def draw(self):
        for box in self.boxes:
            box.draw()

class SettingsScreen(Screen):
    def on_screen_start(self):
        super().on_screen_start()
        self.config = global_data.config
        self.indicator = Indicator(Indicator.State.SELECT)
        self.template = json.loads((tex.graphics_path / "settings_template.json").read_text(encoding='utf-8'))
        self.box_manager = BoxManager(self.template)

    def on_screen_end(self, next_screen: str):
        save_config(self.config)
        global_data.config = self.config
        audio.init_audio_device()
        logger.info("Settings saved and audio device re-initialized")
        return next_screen

    def handle_input(self):
        if is_l_kat_pressed():
            audio.play_sound('kat', 'sound')
            self.box_manager.move_left()
        elif is_r_kat_pressed():
            audio.play_sound('kat', 'sound')
            self.box_manager.move_right()

    def update(self):
        super().update()

        self.handle_input()

        current_time = get_current_ms()
        self.indicator.update(current_time)
        self.box_manager.update(current_time)

    def draw(self):
        tex.draw_texture('background', 'background')
        self.box_manager.draw()
        tex.draw_texture('background', 'footer')
        self.indicator.draw(tex.skin_config['song_select_indicator'].x, tex.skin_config['song_select_indicator'].y)
        tex.draw_texture('background', 'overlay', scale=0.70)
