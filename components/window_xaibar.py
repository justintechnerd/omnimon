import pygame
from .window_xai import WindowXai
import random
from core.utils import blit_with_shadow

XAIARROW_ICON_PATH = "resources/XaiArrow.png"  # Update this path as needed

class WindowXaiBar:
    WIDTH = 152   # 132 + 20 for extra width
    HEIGHT = 72   # 68 + 4 for border (doubled)
    INNER_WIDTH = 148  # 128 + 20 for extra width
    INNER_HEIGHT = 68

    def __init__(self, x, y, xai_number, pet):
        self.x = x
        self.y = y
        self.xai_number = xai_number
        self.pet = pet
        # Load and scale arrow sprite once
        arrow_img = pygame.image.load(XAIARROW_ICON_PATH).convert_alpha()
        self.arrow_height = 32  # quadruple the original 8px (was doubled, now doubled again)
        self.arrow_width = arrow_img.get_width() * 4
        self.arrow_sprite = pygame.transform.scale(arrow_img, (self.arrow_width, self.arrow_height))
        self.arrow_animating = False
        self.arrow_anim_dir = 1  # 1 = right, -1 = left
        self.arrow_anim_x = 0
        # Arrow should move so its midpoint covers the entire inner region
        self.arrow_anim_min = self.x + 2 - self.arrow_width // 2
        self.arrow_anim_max = self.x + 2 + self.INNER_WIDTH - self.arrow_width // 2
        self.selected_strength = None
        self.structures = self.get_bar_structures()

    def start(self):
        self.arrow_animating = True
        self.arrow_anim_dir = 1
        self.arrow_anim_x = self.arrow_anim_min
        self.selected_strength = None

    def stop(self):
        self.arrow_animating = False
        self.selected_strength = self._get_strength_from_arrow()

    def update(self):
        if self.arrow_animating:
            # Speed: 1 (fastest) to 7 (slowest)
            speed = max(1, 8 - self.xai_number)
            self.arrow_anim_x += self.arrow_anim_dir * speed
            if self.arrow_anim_x <= self.arrow_anim_min:
                self.arrow_anim_x = self.arrow_anim_min
                self.arrow_anim_dir = 1
            elif self.arrow_anim_x >= self.arrow_anim_max:
                self.arrow_anim_x = self.arrow_anim_max
                self.arrow_anim_dir = -1

    def get_bar_structures(self):
        """
        Returns a list of (rect, value) tuples for the current pet,
        where value is 1 for red, 2 for orange, 3 for yellow.
        """
        yellow_width, orange_width, orange_height, red_width, red_height = self.getBars()
        name_seed = sum(ord(c) for c in self.pet.name)
        base_y = self.y + 2
        bar_left = self.x + 2
        bar_right = self.x + 2 + self.INNER_WIDTH

        rects = []

        if self.pet.stage < 5:
            total_width = red_width + orange_width + yellow_width + orange_width + red_width
            max_x = bar_right - total_width
            min_x = bar_left
            offset = (name_seed % (max_x - min_x + 1)) if (max_x - min_x) > 0 else 0
            group_x = min_x + offset

            # Rects: red, orange, yellow, orange, red
            red_left_rect = pygame.Rect(group_x, base_y + self.INNER_HEIGHT - red_height, red_width, red_height)
            orange_left_rect = pygame.Rect(red_left_rect.right, base_y + self.INNER_HEIGHT - orange_height, orange_width, orange_height)
            yellow_rect = pygame.Rect(orange_left_rect.right, base_y, yellow_width, self.INNER_HEIGHT)
            orange_right_rect = pygame.Rect(yellow_rect.right, base_y + self.INNER_HEIGHT - orange_height, orange_width, orange_height)
            red_right_rect = pygame.Rect(orange_right_rect.right, base_y + self.INNER_HEIGHT - red_height, red_width, red_height)

            # Truncate red bars if outside the boundaries
            if red_left_rect.left < bar_left:
                clip = bar_left - red_left_rect.left
                red_left_rect.width -= clip
                red_left_rect.left = bar_left
            if red_left_rect.width > 0:
                rects.append((red_left_rect, 1))

            rects.append((orange_left_rect, 2))
            rects.append((yellow_rect, 3))
            rects.append((orange_right_rect, 2))

            if red_right_rect.right > bar_right:
                red_right_rect.width -= (red_right_rect.right - bar_right)
            if red_right_rect.width > 0:
                rects.append((red_right_rect, 1))
        else:
            # Stage 5 or higher: two yellow bars, each with an orange on one side and a red at the tip
            side = "left" if (name_seed % 2 == 0) else "right"
            order = "small_first" if (name_seed % 4 < 2) else "big_first"

            struct1 = {
                "yellow": yellow_width,
                "orange": orange_width,
                "red": red_width
            }
            struct2 = {
                "yellow": yellow_width,
                "orange": orange_width,
                "red": 0
            }
            if order == "big_first":
                struct1, struct2 = struct2, struct1

            gap = 8
            total_width = (
                struct1["yellow"] + struct1["orange"] + struct1["red"] +
                struct2["yellow"] + struct2["orange"] + struct2["red"] +
                gap
            )
            max_x = bar_right - total_width
            min_x = bar_left
            offset = (name_seed % (max_x - min_x + 1)) if (max_x - min_x) > 0 else 0
            group_x = min_x + offset

            # First structure
            if side == "left":
                # red, orange, yellow (left to right)
                red1 = pygame.Rect(group_x, base_y + self.INNER_HEIGHT - red_height, struct1["red"], red_height)
                orange1 = pygame.Rect(red1.right, base_y + self.INNER_HEIGHT - orange_height, struct1["orange"], orange_height)
                yellow1 = pygame.Rect(orange1.right, base_y, struct1["yellow"], self.INNER_HEIGHT)
            else:
                # yellow, orange, red (left to right)
                yellow1 = pygame.Rect(group_x, base_y, struct1["yellow"], self.INNER_HEIGHT)
                orange1 = pygame.Rect(yellow1.right, base_y + self.INNER_HEIGHT - orange_height, struct1["orange"], orange_height)
                red1 = pygame.Rect(orange1.right, base_y + self.INNER_HEIGHT - red_height, struct1["red"], red_height)

            # Second structure
            group_x2 = (group_x + struct1["red"] + struct1["orange"] + struct1["yellow"] + gap
                        if side == "left"
                        else group_x + struct1["yellow"] + struct1["orange"] + struct1["red"] + gap)

            if side == "left":
                # red, orange, yellow (left to right)
                red2 = pygame.Rect(group_x2, base_y + self.INNER_HEIGHT - red_height, struct2["red"], red_height)
                orange2 = pygame.Rect(red2.right, base_y + self.INNER_HEIGHT - orange_height, struct2["orange"], orange_height)
                yellow2 = pygame.Rect(orange2.right, base_y, struct2["yellow"], self.INNER_HEIGHT)
            else:
                # yellow, orange, red (left to right)
                yellow2 = pygame.Rect(group_x2, base_y, struct2["yellow"], self.INNER_HEIGHT)
                orange2 = pygame.Rect(yellow2.right, base_y + self.INNER_HEIGHT - orange_height, struct2["orange"], orange_height)
                red2 = pygame.Rect(orange2.right, base_y + self.INNER_HEIGHT - red_height, struct2["red"], red_height)

            # Only add red2 if its width > 1 (ignore dummy red)
            if side == "left":
                if red1.width > 0: rects.append((red1, 1))
                if orange1.width > 0: rects.append((orange1, 2))
                if yellow1.width > 0: rects.append((yellow1, 3))
                if orange2.width > 0: rects.append((orange2, 2))
                if yellow2.width > 0: rects.append((yellow2, 3))
            else:
                if yellow1.width > 0: rects.append((yellow1, 3))
                if orange1.width > 0: rects.append((orange1, 2))
                if red1.width > 0: rects.append((red1, 1))
                if yellow2.width > 0: rects.append((yellow2, 3))
                if orange2.width > 0: rects.append((orange2, 2))
                # Only add red2 if it's not just a dummy
                if struct2["red"] > 1 and red2.width > 0:
                    rects.append((red2, 1))
        return rects

    def _get_strength_from_arrow(self):
        # Check which rectangle the arrow's midpoint is above
        arrow_mid = self.arrow_anim_x + self.arrow_width // 2
        rects = self.structures
        for rect, val in rects:
            if rect.left <= arrow_mid <= rect.right:
                return val
        return 0

    def draw(self, surface):
        # Draw outer border with shadow
        border_surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (0, 0, 0), (0, 0, self.WIDTH, self.HEIGHT), 0)
        blit_with_shadow(surface, border_surf, (self.x, self.y))

        # Draw inner background with shadow
        inner_surf = pygame.Surface((self.INNER_WIDTH, self.INNER_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(inner_surf, (255, 255, 255, 200), (0, 0, self.INNER_WIDTH, self.INNER_HEIGHT), 0)
        blit_with_shadow(surface, inner_surf, (self.x + 2, self.y + 2))

        # --- Draw top extension rectangle (white with black border) with shadow ---
        ext_height = 30
        ext_y = self.y - ext_height
        ext_surf = pygame.Surface((self.WIDTH, ext_height), pygame.SRCALPHA)
        pygame.draw.rect(ext_surf, (0, 0, 0), (0, 0, self.WIDTH, ext_height), 0)
        pygame.draw.rect(ext_surf, (255, 255, 255, 200), (2, 2, self.INNER_WIDTH, ext_height - 4), 0)
        blit_with_shadow(surface, ext_surf, (self.x, ext_y))

        # Draw arrow sprite at the top, centered or animating, with shadow
        if self.arrow_animating or self.selected_strength is not None:
            arrow_x = int(self.arrow_anim_x)
        else:
            arrow_x = self.x + (self.WIDTH - self.arrow_width) // 2
        arrow_y = ext_y + (ext_height - self.arrow_height) // 2
        blit_with_shadow(surface, self.arrow_sprite, (arrow_x, arrow_y))

        # --- Draw rectangles inside the bar using pet's data, with shadow ---
        orange_color = (255, 165, 0)
        yellow_color = (255, 255, 0)
        red_color = (255, 0, 0)

        color_map = {1: red_color, 2: orange_color, 3: yellow_color}
        for rect, val in self.structures:
            if rect.width > 0 and rect.height > 0:
                surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(surf, color_map[val], (0, 0, rect.width, rect.height), 0)
                blit_with_shadow(surface, surf, (rect.x, rect.y))

    def getBars(self):
        # Returns: yellow_width, orange_width, orange_height, red_width, red_height
        yellow_width = int(7 + (self.pet.level / 4))
        orange_width = int(20 + (self.pet.level / 3))
        orange_height = int(self.INNER_HEIGHT * 2 / 3)
        red_width = int(26 + (self.pet.level / 4))
        red_height = int(self.INNER_HEIGHT / 3)
        return yellow_width, orange_width, orange_height, red_width, red_height

