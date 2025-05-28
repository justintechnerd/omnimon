import pygame
from core import runtime_globals
from core.constants import *
from core.utils import get_font


class WindowMenu:
    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.options = []
        self.menu_index = 0
        self.active = False
        self.position = (0, 0)

    def open(self, position, options):
        self.active = True
        self.menu_index = 0
        self.position = position
        self.options = options

    def close(self):
        self.active = False

    def handle_event(self, input_action):
        if input_action == "UP":
            runtime_globals.game_sound.play("menu")
            self.menu_index = (self.menu_index - 1) % len(self.options)
        elif input_action == "DOWN":
            runtime_globals.game_sound.play("menu")
            self.menu_index = (self.menu_index + 1) % len(self.options)

    def draw(self, surface):
        if not self.active:
            return
        x, y = self.position
        menu_height = 30 + len(self.options) * 25
        menu_surface = pygame.Surface((100, menu_height))
        menu_surface.set_alpha(180)
        menu_surface.fill((0, 0, 0))
        surface.blit(menu_surface, (x, y))
        for i, option in enumerate(self.options):
            color = FONT_COLOR_GREEN if i == self.menu_index else FONT_COLOR_DEFAULT
            text_surface = self.font.render(option, True, color)
            surface.blit(text_surface, (x + 10, y + 10 + i * 25))