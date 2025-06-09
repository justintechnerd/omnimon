import pygame
from core.constants import *
from core.utils import blit_with_shadow, get_font


class WindowHorizontalMenu:
    def __init__(self, options, get_selected_index_callback):
        """
        options: List of (label, icon_surface)
        get_selected_index_callback: Function returning the current selected index
        """
        self.options = options
        self.get_index = get_selected_index_callback

        # Pre-scale icons
        self.scaled_options = {
            "normal": [(label, pygame.transform.smoothscale(icon, (OPTION_ICON_SIZE, OPTION_ICON_SIZE)))
                       for label, icon in options],
            "small": [(label, pygame.transform.smoothscale(icon, (
                int(OPTION_ICON_SIZE * 0.75), int(OPTION_ICON_SIZE * 0.75))))
                      for label, icon in options]
        }

        # Pre-scale frames
        self.selection_on = pygame.image.load(SELECTION_ON_PATH).convert_alpha()
        self.selection_off = pygame.image.load(SELECTION_OFF_PATH).convert_alpha()

        self.selection_on_small = pygame.transform.smoothscale(
            self.selection_on, (int(OPTION_FRAME_WIDTH * 0.75), int(OPTION_FRAME_HEIGHT * 0.75)))
        self.selection_off_small = pygame.transform.smoothscale(
            self.selection_off, (int(OPTION_FRAME_WIDTH * 0.75), int(OPTION_FRAME_HEIGHT * 0.75)))

        # Fonts
        self.font_large = get_font(FONT_SIZE_SMALL)
        self.font_small = get_font(int(FONT_SIZE_SMALL * 0.75))

    def draw(self, surface: pygame.Surface, x: int, y: int, spacing: int = 16):
        selected_index = self.get_index()
        total = len(self.options)

        if total == 1:
            label, icon = self.scaled_options["normal"][0]
            center_x = SCREEN_WIDTH // 2 - OPTION_FRAME_WIDTH // 2
            self.draw_option(surface, center_x, y, label, icon, selected=True, large=True)

        elif total == 2:
            for i, (label, icon) in enumerate(self.scaled_options["normal"]):
                offset_x = x + i * (OPTION_FRAME_WIDTH + spacing)
                self.draw_option(surface, offset_x, y, label, icon, selected=(i == selected_index), large=True)

        elif total > 2:
            prev_index = (selected_index - 1) % total
            next_index = (selected_index + 1) % total

            # Draw previous (left) option - small
            prev_label, prev_icon = self.scaled_options["small"][prev_index]
            self.draw_option(surface, x - OPTION_FRAME_WIDTH * 0.8, y + 10, prev_label, prev_icon, selected=False, large=False)

            # Draw next (right) option - small
            next_label, next_icon = self.scaled_options["small"][next_index]
            self.draw_option(surface, x + OPTION_FRAME_WIDTH + 10, y + 10, next_label, next_icon, selected=False, large=False)

            # Draw current (center) option - large
            center_label, center_icon = self.scaled_options["normal"][selected_index]
            self.draw_option(surface, x, y, center_label, center_icon, selected=True, large=True)

    def draw_option(self, surface, x, y, label, icon, selected, large=True):
        frame = (
            self.selection_on if selected else self.selection_off
        ) if large else (
            self.selection_on_small if selected else self.selection_off_small
        )

        font = self.font_large if large else self.font_small

        # Draw frame
        blit_with_shadow(surface, frame, (x, y))

        # Draw icon centered in frame
        icon_x = x + (frame.get_width() - icon.get_width()) // 2
        icon_y = y + 20
        blit_with_shadow(surface, icon, (icon_x, icon_y))

        # Draw label centered under icon
        text_surface = font.render(label, True, FONT_COLOR_DEFAULT)
        text_x = x + (frame.get_width() - text_surface.get_width()) // 2
        text_y = icon_y + icon.get_height() + 6
        blit_with_shadow(surface, text_surface, (text_x, text_y))
