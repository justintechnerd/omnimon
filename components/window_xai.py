import pygame
from core.constants import XAI_ICON_PATH


class WindowXai:
    FRAME_SIZE = 48
    FRAME_COUNT = 7

    def __init__(self, x, y, width, height, xai_number):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xai_number = max(1, min(self.FRAME_COUNT, xai_number))
        self.sprite_sheet = pygame.image.load(XAI_ICON_PATH).convert_alpha()
        self.current_frame = self.xai_number - 1
        self.rolling = False
        self.roll_timer = 0
        self.roll_speed = 5  # frames per sprite change

        # Animation state for stop effect
        self.stopping = False
        self.stop_target_frame = None
        self.rect_anim_progress = 0
        self.rect_anim_speed = 8  # pixels per frame
        self.rect_anim_max = self.height // 2
        self.rect_anim_phase = 0  # 0: expanding, 1: shrinking

        # Cache scaled sprites
        self.scaled_sprites = []
        for i in range(self.FRAME_COUNT):
            frame_rect = pygame.Rect(i * self.FRAME_SIZE, 0, self.FRAME_SIZE, self.FRAME_SIZE)
            icon = self.sprite_sheet.subsurface(frame_rect)
            icon = pygame.transform.scale(icon, (self.width, self.height))
            self.scaled_sprites.append(icon)

    def roll(self):
        self.rolling = True
        self.stopping = False
        self.roll_timer = 0

    def stop(self, xai_number=None):
        # Begin stop animation
        self.stopping = True
        self.rolling = True  # keep rolling during animation
        self.rect_anim_progress = 0
        self.rect_anim_phase = 0
        if xai_number is not None:
            self.stop_target_frame = max(1, min(self.FRAME_COUNT, xai_number)) - 1
        else:
            self.stop_target_frame = self.current_frame

    def update(self):
        if self.rolling:
            self.roll_timer += 1
            if self.roll_timer >= self.roll_speed:
                self.roll_timer = 0
                self.current_frame = (self.current_frame + 1) % self.FRAME_COUNT

        if self.stopping:
            if self.rect_anim_phase == 0:
                # Expand rectangles
                self.rect_anim_progress += self.rect_anim_speed
                if self.rect_anim_progress >= self.rect_anim_max:
                    self.rect_anim_progress = self.rect_anim_max
                    # Switch to stopped frame and start shrinking
                    self.current_frame = self.stop_target_frame
                    self.rolling = False
                    self.rect_anim_phase = 1
            elif self.rect_anim_phase == 1:
                # Shrink rectangles
                self.rect_anim_progress -= self.rect_anim_speed
                if self.rect_anim_progress <= 0:
                    self.rect_anim_progress = 0
                    self.stopping = False  # Animation done

    def draw(self, surface):
        icon = self.scaled_sprites[self.current_frame]
        surface.blit(icon, (self.x, self.y))

        if self.stopping and self.rect_anim_progress > 0:
            # Draw expanding/shrinking rectangles from top and bottom
            rect_height = self.rect_anim_progress
            top_rect = pygame.Rect(self.x, self.y, self.width, rect_height)
            bottom_rect = pygame.Rect(self.x, self.y + self.height - rect_height, self.width, rect_height)
            color = (0, 0, 0)  # Black, or choose another color for the effect
            pygame.draw.rect(surface, color, top_rect)
            pygame.draw.rect(surface, color, bottom_rect)