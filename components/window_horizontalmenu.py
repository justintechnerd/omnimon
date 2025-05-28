import pygame

from core.constants import *
from core.utils import blit_with_shadow, get_font

class WindowHorizontalMenu:
    def __init__(self, options, get_selected_index_callback):
        self.options = options  # list of (label, icon_surface)
        self.get_index = get_selected_index_callback
        
        # Pre-scale options (normal & small versions)
        self.scaled_options = {
            "normal": [(label, pygame.transform.scale(icon, (OPTION_ICON_SIZE, OPTION_ICON_SIZE)))
                       for label, icon in options],
            "small": [(label, pygame.transform.scale(icon, (int(OPTION_ICON_SIZE * 0.75), int(OPTION_ICON_SIZE * 0.75))))
                      for label, icon in options]
        }

        # Pre-scale frames
        self.selection_off = pygame.image.load(SELECTION_OFF_PATH).convert_alpha()
        self.selection_on = pygame.image.load(SELECTION_ON_PATH).convert_alpha()
        self.selection_off_small = pygame.transform.scale(self.selection_off, (int(OPTION_FRAME_WIDTH * 0.75), int(OPTION_FRAME_HEIGHT * 0.75)))
        self.selection_on_small = pygame.transform.scale(self.selection_on, (int(OPTION_FRAME_WIDTH * 0.75), int(OPTION_FRAME_HEIGHT * 0.75)))

        # Font adjustments
        self.font_large = get_font(FONT_SIZE_SMALL)
        self.font_small = get_font(int(FONT_SIZE_SMALL * 0.75))  # Smaller font for side options

    def draw(self, surface: pygame.Surface, x: int, y: int, spacing: int = 16):
        selected_index = self.get_index()
        total = len(self.options)

        if total == 1:
            label, icon = self.scaled_options["normal"][0]
            center_x = SCREEN_WIDTH // 2 - OPTION_FRAME_WIDTH // 2  # Centered on the screen
            self.draw_option(surface, center_x, y, label, icon, True, large=True)

        elif total == 2:
            # Show both options side by side
            for i, (label, icon) in enumerate(self.scaled_options["normal"]):
                x_offset = i * (OPTION_FRAME_WIDTH + spacing)
                selected = (i == selected_index)
                self.draw_option(surface, x + x_offset, y, label, icon, selected, large=True)
        else:
            prev_index = (selected_index - 1) % total
            next_index = (selected_index + 1) % total

            # Left (previous) item - smaller size, adjusted placement
            label, icon = self.scaled_options["small"][prev_index]
            self.draw_option(surface, x - (OPTION_FRAME_WIDTH * 0.75), y + 10, label, icon, False, large=False)

            # Right (next) item - smaller size, adjusted placement
            label, icon = self.scaled_options["small"][next_index]
            self.draw_option(surface, x + OPTION_FRAME_WIDTH - 2, y + 10, label, icon, False, large=False)

            # Center (selected) item - Draw last to keep it on top
            label, icon = self.scaled_options["normal"][selected_index]
            self.draw_option(surface, x, y, label, icon, True, large=True)

    def draw_option(self, surface, x, y, label, icon, selected, large=True):
        frame = self.selection_on if selected else self.selection_off
        font = self.font_large if large else self.font_small

        if not large:
            frame = self.selection_on_small if selected else self.selection_off_small
        
        blit_with_shadow(surface, frame, (x, y))

        icon_x = x + (frame.get_width() - icon.get_width()) // 2
        icon_y = y + 20
        blit_with_shadow(surface, icon, (icon_x, icon_y))

        text_surface = font.render(label, True, FONT_COLOR_DEFAULT)
        text_x = x + (frame.get_width() - text_surface.get_width()) // 2
        text_y = icon_y + icon.get_height() + 10
        blit_with_shadow(surface, text_surface, (text_x, text_y))
