
import pygame

from config import constants


# =============================================
# Shockwave Effect Class
# =============================================
class Shockwave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.alpha = 255  # Full opacity
        self.color = (255, 255, 255)

    def update(self):
        # Expand the shockwave and gradually fade it out
        self.radius += 5
        self.alpha -= 10
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, screen):
        # Draw the shockwave with fading transparency
        if self.alpha > 0:
            surface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, self.alpha), (self.x, self.y), self.radius, 2)
            screen.blit(surface, (0, 0))
