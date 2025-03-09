import pygame
import random
# =============================================
# Particle Class (for bullet hit particles)
# =============================================
class Particle:
    def __init__(self, x, y, color, lifetime=20):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(1, 2)
        self.lifetime = lifetime
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)

    def update(self):
        # Update particle position based on velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1

    def draw(self, screen):
        # Draw the particle as a small circle
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)