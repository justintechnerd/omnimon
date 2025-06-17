import pygame
from datetime import datetime

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from core import runtime_globals
from core.constants import *
from core.utils.pet_utils import distribute_pets_evenly, get_selected_pets
from core.utils.pygame_utils import sprite_load_percent
from core.utils.scene_utils import change_scene


#=====================================================================
# SceneSleepMenu
#=====================================================================
class SceneSleepMenu:
    def __init__(self) -> None:
        self.background = WindowBackground()
        # Use new method for icons, scale to option icon size and keep proportions
        self.options = [
            ("Sleep", sprite_load_percent("resources/SleepIcon.png", percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")),
            ("Wake", sprite_load_percent("resources/WakeIcon.png", percent=(OPTION_ICON_SIZE / SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height"))
        ]

        self.selected_index = 0
        runtime_globals.strategy_index = 0
        
        self.pet_list_window = WindowPetList(lambda: self.pets_can())
        self.menu_window = WindowHorizontalMenu(
            options=self.options,
            get_selected_index_callback=lambda: self.selected_index,
        )

        runtime_globals.game_console.log("[SceneSleepMenu] Sleep menu initialized.")

    def update(self) -> None:
        pass

    def pets_can(self):
        if self.selected_index == 0:
            return self.pets_can_sleep()
        else:
            return self.pets_can_wake()

    def pets_can_sleep(self):
        return [pet for pet in get_selected_pets() if pet.stage > 1 and pet.state != "nap" and pet.state != "dead"]

    def pets_can_wake(self):
        return [pet for pet in get_selected_pets() if pet.state == "nap"]
    
    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)

        # Desenha menu horizontal (positions scaled)
        self.menu_window.draw(surface, x=int(16 * UI_SCALE), y=int(16 * UI_SCALE), spacing=int(16 * UI_SCALE))

        # Desenha pets na parte inferior
        self.pet_list_window.draw(surface)

    def handle_event(self, input_action) -> None:
        """
        Handles keyboard and GPIO button inputs for menu navigation and selection.
        """
        if input_action:
            if input_action == "B":  # Maps to ESC (PC) & START button (Pi)
                runtime_globals.game_sound.play("cancel")
                change_scene("game")

            elif input_action in ("LEFT", "RIGHT"):  # Navigate menu left/right
                runtime_globals.game_sound.play("menu")
                direction = 1 if input_action == "RIGHT" else -1
                self.selected_index = (self.selected_index + direction) % len(self.options)

            elif input_action == "A":  # Maps to ENTER (PC) & A button (Pi)
                self.confirm_selection()

    def confirm_selection(self) -> None:
        if self.selected_index == 0:
            self.put_pets_to_sleep()
        else:
            self.wake_pets()

    def put_pets_to_sleep(self) -> None:
        now = datetime.now()

        pets = self.pets_can_sleep()
        if len(pets) > 0:
            runtime_globals.game_sound.play("menu")
        else:
            runtime_globals.game_sound.play("cancel")
            return
        
        for pet in pets:
            pet.set_state("nap")
            pet.sleep_start_time = now
        runtime_globals.game_console.log("[SceneSleepMenu] Pets put to sleep manually.")
        distribute_pets_evenly()
        change_scene("game")

    def wake_pets(self) -> None:
        now = datetime.now()

        pets = self.pets_can_wake()
        if len(pets) > 0:
            runtime_globals.game_sound.play("menu")
        else:
            runtime_globals.game_sound.play("cancel")
            return

        for pet in pets:
            if pet.state == "nap":
                slept_hours = 0
                if hasattr(pet, "sleep_start_time"):
                    slept_hours = (now - pet.sleep_start_time).total_seconds() // 3600

                pet.set_state("idle")

                if slept_hours >= SLEEP_RECOVERY_HOURS:
                    pet.dp = pet.energy
                    runtime_globals.game_console.log(f"[SceneSleepMenu] {pet.name} fully recharged DP after sleeping {slept_hours}h.")

        runtime_globals.game_console.log("[SceneSleepMenu] Pets woke up manually.")
        distribute_pets_evenly()
        change_scene("game")
