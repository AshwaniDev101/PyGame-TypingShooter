import math

import pygame

from config import constants, utils

HIT_EFFECT_DURATION = 1000        # milliseconds
MAX_ALPHA = 200                   # maximum opacity for hit effect
BORDER_THICKNESS = 40             # thickness of the border for hit effect

class HitEffect:
    """
    Class to handle the player's hit effect with a pulsating border.
    """
    def __init__(self, screen, duration=HIT_EFFECT_DURATION, max_alpha=MAX_ALPHA, border_thickness=BORDER_THICKNESS):
        """
        :param screen: The pygame display surface.
        :param duration: Duration of the effect in milliseconds.
        :param max_alpha: Maximum opacity for the effect.
        :param border_thickness: Thickness of the border effect.
        """
        self.screen = screen
        self.duration = duration
        self.max_alpha = max_alpha
        self.border_thickness = border_thickness
        self.active = False
        self.start_time = 0

    def trigger(self):
        """Activate the hit effect."""
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def update_and_draw(self):
        """Update and draw the hit effect if active."""
        if not self.active:
            return
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time < self.duration:
            alpha = int(self.max_alpha * abs(math.sin(elapsed_time / 200)))
            overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA)
            for i in range(1, 4):
                color = utils.color_with_alpha("0005FF",alpha // (i + 1))
                # color = (0, 200, 255, alpha // (i + 1))
                pygame.draw.rect(overlay, color, (i, i, constants.SCREEN_WIDTH - 2 * i, self.border_thickness))
                pygame.draw.rect(overlay, color, (i, constants.SCREEN_HEIGHT - self.border_thickness - i,
                                                  constants.SCREEN_WIDTH - 2 * i, self.border_thickness))
                pygame.draw.rect(overlay, color, (i, i, self.border_thickness, constants.SCREEN_HEIGHT - 2 * i))
                pygame.draw.rect(overlay, color, (constants.SCREEN_WIDTH - self.border_thickness - i, i,
                                                  self.border_thickness, constants.SCREEN_HEIGHT - 2 * i))
            self.screen.blit(overlay, (0, 0))
        else:
            self.active = False