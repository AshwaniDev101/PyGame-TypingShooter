import pygame

from config import utils
from config.loader import Loader
from menu_screens.gui_button import HintButton


class LayoutMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.active = True  # Flag for the loop

        # Get screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        # Set up fonts for the text
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 28)

        # Multi-paragraph thank you message
        self.paragraphs = [
            "Thank you for playing my game!",
            "- Bunny#3001",

        ]
        # Render each paragraph into a text surface
        self.text_surfaces = [
            self.text_font.render(line, True, (255, 255, 255)) for line in self.paragraphs
        ]

        # Define the square dimensions (adjust as needed)
        self.square_width = 400
        self.square_height = 400
        self.square_rect = pygame.Rect(
            (self.screen_width - self.square_width) // 2,
            (self.screen_height - self.square_height) // 2,
            self.square_width,
            self.square_height
        )

        # Set up ESC button (for exiting the screen)
        self.button_font = pygame.font.Font(None, 24)
        self.esc_button = HintButton(text="Press ESC", can_hover=True, pos=[10, 10], font=self.button_font)

    def handle_events(self, events):
        """Process events for closing the window or pressing ESC."""
        for event in events:
            if event.type == pygame.QUIT:
                self.active = False
                return "Exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.active = False
                    return "Exit"

    def draw(self):
        """Draw the decorated square, thank you text, and ESC hint button."""
        # Fill the background with a dark color
        self.screen.fill((30, 30, 30))

        # Load and scale the image to 500x500
        # image = Loader.load_image("assets/images/game_window/bunny.jpg")
        image = utils.loader_scale_image("assets/images/game_window/bunny.jpg",100)

        # Center the image on the screen
        image_rect = image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(image, image_rect)

        # Draw multi-paragraph text inside the square
        text_padding = 20
        current_y = self.square_rect.top + text_padding
        for surface in self.text_surfaces:
            # Center each line horizontally within the square
            text_rect = surface.get_rect(centerx=self.square_rect.centerx, y=current_y)
            self.screen.blit(surface, text_rect)
            current_y += surface.get_height() + 10  # Space between paragraphs

        # Draw the ESC hint button
        self.esc_button.draw(self.screen)

        # Update the display
        pygame.display.flip()

    def run(self):
        """Main loop to keep the screen active."""
        while self.active:
            events = pygame.event.get()
            self.handle_events(events)
            self.draw()
            self.clock.tick(30)  # Limit to 30 frames per second


# To run the menu, you'd typically initialize pygame and create a screen like this:
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    menu = LayoutMenu(screen)
    menu.run()
    pygame.quit()
