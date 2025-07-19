"""
Virtual Pet - Main Program
Entry point for the Virtual Pet game.
Handles game initialization, main loop, and scene transitions.
"""

import platform
import pygame
import time
import cProfile
import pstats

# Scenes
from core import game_globals, runtime_globals
from core.constants import *
from core.input.system_stats import get_system_stats
from core.utils.module_utils import load_modules
from core.utils.pygame_utils import blit_with_cache, load_misc_sprites
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

# Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)

# Set up display
device_name = platform.node()  # Gets the hostname
screen_mode = (pygame.FULLSCREEN | pygame.DOUBLEBUF) | (pygame.SRCALPHA | pygame.DOUBLEBUF) if device_name == "omnimon" else 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_mode, 16)

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=128)
pygame.display.set_caption(f"Omnimon {runtime_globals.VERSION}")

pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
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

        # Only draw debug stats if explicitly enabled
        if game_globals.debug:
            now = time.time()
            if now - last_stats_update >= 3:  # Update stats every 3 seconds
                cached_stats = get_system_stats()
                last_stats_update = now
            draw_system_stats(self.clock, surface, cached_stats, self.stat_font)  # Use surface instead of screen

        if self.rotated:
            rotated_surface = pygame.transform.rotate(surface, 180)  # Rotate only the surface
            surface.blit(rotated_surface, (0, 0))

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
    #profiler = cProfile.Profile()
    #profiler.enable()  # Start profiling

    game = VirtualPetGame()
    running = True

    while running:
        game.update()
        game.draw(screen)
        pygame.display.flip()  # Use flip() instead of update() for better performance

        game_globals.autosave()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_globals.save()
                running = False
            else:
                game.handle_event(event)

        game.clock.tick(FRAME_RATE)  # Use optimized frame rate

    #profiler.disable()  # Stop profiling

    # Save profiling data in .prof format for SnakeViz
    #profiler.dump_stats("profile_stats.prof")

    # Analyze profiling data for all calls
    #print("Profiling results:")
    #stats = pstats.Stats(profiler)
    #stats.strip_dirs()
    #stats.sort_stats("cumulative")
    #stats.print_stats()  # Print all profiling results

    pygame.quit()


cached_stats_surface = None
last_stats_values = None

def draw_system_stats(clock, surface, stats, font):
    """Efficiently draws FPS, CPU temp, memory, and CPU usage."""
    global cached_stats_surface, last_stats_values

    if not game_globals.debug:
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

if __name__ == "__main__":
    main()