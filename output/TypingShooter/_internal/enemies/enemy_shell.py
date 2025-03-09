import pygame
from math import sin
from config import utils, constants
from config.loader import Loader
from enemies.enemy import Enemy


class EnemyShell(Enemy):
    def __init__(self, player, battleship, horizontal_speed=0, is_round=False):
        super().__init__(player)
        self.is_round = is_round  # Boolean to determine shape type
        self.speed = 5  # Vertical speed (drop rate)
        self.speed_x = horizontal_speed  # Horizontal drift speed
        self.word = utils.generate_random_letter()

        if self.is_round:
            # For round shells, use a circular design with an animated outer yellow circle.
            self.diameter = 20  # Overall surface size
            self.image = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
            # Outer circle oscillates between a minimum and maximum radius.
            self.outer_min_radius = 7  # Minimum radius for the yellow circle
            self.outer_max_radius = self.diameter // 2  # Maximum radius (10 if diameter is 20)
            self.size_phase = 0.0  # Phase for oscillation of the outer circle size
            self.draw_round_bullet()
        else:
            # For square (rectangular) shells, use a fixed rectangle.
            self.image = pygame.Surface((5, 20))
            self.draw_square_bullet()

        # Position the shell at the battleship's center.
        self.rect = self.image.get_rect(center=battleship.rect.center)

    def draw_square_bullet(self):
        """Draws the square (rectangular) bullet."""
        self.image.fill(utils.color("FFB34B"))

    def draw_round_bullet(self):
        """
        Draws the round bullet:
        - Outer circle: Animated yellow circle that changes size.
        - Inner circle: Fixed red circle.
        """
        # Clear the surface with a transparent fill.
        self.image.fill((0, 0, 0, 0))
        center = (self.diameter // 2, self.diameter // 2)

        # Calculate the oscillating outer yellow circle's radius.
        outer_radius = int(self.outer_min_radius +
                           (self.outer_max_radius - self.outer_min_radius) * ((sin(self.size_phase) + 1) / 2))
        outer_color = utils.color("FFB34B")  # Yellow

        pygame.draw.circle(self.image, outer_color, center, outer_radius)

        # Draw the inner circle with a fixed red color.
        inner_color = utils.color("FF2117")  # Red
        inner_radius = int(outer_radius * 0.5)
        pygame.draw.circle(self.image, inner_color, center, inner_radius)

    def animate_round_bullet(self):
        """Updates the animation phase for the round bullet and redraws it."""
        self.size_phase += 0.1  # Adjust phase for oscillation speed.
        self.draw_round_bullet()

    def move(self, gameover):
        """Move the shell diagonally to simulate a thrown ball effect."""
        if self.is_round:
            # Update the animation for the round bullet.
            self.animate_round_bullet()

        if gameover:
            # If game is over, fall straight down faster.
            self.rect.y += self.speed * 2
        else:
            # Apply horizontal drift and vertical drop.
            self.rect.x += self.speed_x
            self.rect.y += self.speed
