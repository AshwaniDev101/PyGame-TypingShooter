import random
import string

import pygame
import sys, os

from config.loader import Loader


def loader_scale_image(image_path, target_height):
    # Use the resource_path helper to get the correct path.
    image_path = Loader.resource_path(image_path)
    image = pygame.image.load(image_path).convert_alpha()
    original_width, original_height = image.get_size()
    aspect_ratio = original_width / original_height
    new_width = int(target_height * aspect_ratio)
    return pygame.transform.smoothscale(image, (new_width, target_height))


def color(hex_color: str):
    """Converts a HEX color string to a Pygame Color object."""
    if not hex_color.startswith("#"):
        hex_color = f"#{hex_color}"
    return pygame.Color(hex_color)


def color_with_alpha(hex_color: str, alpha: int = 255):
    """Converts a HEX color string to a Pygame Color object with optional alpha."""
    if not hex_color.startswith("#"):
        hex_color = f"#{hex_color}"

    col = pygame.Color(hex_color)
    col.a = max(0, min(alpha, 255))  # Ensure alpha stays within valid range (0-255)

    return col


def draw_transparent_circle(surface, color, center, radius, alpha=128):
    # Create a temporary surface with per-pixel alpha
    circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    # Draw a circle with the specified transparency
    pygame.draw.circle(circle_surface, (color[0], color[1], color[2], alpha), (radius, radius), radius)

    # Blit the transparent circle onto the main surface
    surface.blit(circle_surface, (center[0] - radius, center[1] - radius))


def draw_transparent_circle_with_gradient(surface, color, center, radius, alpha=128):
    """ Draws a transparent circle with a darker border and gradient effect. """
    circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    # Darker border color (adjust intensity)
    # border_color = (max(color[0] - 30, 0), max(color[1] - 30, 0), max(color[2] - 30, 0), alpha)

    # Draw gradient by layering circles
    for i in range(radius, 0, -1):
        fade_alpha = int(alpha * (i / radius))  # Reduce transparency toward center
        pygame.draw.circle(circle_surface, (color[0], color[1], color[2], fade_alpha), (radius, radius), i)

    # Draw the border with the darker color
    # pygame.draw.circle(circle_surface, border_color, (radius, radius), radius, width=10)

    # Draw the yellow border
    # pygame.draw.circle(circle_surface, color_with_alpha("F9FFF9",125), (radius, radius), radius, width=5)

    surface.blit(circle_surface, (center[0] - radius, center[1] - radius))

def generate_random_word(min,max):
    length = random.randint(min, max)  # Choose a random length between 5 and 20
    word = ''.join(random.choices(string.ascii_lowercase, k=length))
    return word

def generate_random_letter():
    # Choose one random letter from the lowercase alphabet.
    return random.choice(string.ascii_lowercase)
