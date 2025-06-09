"""
Scene Training
Handles both Dummy and Head-to-Head training modes for pets.
"""
import pygame

from components.window_background import WindowBackground
from components.window_horizontalmenu import WindowHorizontalMenu
from components.window_petview import WindowPetList
from core import game_globals, runtime_globals
from core.combat.battle_encounter_dmc import BattleEncounterDMC
from core.combat.battle_encounter_penc import BattleEncounterPENC
from core.combat.battle_encounter_versus import BattleEncounterVersus
from core.constants import *
from core.utils import blit_with_shadow, change_scene, get_battle_targets, get_font, sprite_load


#=====================================================================
# Training Constants
#=====================================================================

ALERT_DURATION_FRAMES = 50
WAIT_AFTER_BAR_FRAMES = 30
IMPACT_DURATION_FRAMES = 60
WAIT_ATTACK_READY_FRAMES = 19
RESULT_SCREEN_FRAMES = 60
BAR_HOLD_TIME_MS = 2500
ATTACK_SPEED = 4

#=====================================================================
# SceneTraining (Training Menu)
#=====================================================================

class SceneBattle:
    """
    Menu scene where players choose between Dummy or Head-to-Head training.
    """

    def __init__(self) -> None:
        self.background = WindowBackground(False)
        self.font = get_font(FONT_SIZE_LARGE)

        self.phase = "menu"
        self.mode = None

        self.selectionBackground = sprite_load(PET_SELECTION_BACKGROUND_PATH)
        self.jogress_slot_on = sprite_load(PET_SELECTION_SMALL_ON_PATH)
        self.jogress_slot_off = sprite_load(PET_SELECTION_SMALL_OFF_PATH)


        self.options1 = [("Adventure", sprite_load(BATTLE_ICON_PATH)),
                         ("Versus", sprite_load(HEAD_TRAINING_ICON_PATH)),
                        ("Jogress", sprite_load(JOGRESS_ICON_PATH))]
        
        self.options2 = []
        self.module_lookup = []
        self.jogress_ready = False
        self.versus_ready = False
         
        for module in runtime_globals.game_modules.values():
            if module.adventure_mode:
                self.options2.append((module.name, sprite_load(module.folder_path + "/BattleIcon.png")))
                self.module_lookup.append(module.name)
        
        self.selected_module = None

        self.selectionBackground = sprite_load(PET_SELECTION_BACKGROUND_PATH)
        self.backgroundIm = sprite_load(TRAINING_BACKGROUND_PATH)

        self.pet_list_window = WindowPetList(lambda: get_battle_targets())

        if runtime_globals.battle_index.get("menu") == None:
            runtime_globals.battle_index["menu"] = 0
        if runtime_globals.battle_index.get("module") == None:
            runtime_globals.battle_index["module"] = 0
        if runtime_globals.battle_index.get("battle_select") == None:
            runtime_globals.battle_index["battle_select"] = 0

        self.menu_window1 = WindowHorizontalMenu(
            options=self.options1,
            get_selected_index_callback=lambda: runtime_globals.battle_index["menu"],
        )

        self.menu_window2 = WindowHorizontalMenu(
            options=self.options2,
            get_selected_index_callback=lambda: runtime_globals.battle_index["module"],
        )

        self.menu = self.menu_window1
        runtime_globals.game_console.log("[SceneTraining] Training scene initialized.")

    def update(self):
        if self.mode:
            self.mode.update()

    def draw(self, surface: pygame.Surface):
        self.background.draw(surface)

        if self.phase in ["menu", "module", "battle_select"]:
            # Desenha menu horizontal
            if len(self.menu.options) > 2:
                self.menu.draw(surface, x=72, y=16, spacing=30)
            else:
                self.menu.draw(surface, x=16, y=16, spacing=16)

            # Desenha pets na parte inferior
            self.pet_list_window.draw(surface)
        elif self.phase == "jogress":
            self.draw_selection_phase(
                surface,
                prompt_text="Press START to confirm Jogress",
                require_compatibility=True
            )
        elif self.phase == "versus":
            self.draw_selection_phase(
                surface,
                prompt_text="Press START to begin Battle",
                require_compatibility=False
            )
        elif self.mode:
            self.mode.draw(surface)

    def draw_selection_phase(self, surface, prompt_text, require_compatibility=False):
        self.pet_list_window.draw(surface)

        selected = self.pet_list_window.selected_indices  # 0–2 indices
        is_compatible = self.check_jogress_compatibility(selected) if require_compatibility else True

        for i in range(2):
            x = 16 + i * (self.jogress_slot_off.get_width() + 16)
            y = 16

            # Slot sprite (ON if selected and valid, else OFF)
            if i < len(selected) and is_compatible:
                blit_with_shadow(surface,self.jogress_slot_on, (x, y))
            else:
                blit_with_shadow(surface,self.jogress_slot_off, (x, y))

            # Draw pet sprite inside slot
            if i < len(selected):
                pet = game_globals.pet_list[selected[i]]
                sprite = self.pet_list_window.get_scaled_sprite(pet)
                sprite_x = x + (self.jogress_slot_on.get_width() - sprite.get_width()) // 2
                sprite_y = y + (self.jogress_slot_on.get_height() - sprite.get_height()) // 2
                blit_with_shadow(surface,sprite, (sprite_x, sprite_y))

        # Show prompt if ready
        ready = (self.jogress_ready if require_compatibility else self.versus_ready)
        if ready:
            font = get_font(20)
            text = font.render(prompt_text, True, FONT_COLOR_GREEN)
            text_x = (SCREEN_WIDTH - text.get_width()) // 2
            text_y = SCREEN_HEIGHT - 120
            blit_with_shadow(surface, text, (text_x, text_y))

    def handle_event(self, input_action):
        if self.phase == "menu":
            self.handle_menu_input(input_action)
        elif self.phase == "module":
            self.handle_module_input(input_action)
        elif self.phase == "battle_select":
            self.handle_battle_select_input(input_action)
        elif self.phase == "jogress":
            self.handle_jogress_input(input_action)
        elif self.phase == "versus":
            self.handle_versus_input(input_action)
        elif self.mode:
            self.mode.handle_event(input_action)

    def handle_menu_input(self, input_action):
        if input_action == "B":
            runtime_globals.game_sound.play("cancel")
            change_scene("game")
        elif input_action in ("LEFT", "RIGHT"):
            runtime_globals.game_sound.play("menu")
            delta = -1 if input_action == "LEFT" else 1
            runtime_globals.battle_index[self.phase] = (runtime_globals.battle_index[self.phase] + delta) % len(self.menu.options)
        elif input_action == "A":
            if runtime_globals.battle_index[self.phase] == 0: #Adventure
                runtime_globals.game_sound.play("menu")
                self.phase = "module"
                self.menu = self.menu_window2
            elif runtime_globals.battle_index[self.phase] == 1: #Versus
                self.phase = "versus"
                self.pet_list_window.select_mode = True
            elif runtime_globals.battle_index[self.phase] == 2: #Jogress
                self.phase = "jogress"
                self.pet_list_window.select_mode = True

    def handle_module_input(self, input_action):
        if input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.phase = "menu"
            self.menu = self.menu_window1
        elif input_action in ("LEFT", "RIGHT"):
            runtime_globals.game_sound.play("menu")
            delta = -1 if input_action == "LEFT" else 1
            runtime_globals.battle_index[self.phase] = (runtime_globals.battle_index[self.phase] + delta) % len(self.menu.options)
        elif input_action == "A":
            runtime_globals.game_sound.play("menu")
            selected_index = runtime_globals.battle_index["module"]
            self.selected_module = self.module_lookup[selected_index]
            runtime_globals.battle_index[self.phase] = 0
            self.phase = "battle_select"
            if self.selected_module == "DMC":
                self.options3 = [(f"Area {game_globals.battle_round[self.selected_module]}-{game_globals.battle_area[self.selected_module]}", sprite_load(NEXT_BATTLE_ICON_PATH)),
                        ("Restart", sprite_load(RESTART_BATTLE_ICON_PATH))]
            else:
                self.options3 = [(f"Area {game_globals.battle_area[self.selected_module]}", sprite_load(NEXT_BATTLE_ICON_PATH)),
                        ("Restart", sprite_load(RESTART_BATTLE_ICON_PATH))]
            self.menu_window3 = WindowHorizontalMenu(
                options=self.options3,
                get_selected_index_callback=lambda: runtime_globals.battle_index["battle_select"],
            )
            self.menu = self.menu_window3

    def handle_battle_select_input(self, input_action):
        if input_action == "B":
            runtime_globals.game_sound.play("cancel")
            self.phase = "module"
            self.menu = self.menu_window2
        elif input_action in ("LEFT", "RIGHT"):
            runtime_globals.game_sound.play("menu")
            delta = -1 if input_action == "LEFT" else 1
            runtime_globals.battle_index[self.phase] = (runtime_globals.battle_index[self.phase] + delta) % len(self.menu.options)
        elif input_action == "A":
            runtime_globals.game_sound.play("menu")
            if runtime_globals.battle_index[self.phase] == 1:
                game_globals.battle_round[self.selected_module] = 1
                game_globals.battle_area[self.selected_module] = 1
            self.phase = "next"
            for pet in get_battle_targets():
                pet.check_disturbed_sleep()
            if self.selected_module == "DMC":
                self.mode = BattleEncounterDMC(self.selected_module)
            elif self.selected_module == "PenC":
                game_globals.battle_round[self.selected_module] = 1
                self.mode = BattleEncounterPENC(self.selected_module)
            runtime_globals.game_console.log("Starting Battle.")

    def handle_jogress_input(self, input_action):
        if input_action == "LEFT" or input_action == "RIGHT":
            self.pet_list_window.handle_input(input_action)
        elif input_action == "A":
            self.pet_list_window.handle_input(input_action)
            if len(self.pet_list_window.selected_indices) == 2:
                self.jogress_ready = self.check_jogress_compatibility(self.pet_list_window.selected_indices)
            else:
                self.jogress_ready = False
        elif input_action == "B":
            # Cancel Jogress selection
            self.pet_list_window.selected_indices.clear()
            self.phase = "menu"
            self.pet_list_window.select_mode = False
            runtime_globals.game_sound.play("cancel")
        elif input_action == "START":
            if self.jogress_ready:
                self.perform_jogress()
            else:
                runtime_globals.game_sound.play("fail")

    def handle_versus_input(self, input_action):
        if input_action in ("LEFT", "RIGHT"):
            self.pet_list_window.handle_input(input_action)
        elif input_action == "A":
            self.pet_list_window.handle_input(input_action)
            self.versus_ready = len(self.pet_list_window.selected_indices) == 2
        elif input_action == "B":
            # Cancel Jogress selection
            self.pet_list_window.selected_indices.clear()
            self.phase = "menu"
            self.pet_list_window.select_mode = False
            runtime_globals.game_sound.play("cancel")
        elif input_action == "START":
            if self.versus_ready:
                # Transition to Versus battle mode here
                selected = [game_globals.pet_list[i] for i in self.pet_list_window.selected_indices]
                self.mode = BattleEncounterVersus(selected[0],selected[1])  # or your actual Versus class
                selected[0].check_disturbed_sleep()
                selected[1].check_disturbed_sleep()
                self.phase = "next"
                runtime_globals.game_console.log("Starting Versus Battle.")
            else:
                runtime_globals.game_sound.play("fail")

    def check_jogress_compatibility(self, selected_indices):
        if len(selected_indices) != 2:
            return False

        pet1 = game_globals.pet_list[selected_indices[0]]
        pet2 = game_globals.pet_list[selected_indices[1]]

        # Must belong to the same module
        if pet1.module != pet2.module:
            return False

        # Pet1 must have jogress options
        for evo in pet1.evolve:
            if "jogress" not in evo:
                continue

            # 🔸 Standard jogress
            if evo["jogress"] != "PenC":
                if pet2.name == evo["jogress"] and pet2.version == evo.get("version", pet1.version):
                    return True

            # 🔸 PenC jogress (based on attribute + stage)
            elif evo["jogress"] == "PenC":
                if (
                    pet2.attribute == evo.get("attribute") and
                    pet2.stage == evo.get("stage")
                ):
                    return True

        return False

    def perform_jogress(self):
        selected = self.pet_list_window.selected_indices
        if len(selected) != 2:
            return

        pet1 = game_globals.pet_list[selected[0]]
        pet2 = game_globals.pet_list[selected[1]]

        if pet1.module != pet2.module:
            return

        for evo in pet1.evolve:
            if "jogress" not in evo:
                continue

            if evo["jogress"] != "PenC":
                if pet2.name == evo["jogress"] and pet2.version == evo.get("version", pet1.version):
                    pet1.evolve_to(evo["to"], pet1.version)
                    pet2.evolve_to(evo["to"], pet2.version)
                    if pet2.traited:
                        pet1.trated = True
                    if pet2.shiny:
                        pet1.shiny = True
                    if pet2.shook:
                        pet1.shook = True
                    game_globals.pet_list.remove(pet2)
                    runtime_globals.game_sound.play("evolution")
                    runtime_globals.game_console.log(f"[Jogress] {pet1.name} jogressed to {evo['to']}!")
                    change_scene("game")
                    return

            elif evo["jogress"] == "PenC":
                if pet2.attribute == evo.get("attribute") and pet2.stage == evo.get("stage"):
                    evo2 = next((e for e in pet2.evolve if e.get("jogress") == "PenC" and e.get("attribute") == pet1.attribute), None)

                    if evo2:
                        pet1.evolve_to(evo["to"], pet1.version)  # pet1 evolves to pet2's attribute evolution
                        pet2.evolve_to(evo2["to"], pet2.version)  # pet2 evolves to pet1's attribute evolution

                    runtime_globals.game_sound.play("evolution")
                    runtime_globals.game_console.log(f"[Jogress] {pet1.name} jogressed to {evo['to']}!")
                    change_scene("game")
                    return

        runtime_globals.game_console.log("[Jogress] Invalid combination.")
        runtime_globals.game_sound.play("fail")