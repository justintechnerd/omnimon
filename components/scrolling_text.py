import pygame
from core.utils import blit_with_shadow

class ScrollingText:
    def __init__(self, text_surface, max_width, speed=1):
        """Initializes scrolling text with optimized behavior."""
        self.text_surface = text_surface
        self.max_width = max_width
        self.speed = speed  # Pixels per frame
        self.offset = 0
        self.direction = 1  # 1: left, -1: right
        self.frame_count = 0
        self.should_scroll = self.text_surface.get_width() > self.max_width  # Scroll only if necessary

    def update(self):
        """Updates text scrolling only if required."""
        if self.should_scroll:
            self.frame_count += 1
            if self.frame_count % 2 == 0:  # Scroll every 2 frames
                self.offset += self.speed * self.direction
                if self.offset + self.max_width >= self.text_surface.get_width():
                    self.direction = -1
                elif self.offset <= 0:
                    self.direction = 1

    def draw(self, surface, position):
        """Draws scrolling text or static text if it fits."""
        if not self.should_scroll:
            # If text fits, render normally
            blit_with_shadow(surface, self.text_surface, position)
        else:
            # Scroll text using clamped rect
            rect = pygame.Rect(self.offset, 0, self.max_width, self.text_surface.get_height())
            if rect.right > self.text_surface.get_width():
                rect.width = self.text_surface.get_width() - rect.left

            visible_surface = pygame.Surface((self.max_width, self.text_surface.get_height()), pygame.SRCALPHA)
            visible_surface.blit(self.text_surface, (0, 0), rect)

            # Draw the visible surface with shadow
            blit_with_shadow(surface, visible_surface, position)