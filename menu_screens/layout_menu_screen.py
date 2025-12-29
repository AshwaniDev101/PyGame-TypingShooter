import pygame
from config.loader import Loader
from menu_screens.gui_button import HintButton


class LayoutMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.active = True

        # Load the placeholder image
        self.image = Loader.load_image("assets/images/game_window/keyboard.png")

        # Font for the ESC hint button
        self.button_font = pygame.font.Font(None, 24)

        # Top-left "Press ESC" hint button (with hover support)
        self.esc_button = HintButton(
            text="Back (Esc)",
            pos=(10, 10),
            font=self.button_font,
            can_hover=True
        )

        # Center the main image
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.image_rect = self.image.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )

    def handle_events(self, events):
        """Handle events and return action if needed."""
        for event in events:
            # Update hover state for the button
            if event.type == pygame.MOUSEMOTION:
                self.esc_button.update_hover(event.pos)

            # Click on the "Press ESC" button
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.esc_button.rect.collidepoint(event.pos):
                    self.active = False
                    return "Escape"

            # ESC key to go back
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.active = False
                    return "Escape"

            # Window close
            elif event.type == pygame.QUIT:
                self.active = False
                return "Exit"

        return None

    def draw(self):
        """Draw the placeholder screen."""
        # Solid dark background (no stars)
        self.screen.fill((30, 30, 30))

        # Draw centered image
        self.screen.blit(self.image, self.image_rect)

        # Draw the ESC hint button (with hover glow if applicable)
        self.esc_button.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """Main loop."""
        while self.active:
            events = pygame.event.get()
            action = self.handle_events(events)

            if action:
                return action  # Returns "Escape" or "Exit"

            self.draw()
            self.clock.tick(30)

        return "Exit"