"""
Virtual Pet - Game Logic
Handles the Virtual Pet game logic, scene management, and game state.
Display and audio initialization is handled by main.py
"""

import pygame
import time

# Scenes
from core import game_globals, runtime_globals
from core.input.system_stats import get_system_stats
from core.utils.module_utils import load_modules
from core.utils.pygame_utils import blit_with_cache, load_misc_sprites
from game.core import constants
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
runtime_globals.VERSION = "0.9.6"

# Global timing variable for system stats updates
last_stats_update = time.time()
cached_stats = get_system_stats()  # Initialize with actual values


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
        print("[Init] Omnibot initialized with SceneBoot")
        self.rotated = False
        self.stat_font = pygame.font.Font(None, 16)
        # Clock is now managed by main.py

    def update(self) -> None:
        """
        Updates the current scene and handles scene transitions if needed.
        """
        self.scene.update()

        # Poll GPIO actions
        self.poll_gpio_inputs()

        # Poll joystick actions (including analog stick directions)
        #for action in runtime_globals.game_input.get_just_pressed_joystick():
        #    self.scene.handle_event(action)

        if runtime_globals.game_state_update:
            self.change_scene()

        if game_globals.rotated:
            game_globals.rotated = False
            self.rotated = not self.rotated

        if runtime_globals.shake_detector.check_for_shake():
            self.scene.handle_event("SHAKE")
            
        # Handle autosave
        game_globals.autosave()

    def draw(self, surface: pygame.Surface, clock: pygame.time.Clock = None) -> None:
        """
        Draws the current scene to the given surface.
        """
        self.scene.draw(surface)

        global last_stats_update, cached_stats

        # Only draw debug stats if explicitly enabled and clock is provided
        if constants.DEBUG and clock is not None:
            now = time.time()
            if now - last_stats_update >= 3:  # Update stats every 3 seconds
                cached_stats = get_system_stats()
                last_stats_update = now
            #draw_system_stats(clock, surface, cached_stats, self.stat_font)

        if self.rotated:
            rotated_surface = pygame.transform.rotate(surface, 180)  # Rotate only the surface
            surface.blit(rotated_surface, (0, 0))

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Delegates event handling to the current scene.
        """
        input_action = runtime_globals.game_input.process_event(event)
        if input_action:
            self.scene.handle_event(input_action)
        else: #Analog inputs
            for action in runtime_globals.game_input.get_just_pressed_joystick():
                if action in ("ANALOG_UP", "ANALOG_DOWN", "ANALOG_LEFT", "ANALOG_RIGHT"):
                    self.scene.handle_event(action.replace("ANALOG_", ""))

    def poll_gpio_inputs(self):
        for action in runtime_globals.game_input.get_gpio_just_pressed():
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
            print(f"[Scene] Switching to {scene_class.__name__}")
            self.scene = scene_class()

    def save(self) -> None:
        """
        Saves the current game state.
        """
        game_globals.save()
        runtime_globals.game_console.log("[VirtualPetGame] Game state saved.")


def main() -> None:
    """
    Main loop of the Virtual Pet game.
    This function is now handled by main.py
    """
    pass


cached_stats_surface = None
last_stats_values = None

def draw_system_stats(clock, surface, stats, font):
    """Efficiently draws FPS, CPU temp, memory, and CPU usage."""
    global cached_stats_surface, last_stats_values

    if not constants.DEBUG:
        return

    temp, cpu_usage, memory_usage = stats
    fps = int(clock.get_fps())
    stats_tuple = (fps, temp, cpu_usage, memory_usage)

    # Only update cached surface if stats changed
    if cached_stats_surface is None or stats_tuple != last_stats_values:
        cached_stats_surface = pygame.Surface((140, 60), pygame.SRCALPHA)
        y = 0
        cached_stats_surface.blit(font.render(f"FPS: {fps}", True, (255, 255, 255)), (0, y))
        y += 16
        if temp is not None:
            cached_stats_surface.blit(font.render(f"Temp: {temp:.1f}°C", True, (255, 255, 255)), (0, y))
            y += 16
        if cpu_usage is not None:
            cached_stats_surface.blit(font.render(f"CPU: {cpu_usage:.1f}%", True, (255, 255, 255)), (0, y))
            y += 16
        if memory_usage is not None:
            cached_stats_surface.blit(font.render(f"RAM: {memory_usage:.1f}%", True, (255, 255, 255)), (0, y))
        last_stats_values = stats_tuple

    # Blit the cached stats surface
    blit_with_cache(surface, cached_stats_surface, (4, 64))