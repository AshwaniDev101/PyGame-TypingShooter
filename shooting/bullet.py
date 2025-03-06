import pygame
from config import constants
import math

class Bullet:
    def __init__(self, firing_point, target_enemy, letter):
        self.x, self.y = firing_point


        self.target = target_enemy
        self.surface = pygame.Surface((constants.BULLET_WIDTH, constants.BULLET_HEIGHT), pygame.SRCALPHA)
        self.surface.fill(constants.YELLOW)

        # Calculate correct angle
        dx = target_enemy.rect.centerx - self.x
        dy = target_enemy.rect.centery - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

        self.rect = self.surface.get_rect(center=(self.x, self.y))

        # Attaching letter to bullet
        self.letter = letter
        self.font = pygame.font.Font(None, 30)

    def update(self):
        # Move bullet toward the enemy in a homing manner.
        if self.target:
            dx = self.target.rect.centerx - self.x
            dy = self.target.rect.centery - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                dx, dy = dx / distance, dy / distance  # Normalize
                self.x += dx * constants.BULLET_SPEED
                self.y += dy * constants.BULLET_SPEED
                self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Rotate and draw the bullet
        rotated_bullet = pygame.transform.rotate(self.surface, -self.angle)
        rotated_rect = rotated_bullet.get_rect(center=self.rect.center)
        screen.blit(rotated_bullet, rotated_rect.topleft)

        # Drawing letter with bullet
        # letter_surface = self.font.render(self.letter, True, (255, 255, 255))
        # screen.blit(letter_surface, (self.rect.x + 20, self.rect.y + 20))

