import os
import sys
import pygame
import json

class Loader:
    @staticmethod
    def resource_path(relative_path):
        """
        Returns the absolute path to a resource.
        Works both in development and when bundled with PyInstaller.
        """
        try:
            # When bundled, PyInstaller sets sys._MEIPASS.
            base_path = sys._MEIPASS
        except Exception:
            # Since this file is in "D:\DSA\Pygame Game Jam\config",
            # go one level up to get to the project root.
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_image(relative_path, convert_alpha=True):
        """
        Load an image from the specified relative path.
        If convert_alpha is True, the image is converted for optimal display with per-pixel alpha.
        """
        path = Loader.resource_path(relative_path)
        image = pygame.image.load(path)
        if convert_alpha:
            return image.convert_alpha()
        return image.convert()

    @staticmethod
    def load_sound(relative_path):
        """
        Load a sound file from the specified relative path.
        """
        path = Loader.resource_path(relative_path)
        return pygame.mixer.Sound(path)

    @staticmethod
    def load_music(relative_path):
        """
        Load a music file from the specified relative path using pygame.mixer.music.
        This sets up the music stream for playback.
        """
        path = Loader.resource_path(relative_path)
        pygame.mixer.music.load(path)

    @staticmethod
    def load_json(relative_path):
        """
        Load and parse a JSON file from the specified relative path.
        """
        path = Loader.resource_path(relative_path)
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def load_font(relative_path, size):
        """
        Load a font from the specified relative path and size.
        """
        path = Loader.resource_path(relative_path)
        return pygame.font.Font(path, size)
