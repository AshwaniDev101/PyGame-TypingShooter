import pygame
import random

from config.utils import loader_scale_image

PLUS_ONE_LIFETIME = 80  # Duration the "+X" effect remains visible


# =============================================
# PlusXEffect Class (for ammo gain visual effect)
# =============================================
class PlusXEffect:
    def __init__(self, x, y, amount):
        randomizer = 20
        self.x = x + random.randint(-randomizer, randomizer)
        self.y = y + random.randint(-randomizer, randomizer)
        self.alpha = 255
        self.lifetime = PLUS_ONE_LIFETIME
        self.amount = amount
        self.ammo_image = loader_scale_image("assets/images/animated/ammo_plus.png", 30)

    def update(self):
        # Move the '+X' effect upward and fade it out
        self.y -= 0.5
        if self.lifetime < PLUS_ONE_LIFETIME // 2:
            self.alpha -= 5
            if self.alpha < 0:
                self.alpha = 0
        self.lifetime -= 1

    def draw(self, screen):
        # Draw the ammo image and '+X' text with fading transparency
        if self.lifetime > 0:
            self.ammo_image.set_alpha(self.alpha)
            screen.blit(self.ammo_image, (self.x, self.y))
            font = pygame.font.Font(None, 30)
            text_surface = font.render(f"+{self.amount}", True, (255, 255, 255))
            text_surface.set_alpha(self.alpha)
            screen.blit(text_surface, (self.x + 10, self.y + 5))
