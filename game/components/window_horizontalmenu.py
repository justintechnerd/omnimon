import pygame
import game.core.constants as constants
from core.utils.pygame_utils import blit_with_cache, blit_with_shadow, get_font, sprite_load_percent


class WindowHorizontalMenu:
    def __init__(self, options, get_selected_index_callback):
        """
        options: List of (label, icon_surface or icon_path, [optional] amount)
        get_selected_index_callback: Function returning the current selected index
        """
        self.options = options
        self.get_index = get_selected_index_callback

        # Precompute and cache scaled icons and frames
        self._cache_surfaces()

        # Fonts
        self.font_large = get_font(constants.FONT_SIZE_SMALL)
        self.font_small = get_font(int(constants.FONT_SIZE_SMALL * 0.75))

        # Cache for draw layout
        self._last_screen_size = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self._layout_cache = {}
        self._last_selected_index = None  # Cache for selected index
        self._sprite_cache = {}  # Cache for pre-rendered sprites

    def _cache_surfaces(self):
        # Pre-scale icons using the new method
        self.scaled_options = {
            "normal": [
                (label, sprite_load_percent(icon if isinstance(icon, str) else None,
                                            percent=(constants.OPTION_ICON_SIZE / constants.SCREEN_HEIGHT) * 100,
                                            keep_proportion=True,
                                            base_on="height") if isinstance(icon, str)
                 else pygame.transform.smoothscale(icon, (constants.OPTION_ICON_SIZE, constants.OPTION_ICON_SIZE)),
                 amount if len(opt) > 2 else None)
                for opt in self.options
                for label, icon, *amount in [opt]
            ],
            "small": [
                (label, sprite_load_percent(icon if isinstance(icon, str) else None,
                                            percent=(int(constants.OPTION_ICON_SIZE * 0.75) / constants.SCREEN_HEIGHT) * 100,
                                            keep_proportion=True,
                                            base_on="height") if isinstance(icon, str)
                 else pygame.transform.smoothscale(icon, (int(constants.OPTION_ICON_SIZE * 0.75), int(constants.OPTION_ICON_SIZE * 0.75))),
                 amount if len(opt) > 2 else None)
                for opt in self.options
                for label, icon, *amount in [opt]
            ]
        }

        # Pre-scale frames using the new method
        self.selection_on = sprite_load_percent(constants.SELECTION_ON_PATH, percent=(constants.OPTION_FRAME_HEIGHT / constants.SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")
        self.selection_off = sprite_load_percent(constants.SELECTION_OFF_PATH, percent=(constants.OPTION_FRAME_HEIGHT / constants.SCREEN_HEIGHT) * 100, keep_proportion=True, base_on="height")

        self.selection_on_small = pygame.transform.smoothscale(
            self.selection_on, (int(constants.OPTION_FRAME_WIDTH * 0.75), int(constants.OPTION_FRAME_HEIGHT * 0.75)))
        self.selection_off_small = pygame.transform.smoothscale(
            self.selection_off, (int(constants.OPTION_FRAME_WIDTH * 0.75), int(constants.OPTION_FRAME_HEIGHT * 0.75)))

    def _precompute_layout(self, y, spacing):
        # Only recompute if screen size or option count changes
        cache_key = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, len(self.options), y, spacing, self.get_index())
        if self._layout_cache.get("key") == cache_key:
            return self._layout_cache["layout"]

        layout = []
        total = len(self.options)
        if total == 1:
            center_x = constants.SCREEN_WIDTH // 2 - constants.OPTION_FRAME_WIDTH // 2
            layout.append(("normal", 0, center_x, y, True))
        elif total == 2:
            total_width = constants.OPTION_FRAME_WIDTH * 2 + spacing
            left_margin = (constants.SCREEN_WIDTH - total_width) // 2
            for i in range(total):
                offset_x = left_margin + i * (constants.OPTION_FRAME_WIDTH + spacing)
                layout.append(("normal", i, offset_x, y, i == self.get_index()))
        elif total > 2:
            center_x = constants.SCREEN_WIDTH // 2 - constants.OPTION_FRAME_WIDTH // 2
            selected_index = self.get_index()
            prev_index = (selected_index - 1) % total
            next_index = (selected_index + 1) % total

            # Previous (left) option
            prev_x = center_x - spacing - (self.selection_on.get_width() // 2) + (7 * constants.UI_SCALE)
            layout.append(("small", prev_index, prev_x, y + int(10 * constants.UI_SCALE), False))

            # Next (right) option
            next_x = center_x + constants.OPTION_FRAME_WIDTH - (2 * constants.UI_SCALE)
            layout.append(("small", next_index, next_x, y + int(10 * constants.UI_SCALE), False))

            # Current (center) option
            layout.append(("normal", selected_index, center_x, y, True))

        self._layout_cache["key"] = cache_key
        self._layout_cache["layout"] = layout
        return layout

    def _cache_draw_sprites(self, layout):
        """
        Pre-render sprites for the current layout to minimize per-frame rendering.
        """
        self._sprite_cache = {}
        for size, idx, draw_x, draw_y, selected in layout:
            label, icon, amount = self.scaled_options[size][idx]
            frame = (
                self.selection_on if selected else self.selection_off
            ) if size == "normal" else (
                self.selection_on_small if selected else self.selection_off_small
            )
            font = self.font_large if size == "normal" else self.font_small

            # Render frame and icon
            frame_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            blit_with_shadow(frame_surface, frame, (0, 0))
            icon_x = (frame.get_width() - icon.get_width()) // 2
            icon_y = int(20 * constants.UI_SCALE)
            blit_with_shadow(frame_surface, icon, (icon_x, icon_y))

            # Render label
            text_surface = font.render(label, True, constants.FONT_COLOR_DEFAULT)
            text_x = (frame.get_width() - text_surface.get_width()) // 2
            text_y = icon_y + icon.get_height() + int(6 * constants.UI_SCALE)
            blit_with_shadow(frame_surface, text_surface, (text_x, text_y))

            # Render amount if present
            if amount is not None:
                if isinstance(amount, (list, tuple)):
                    amount_value = amount[0]  # Extract first value if iterable
                else:
                    amount_value = amount

                if amount_value > 0:  # Perform comparison only on valid numeric values
                    amount_font = self.font_small if size == "normal" else get_font(int(constants.FONT_SIZE_SMALL * 0.6))
                    amount_surface = amount_font.render(f"x{amount_value}", True, constants.FONT_COLOR_GREEN)
                    amount_x = frame.get_width() - amount_surface.get_width() - int(8 * constants.UI_SCALE)
                    amount_y = int(8 * constants.UI_SCALE)
                    blit_with_shadow(frame_surface, amount_surface, (amount_x, amount_y))

            self._sprite_cache[idx] = (frame_surface, draw_x, draw_y)

    def draw(self, surface: pygame.Surface, x: int, y: int, spacing: int = 16):
        selected_index = self.get_index()
        if self._last_selected_index != selected_index:
            layout = self._precompute_layout(y, spacing)
            self._cache_draw_sprites(layout)
            self._last_selected_index = selected_index

        for idx, (sprite, draw_x, draw_y) in self._sprite_cache.items():
            #surface.blit(sprite, (draw_x, draw_y))
            blit_with_cache(surface, sprite, (draw_x, draw_y))

    def draw_option(self, surface, x, y, label, icon, selected, large=True, amount=None):
        frame = (
            self.selection_on if selected else self.selection_off
        ) if large else (
            self.selection_on_small if selected else self.selection_off_small
        )

        font = self.font_large if large else self.font_small

        # Draw frame
        blit_with_shadow(surface, frame, (int(x), int(y)))

        # Draw icon centered in frame
        icon_x = int(x) + (frame.get_width() - icon.get_width()) // 2
        icon_y = int(y) + int(20 * constants.UI_SCALE)
        blit_with_shadow(surface, icon, (icon_x, icon_y))

        # Draw label centered under icon
        text_surface = font.render(label, True, constants.FONT_COLOR_DEFAULT)
        text_x = int(x) + (frame.get_width() - text_surface.get_width()) // 2
        text_y = icon_y + icon.get_height() + int(6 * constants.UI_SCALE)
        blit_with_shadow(surface, text_surface, (text_x, text_y))

        # Draw amount if present and valid
        if amount is not ModuleNotFoundError:
            if isinstance(amount, (list, tuple)):
                amount_value = amount[0]
            else:
                amount_value = amount

            if amount_value is None or amount_value <= 0:
                return

            amount_font = self.font_small if large else get_font(int(constants.FONT_SIZE_SMALL * 0.6))
            amount_surface = amount_font.render(f"x{amount_value}", True, constants.FONT_COLOR_GREEN)
            amount_x = int(x) + frame.get_width() - amount_surface.get_width() - int(8 * constants.UI_SCALE)
            amount_y = int(y) + int(8 * constants.UI_SCALE)
            blit_with_shadow(surface, amount_surface, (amount_x, amount_y))

    def set_option_label(self, index, new_label):
        """
        Dynamically update the label for an option at the given index.
        """
        for size in self.scaled_options:
            icon = self.scaled_options[size][index][1]
            amount = self.scaled_options[size][index][2] if len(self.scaled_options[size][index]) > 2 else None
            self.scaled_options[size][index] = (new_label, icon, amount)
        self.options[index] = (new_label, self.options[index][1]) if len(self.options[index]) == 2 else (new_label, self.options[index][1], self.options[index][2])
        # Invalidate layout and sprite cache to force redraw
        self._layout_cache.clear()
        self._sprite_cache.clear()
        self._last_selected_index = None  # <-- Add this line
