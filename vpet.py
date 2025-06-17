"""
Virtual Pet - Main Program
Entry point for the Virtual Pet game.
Handles game initialization, main loop, and scene transitions.
"""

import platform
import pygame
import time

# Scenes
from core import game_globals, runtime_globals
from core.constants import *
from core.utils.module_utils import load_modules
from core.utils.pygame_utils import load_misc_sprites
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
runtime_globals.VERSION = "0.9.4"

# Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)

# Set up display
device_name = platform.node()  # Gets the hostname
screen_mode = pygame.FULLSCREEN | pygame.SRCALPHA if device_name == "omnimon" else 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_mode)

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=128)
pygame.display.set_caption(f"Omnimon {runtime_globals.VERSION}")

# Global timing variable for system stats updates
last_stats_update = time.time()
cached_stats = (None, None, None)  # Stores (temp, cpu_usage, memory_usage)


class VirtualPetGame:
    """
    Main Virtual Pet Game class.
    Handles scene management, updating, drawing, and event handling.
    """

    def __init__(self) -> None:
        runtime_globals.misc_sprites = load_misc_sprites()
        load_modules()
        game_globals.load()
        self.scene = SceneBoot()
        runtime_globals.game_console.log("[Init] Omnibot initialized with SceneBoot")
        self.rotated = False
        self.stat_font = pygame.font.Font(None, 16)
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

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the current scene to the given surface.
        """
        self.scene.draw(surface)

        global last_stats_update, cached_stats
        #now = time.time()
        #if now - last_stats_update >= 3:  # Update stats every 3 seconds
        #    cached_stats = get_system_stats()
        #    last_stats_update = now

        draw_system_stats(self.clock, screen, cached_stats, self.stat_font)

        if self.rotated:
            rotated_surface = pygame.transform.rotate(screen, 180)
            screen.blit(rotated_surface, (0, 0))
            pygame.display.update()

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Delegates event handling to the current scene.
        """
        input_action = runtime_globals.game_input.process_event(event)
        self.scene.handle_event(input_action)

    def poll_gpio_inputs(self):
        for action in runtime_globals.game_input.get_just_pressed():
            self.scene.handle_event(action)

    def change_scene(self) -> None:
        """
        Handles changing the current scene based on runtime_globals.game_state.
        """
        runtime_globals.game_state_update = False
        state = runtime_globals.game_state

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
        if scene_class and type(self.scene) is not scene_class:  # Prevent redundant scene switches
            runtime_globals.game_console.log(f"[Scene] Switching to {scene_class.__name__}")
            self.scene = scene_class()


def main() -> None:
    """
    Main loop of the Virtual Pet game.
    """
    game = VirtualPetGame()
    running = True

    while running:
        game.update()
        game.draw(screen)
        pygame.display.update()

        game_globals.autosave()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_globals.save()
                running = False
            else:
                game.handle_event(event)
        
        game.clock.tick(FRAME_RATE)  # limit frame rate here

    pygame.quit()


cached_texts = {}
last_stat_values = {}

def get_cached_stat_text(key, value, font):
    """Returns cached text surface if value is unchanged, otherwise updates it."""
    if key not in last_stat_values or last_stat_values[key] != value:
        cached_texts[key] = font.render(value, True, (255, 255, 255))
        last_stat_values[key] = value
    return cached_texts[key]

def draw_system_stats(clock, surface, stats, font):
    """Efficiently draws FPS, CPU temp, memory, and CPU usage."""
    if not game_globals.debug:
        return

    temp, cpu_usage, memory_usage = stats
    fps = int(clock.get_fps())

    # 🚀 Retrieve or update cached text surfaces
    surface.blit(get_cached_stat_text("fps", f"FPS: {fps}", font), (4, 64))

    if temp is not None:
        surface.blit(get_cached_stat_text("temp", f"Temp: {temp:.1f}°C", font), (4, 80))

    if cpu_usage is not None:
        surface.blit(get_cached_stat_text("cpu", f"CPU: {cpu_usage:.1f}%", font), (4, 96))

    if memory_usage is not None:
        surface.blit(get_cached_stat_text("ram", f"RAM: {memory_usage:.1f}%", font), (4, 112))



if __name__ == "__main__":
    main()