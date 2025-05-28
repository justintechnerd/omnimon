"""
Scene Training
Handles both Dummy and Head-to-Head training modes for pets.
"""

import pygame

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from core import runtime_globals
from core.combat.count_training import CountMatchTraining
from core.combat.dummy_training import DummyTraining
from core.combat.head_training import HeadToHeadTraining
from core.constants import *
from core.utils import change_scene, get_font, get_training_targets


#=====================================================================
# Training Constants
#=====================================================================

ALERT_DURATION_FRAMES = 50
WAIT_AFTER_BAR_FRAMES = 30
IMPACT_DURATION_FRAMES = 60
WAIT_ATTACK_READY_FRAMES = 10
RESULT_SCREEN_FRAMES = 90
BAR_HOLD_TIME_MS = 2500
ATTACK_SPEED = 5

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
            self.options.append(("Dummy", pygame.image.load(DUMMY_TRAINING_ICON_PATH).convert_alpha()))
            self.options.append(("HeadtoHead", pygame.image.load(HEAD_TRAINING_ICON_PATH).convert_alpha()))

        if runtime_globals.penc_enabled:
            self.options.append(("CountMatch", pygame.image.load(SHAKE_MATCH_ICON_PATH).convert_alpha()))

        self.selectionBackground = pygame.image.load(PET_SELECTION_BACKGROUND_PATH).convert_alpha()
        self.backgroundIm = pygame.image.load(TRAINING_BACKGROUND_PATH).convert_alpha()

        self.pet_list_window = WindowPetList(lambda: get_training_targets())

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
                self.menu_window.draw(surface, x=72, y=16, spacing=30)
            else:
                self.menu_window.draw(surface, x=16, y=16, spacing=16)

            # Desenha pets na parte inferior
            self.pet_list_window.draw(surface)
        elif self.mode:
            surface.blit(self.backgroundIm, (0,0))
            
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
            if runtime_globals.training_index == 0:
                if len(get_training_targets())  > 0:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "dummy"
                    self.mode = DummyTraining()
                    runtime_globals.game_console.log("Starting Dummy Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            elif runtime_globals.training_index == 1:
                if len(get_training_targets())  > 1:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "headtohead"
                    self.mode = HeadToHeadTraining()
                    runtime_globals.game_console.log("Starting Head-to-Head Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            elif runtime_globals.training_index == 2:
                if len(get_training_targets())  > 0:
                    runtime_globals.game_sound.play("menu")
                    self.phase = "count"
                    self.mode = CountMatchTraining()
                    runtime_globals.game_console.log("Starting Dummy Training.")
                    for pet in get_training_targets():
                        pet.check_disturbed_sleep()
                else:
                    runtime_globals.game_sound.play("cancel")
            
        elif input_action == "SELECT" and self.phase == "menu":
            runtime_globals.game_sound.play("menu")
            runtime_globals.strategy_index = (runtime_globals.strategy_index + 1) % 2
