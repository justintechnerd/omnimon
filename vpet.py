"""
Virtual Pet - Main Program
Entry point for the Virtual Pet game.
Handles game initialization, main loop, and scene transitions.
"""

import platform
import pygame

# Scenes
from core import game_globals, runtime_globals
from core.constants import *
from core.utils import load_modules
from scenes.scene_battle import SceneBattle
from scenes.scene_boot import SceneBoot
from scenes.scene_digidex import SceneDigidex
from scenes.scene_eggselection import SceneEggSelection
from scenes.scene_evolution import SceneEvolution
from scenes.scene_freezerbox import SceneFreezerBox
from scenes.scene_settingsmenu import SceneSettingsMenu
from scenes.scene_sleepmenu import SceneSleepMenu
from scenes.scene_statusmenu import SceneStatusMenu
from scenes.scene_maingame import SceneMainGame
from scenes.scene_feedingmenu import SceneFeedingMenu
from scenes.scene_training import SceneTraining

# Game Version
runtime_globals.VERSION = "0.9.2"

# Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)

# Set up display
device_name = platform.node()  # Gets the hostname

# Adjust fullscreen setting based on hostname
if device_name == "omnimon":  # Replace with your Raspberry Pi’s hostname
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SRCALPHA)
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Windowed on other devices

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=128)
pygame.display.set_caption(f"Omnimon {runtime_globals.VERSION}")


class VirtualPetGame:
    """
    Main Virtual Pet Game class.
    Handles scene management, updating, drawing, and event handling.
    """

    def __init__(self) -> None:
        runtime_globals.load_misc_sprites()
        load_modules()
        game_globals.load()
        self.scene = SceneBoot()
        runtime_globals.game_console.log("[Init] Omnibot initialized with SceneBoot")
        self.rotated = False
        self.clock = pygame.time.Clock()

    def update(self) -> None:
        """
        Updates the current scene and handles scene transitions if needed.
        """
        self.scene.update()
        self.poll_gpio_inputs()

        if runtime_globals.game_state_update:
            self.change_scene()

        if game_globals.rotated:
            game_globals.rotated = False
            self.rotated = not self.rotated

        if runtime_globals.shake_detector.check_for_shake():
            self.scene.handle_event("SHAKE")

        self.clock.tick(FRAME_RATE)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the current scene to the given surface.
        """
        self.scene.draw(surface)
        draw_fps(self.clock, screen)
        if self.rotated:
            rotated_surface = pygame.transform.rotate(screen, 180)
            screen.blit(rotated_surface, (0, 0))
            pygame.display.flip()

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Delegates event handling to the current scene.
        """
        input_action = runtime_globals.game_input.process_event(event)
        #if input_action:
        #    print(input_action)
            
        self.scene.handle_event(input_action)

    def poll_gpio_inputs(self):
        for action in runtime_globals.game_input.get_just_pressed():
            self.scene.handle_event(action)

    def change_scene(self) -> None:
        """
        Handles changing the current scene based on  runtime_globals.game_state.
        """
        runtime_globals.game_state_update = False
        state =  runtime_globals.game_state

        scene_mapping = {
            "egg": SceneEggSelection,
            "game": SceneMainGame,
            "settings": SceneSettingsMenu,
            "status": SceneStatusMenu,
            "feeding": SceneFeedingMenu,
            "training": SceneTraining,
            "sleepmenu": SceneSleepMenu,
            "battle": SceneBattle,
            "digidex": SceneDigidex,
            "evolution": SceneEvolution,
            "freezer": SceneFreezerBox,
        }

        scene_class = scene_mapping.get(state)
        if scene_class:
            runtime_globals.game_console.log(f"[Scene] Switching to {scene_class.__name__}")
            self.scene = scene_class()
        else:
            runtime_globals.game_console.log(f"[Error] Unknown game_state: {state}")

def main() -> None:
    """
    Main loop of the Virtual Pet game.
    """
    game = VirtualPetGame()
    running = True

    while running:
        #screen.fill((198, 203, 173))  # Base background color
        game.update()
        game.draw(screen)
        pygame.display.flip()

        game_globals.autosave()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_globals.save()
                running = False
            else:
                game.handle_event(event)

    pygame.quit()

def draw_fps(clock, surface):
    if game_globals.debug:
        fps = clock.get_fps()
        font = pygame.font.Font(None, 16)
        fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        surface.blit(fps_text, (4, SCREEN_HEIGHT - 16))

if __name__ == "__main__":
    main()
