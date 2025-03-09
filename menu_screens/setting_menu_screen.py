import pygame
import random

from menu_screens.gui_button import HintButton


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.active = True  # Flag for the loop

        # Load and scale image
        self.image = pygame.image.load("assets/images/game_window/sad_emoji.png")
        self.image = pygame.transform.scale(self.image, (300, 300))  # Adjust size as needed

        # Set up apology text
        self.font = pygame.font.Font(None, 36)
        self.message = "Oops! This section isn't ready yet."  # Short but meaningful apology
        self.text_surface = self.font.render(self.message, True, (255, 255, 255))

        # Get screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.button_font = pygame.font.Font(None, 24)
        self.esc_button = HintButton(text="Press ESC", can_hover=True, pos=[10, 10], font=self.button_font)

        # Calculate centered positions
        # Position the image a bit above the vertical center
        self.image_rect = self.image.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        # Position the text below the image
        self.text_rect = self.text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 150))

    def handle_events(self, events):
        """Process events for closing the window."""
        for event in events:
            if event.type == pygame.QUIT:
                self.active = False
                return "Exit"

    def draw(self):
        """Draw the centered image, apology text, and ESC hint button."""
        # Fill the background with a dark color
        self.screen.fill((30, 30, 30))
        # Blit the image and apology text
        self.screen.blit(self.image, self.image_rect)
        self.screen.blit(self.text_surface, self.text_rect)
        # Draw the ESC hint button
        self.display_buttons()
        # Update the display
        pygame.display.flip()

    def display_buttons(self):
        """Display the ESC hint button (for visual purposes only)."""
        # Simply draw the button on the screen
        self.esc_button.draw(self.screen)

    def run(self):
        """Run the loop to keep the screen active."""
        while self.active:
            events = pygame.event.get()
            self.handle_events(events)
            self.draw()
            self.clock.tick(30)  # Limit to 30 frames per second


