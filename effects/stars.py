import pygame
import random
import math
from config import constants


class StarBackground:
    def __init__(self):
        self.star_speed = 2  # Default speed
        self.num_stars = 300
        self.num_twinkles = 50

        self.stars = self.generate_stars(self.num_stars, sizes=[1, 2])
        self.twinkling_stars = self.generate_twinkling_stars(self.num_twinkles, sizes=[1, 2])

    def generate_stars(self, count, sizes):
        """Generate regular stars with given sizes."""
        stars = []
        for _ in range(count):
            x = random.randint(0, constants.SCREEN_WIDTH)
            y = random.randint(0, constants.SCREEN_HEIGHT)
            size = random.choice(sizes)
            stars.append((x, y, size))
        return stars

    def generate_twinkling_stars(self, count, sizes):
        """Generate twinkling stars with given sizes and a random phase for twinkling effect."""
        stars = []
        for _ in range(count):
            x = random.randint(0, constants.SCREEN_WIDTH)
            y = random.randint(0, constants.SCREEN_HEIGHT)
            size = random.choice(sizes)
            phase = random.uniform(0, 2 * math.pi)
            stars.append((x, y, size, phase))
        return stars

    def update_star_position(self, star):
        """Update position for a regular star."""
        x, y, size = star
        y += self.star_speed
        if y > constants.SCREEN_HEIGHT:
            y = 0
            x = random.randint(0, constants.SCREEN_WIDTH)
        return x, y, size

    def update_twinkle_position(self, star):
        """Update position for a twinkling star."""
        x, y, size, phase = star
        y += self.star_speed
        if y > constants.SCREEN_HEIGHT:
            y = 0
            x = random.randint(0, constants.SCREEN_WIDTH)
        return (x, y, size, phase)

    def draw_star(self, screen, star):
        """Draw a regular star as a white rectangle."""
        x, y, size = star
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(x, y, size, size))

    def draw_twinkle(self, screen, star, current_time):
        """Draw a twinkling star with brightness based on a sine function."""
        x, y, size, phase = star
        brightness_factor = (math.sin(current_time / 200.0 + phase) + 1) / 2  # Normalize between 0 and 1
        brightness = int(200 * brightness_factor + 55)  # Keep brightness between 55 and 255
        color = (brightness, brightness, brightness)
        pygame.draw.rect(screen, color, pygame.Rect(x, y, size, size))

    def update_and_draw(self, screen, current_time):
        """Update positions and draw both regular and twinkling stars."""
        # Update and draw regular stars
        updated_stars = []
        for star in self.stars:
            new_star = self.update_star_position(star)
            updated_stars.append(new_star)
            self.draw_star(screen, new_star)
        self.stars = updated_stars

        # Update and draw twinkling stars
        updated_twinkles = []
        for star in self.twinkling_stars:
            new_star = self.update_twinkle_position(star)
            updated_twinkles.append(new_star)
            self.draw_twinkle(screen, new_star, current_time)
        self.twinkling_stars = updated_twinkles

    def set_speed(self, speed):
        """Adjust the speed of the stars."""
        self.star_speed = speed
