"""
Scene Training
Handles both Dummy and Head-to-Head training modes for pets.
"""

import pygame

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from components.window_xai import WindowXai
from core import game_globals, runtime_globals
from core.combat.count_training import CountMatchTraining
from core.combat.dummy_training import DummyTraining
from core.combat.excite_training import ExciteTraining
from core.combat.head_training import HeadToHeadTraining
from core.constants import *
from core.utils.pet_utils import get_training_targets
from core.utils.pygame_utils import get_font, sprite_load_percent
from core.utils.scene_utils import change_scene

#=====================================================================
# SceneTraining (Training Menu)
#=====================================================================

class SceneTraining:
    """
    Menu scene where players choose between Dummy or Head-to-Head training.
    """

    def __init__(self) -> None:
        self.background = WindowBackground(False)
        self.font = get_font(FONT_SIZE_LARGE)

        self.phase = "menu"
        self.mode = None

        self.options = []
        if runtime_globals.dmc_enabled:
            self.options.append(("Dummy", sprite_load_percent(DUMMY_TRAINING_ICON_PATH, percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")))
            self.options.append(("HeadtoHead", sprite_load_percent(HEAD_TRAINING_ICON_PATH, percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")))

        if runtime_globals.penc_enabled:
            self.options.append(("CountMatch", sprite_load_percent(SHAKE_MATCH_ICON_PATH, percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")))

        if runtime_globals.dmx_enabled:
            self.options.append(("Excite", sprite_load_percent(EXCITE_MATCH_ICON_PATH, percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")))

        self.selectionBackground = sprite_load_percent(PET_SELECTION_BACKGROUND_PATH, percent=100, keep_proportion=True, base_on="width")
        self.backgroundIm = sprite_load_percent(TRAINING_BACKGROUND_PATH, percent=100, keep_proportion=True, base_on="width")

        self.pet_list_window = WindowPetList(lambda: get_training_targets())

        # Xai window position and size scaled
        xai_x = int(SCREEN_WIDTH - (79 * UI_SCALE))
        xai_y = int(123 * UI_SCALE)
        xai_size = int(48 * UI_SCALE)
        self.xai_window = WindowXai(xai_x, xai_y, xai_size, xai_size, game_globals.xai)

        self.menu_window = WindowHorizontalMenu(
            options=self.options,
            get_selected_index_callback=lambda: runtime_globals.training_index,
        )

        runtime_globals.game_console.log("[SceneTraining] Training scene initialized.")

    def update(self):
        if self.mode:
            self.mode.update()

    def draw(self, surface: pygame.Surface):
        self.background.draw(surface)
        if self.phase == "menu":
            # Desenha menu horizontal
            if len(self.options) > 2:
                self.menu_window.draw(surface, x=int(72 * UI_SCALE), y=int(16 * UI_SCALE), spacing=int(30 * UI_SCALE))
            else:
                self.menu_window.draw(surface, x=int(16 * UI_SCALE), y=int(16 * UI_SCALE), spacing=int(16 * UI_SCALE))

            # Desenha pets na parte inferior
            self.pet_list_window.draw(surface)
            if self.options[runtime_globals.training_index][0] == "Excite":
                self.xai_window.draw(surface)
        elif self.mode:
            surface.blit(self.backgroundIm, (0, 0))
            self.mode.draw(surface)

    def handle_event(self, input_action):
        """
        Handles keyboard and GPIO button inputs for menu interactions.
        """
        if input_action:
            if self.phase == "menu":
                self.handle_menu_input(input_action)
            elif self.mode:
                self.mode.handle_event(input_action)

    def handle_menu_input(self, input_action):
        if input_action == "B":
            runtime_globals.game_sound.play("cancel")
            change_scene("game")
        elif input_action in ("LEFT", "RIGHT"):
            runtime_globals.game_sound.play("menu")
            delta = -1 if input_action == "LEFT" else 1
            runtime_globals.training_index = (runtime_globals.training_index + delta) % len(self.options)
        elif input_action == "A":
            if self.options[runtime_globals.training_index][0] == "Dummy":
                if len(get_training_targets())  > 0:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "dummy"
                    self.mode = DummyTraining()
                    runtime_globals.game_console.log("Starting Dummy Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            elif self.options[runtime_globals.training_index][0] == "HeadtoHead":
                if len(get_training_targets())  > 1:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "headtohead"
                    self.mode = HeadToHeadTraining()
                    runtime_globals.game_console.log("Starting Head-to-Head Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            elif self.options[runtime_globals.training_index][0] == "CountMatch":
                if len(get_training_targets())  > 0:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "count"
                    self.mode = CountMatchTraining()
                    runtime_globals.game_console.log("Starting Dummy Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            elif self.options[runtime_globals.training_index][0] == "Excite":
                if len(get_training_targets())  > 0:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "excite"
                    self.mode = ExciteTraining()
                    runtime_globals.game_console.log("Starting Dummy Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
        elif input_action == "SELECT" and self.phase == "menu":
            runtime_globals.game_sound.play("menu")
            runtime_globals.strategy_index = (runtime_globals.strategy_index + 1) % 2
