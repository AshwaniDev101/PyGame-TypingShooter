import random
import string

import pygame
import math
from config import constants, utils
from enemies.enemy import Enemy

class EnemySuicideDrone(Enemy):
    """
    A suicide drone that starts off-screen, then once it reaches y = 0,
    it draws a guiding line to the player and homes directly toward them.
    Its appearance is a pulsating, plane-like shape that always points toward the player.
    """
    def __init__(self, player):
        """
        Initialize the drone with a random horizontal start position (off-screen vertically),
        set its size, speed, and initialize pulsating effect variables.
        """
        super().__init__(player)
        self.rect = pygame.Rect(
            random.randint(50, constants.SCREEN_WIDTH - 50),
            -50,
            30, 30  # Adjust size as needed
        )
        self.word = ''.join(random.choices(string.ascii_lowercase, k=3))  # Optional label
        self.speed = random.uniform(2, 4)  # Drone's speed
        self.angle = 0  # Angle the drone is facing; used for rotating the shape
        self.pulse = 0  # Controls the pulsating effect magnitude
        self.pulse_direction = 1  # Determines whether the pulse is increasing or decreasing

    def _get_vector_to_player(self):
        """
        Calculate the normalized vector and distance from the drone to the player.
        Returns:
            ndx, ndy (floats): Normalized direction components.
            distance (float): Euclidean distance between the drone and the player.
        """
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            ndx = dx / distance
            ndy = dy / distance
        else:
            ndx, ndy = 0, 0
        return ndx, ndy, distance

    def move(self, game_over):
        """
        Update the drone's position.
        - Before reaching y = 0, it moves straight downward.
        - Once on-screen (y >= 0), it homes directly toward the player.
        If game_over is True, the drone moves downward faster.
        """
        if game_over:
            self.rect.y += self.speed * 2
            return

        if self.rect.y < 0:
            # Move straight down until the drone is visible
            self.rect.y += self.speed
        else:
            ndx, ndy, _ = self._get_vector_to_player()
            self.rect.x += ndx * self.speed
            self.rect.y += ndy * self.speed
            # Update angle so that the nose points toward the player.
            # The triangle is defined with its nose at (0, -base_size); hence, add 90°.
            self.angle = math.degrees(math.atan2(
                self.player.rect.centery - self.rect.centery,
                self.player.rect.centerx - self.rect.centerx
            )) + 90

        self._update_pulse()
        self.move_handle_pushback()

    def _update_pulse(self):
        """
        Update the pulse value to create a smooth pulsating effect.
        The pulse oscillates between -2 and 2.
        """
        self.pulse += self.pulse_direction * 0.2
        if self.pulse > 2 or self.pulse < -2:
            self.pulse_direction *= -1

    def draw(self, screen):
        """
        Draw the drone on the screen.
        - Draws a pulsating, plane-like shape that rotates to face the player.
        - If the drone is on-screen (y >= 0), draws a guiding line from the drone to the player.
        """
        self._draw_plane_shape(screen)
        if self.rect.y >= 0:
            self._draw_guiding_line(screen)
        self.draw_word(screen)

    def _draw_plane_shape(self, screen):
        """
        Draw a plane-like shape that pulses in size.
        The shape is defined as a simple triangle, with its nose at (0, -base_size).
        The triangle is rotated so that its nose always points toward the player.
        """
        # Base size modulated by the pulsating effect.
        base_size = 10 + self.pulse  # The base size of your shape
        # Triangle defined with its nose at (0, -base_size)
        points = [
            (0, -base_size),  # Tip of the triangle
            (-base_size / 2, base_size),  # Left wing
            (base_size / 2, base_size)  # Right wing
        ]
        # Rotate points using the computed self.angle
        angle_rad = math.radians(self.angle)
        rotated_points = [self._rotate_point(pt, angle_rad) for pt in points]
        translated_points = [
            (self.rect.centerx + pt[0], self.rect.centery + pt[1])
            for pt in rotated_points
        ]
        pygame.draw.polygon(screen, utils.color("FF3E31"), translated_points)


    def _rotate_point(self, point, angle):
        """
        Rotate a point (x, y) around the origin by the given angle in radians.
        Returns the rotated point.
        """
        x, y = point
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        return x * cos_theta - y * sin_theta, x * sin_theta + y * cos_theta

    def _draw_guiding_line(self, screen):
        """
        Draw a guiding line from the drone's center to the player's center.
        Only drawn if the drone is on-screen (y >= 0).
        """
        start_pos = self.rect.center
        end_pos = self.player.rect.center
        pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 1)
