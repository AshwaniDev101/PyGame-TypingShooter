# PlayerBullet.py
import pygame
from config import constants
import math
from bullet import Bullet

class PlayerBullet(Bullet):
    def __init__(self, firing_point, target_enemy, letter):
        """
        Initialize a player bullet.
        Inherits from Bullet and uses its properties.
        """
        super().__init__(firing_point, target_enemy, letter)
        # Ensure the bullet is yellow (player bullet color)
        self.surface.fill(constants.YELLOW)
        # For a straight upward shot, we can ignore the homing angle.
        self.angle = 0

    def update(self):
        """
        Move the bullet upward at a constant speed.
        """
        # Move upward (decrease y)
        self.y -= constants.BULLET_SPEED
        self.rect.center = (self.x, self.y)
