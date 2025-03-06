import pygame

class GameIntro:
    def __init__(self, screen, width=1020, height=800):
        self.screen = screen
        self.WIDTH, self.HEIGHT = width, height

        # Colors
        self.BLACK = (0, 0, 0)
        self.BUTTON_COLOR = (50, 150, 250)
        self.BUTTON_HOVER = (30, 130, 230)
        self.TEXT_COLOR = (255, 255, 255)
        self.BLUE_COLOR = (100, 200, 255)  # Captain
        self.RED_COLOR = (255, 50, 50)  # Mothership, Defenses
        self.LAST_HOPE_COLOR = (50, 255, 50)  # Last Hope
        self.BORDER_COLOR = self.TEXT_COLOR

        # Fonts
        self.font = pygame.font.Font(None, 30)
        self.highlight_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 30)

        # Text Lines
        self.lines = [
            [("Welcome, ", self.TEXT_COLOR), ("Captain.", self.BLUE_COLOR)],  # Line 1
            [("The ", self.TEXT_COLOR), ("Enemy Mothership", self.RED_COLOR),
             (" is waiting just outside our solar system.", self.TEXT_COLOR)],  # Line 2
            [("Surrounded by endless ", self.TEXT_COLOR), ("layers of defenses.", self.RED_COLOR)],  # Line 3
            [("You're our ", self.TEXT_COLOR), ("last hope", self.LAST_HOPE_COLOR), (". Godspeed.", self.TEXT_COLOR)]  # Line 4
        ]

        # Fade Settings
        self.alpha = 0
        self.fade_speed = 15
        self.fade_in = True
        self.show_message = True

        # Box Settings
        self.box_width = self.WIDTH // 1.5
        self.box_height = self.HEIGHT // 2.8
        self.box_rect = pygame.Rect((self.WIDTH - self.box_width) // 2, self.HEIGHT // 3, self.box_width, self.box_height)
        self.border_thickness = 2
        self.border_growing = True

        # Button Settings (Now Dynamic Width)
        self.button_text = self.button_font.render("Close", True, self.TEXT_COLOR)
        text_width, text_height = self.button_text.get_size()
        padding = 20  # Padding around text
        self.button_width = text_width + padding
        self.button_height = text_height + 10
        self.button_rect = pygame.Rect(self.WIDTH // 2 - self.button_width // 2,
                                       self.HEIGHT // 2 + 90,
                                       self.button_width,
                                       self.button_height)

        # Game Loop Flag
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    self.running = False  # Close the intro if Esc, Space, or Enter is pressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(event.pos):
                    self.running = False  # Close the intro when clicking the "Next" button

    def fade_in_text(self):
        """Handles text fading animation."""
        if self.fade_in and self.alpha < 255:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.fade_in = False

    def animate_border(self):
        """Animates the growing and shrinking border."""
        if self.border_growing:
            self.border_thickness += 0.3
            if self.border_thickness >= 5:
                self.border_growing = False
        else:
            self.border_thickness -= 0.3
            if self.border_thickness <= 2:
                self.border_growing = True

    def draw_text(self):
        """Draws the intro text with color highlights."""
        y = self.box_rect.y + 40
        for line in self.lines:
            x = self.box_rect.x + 20
            for word, color in line:
                text_surface = self.highlight_font.render(word, True, color) if color in [self.BLUE_COLOR, self.RED_COLOR, self.LAST_HOPE_COLOR] else self.font.render(word, True, color)
                text_surface.set_alpha(self.alpha)
                self.screen.blit(text_surface, (x, y))
                x += text_surface.get_width()
            y += 45

    def draw_button(self):
        """Draws the next button and centers the text inside it."""
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.BUTTON_HOVER if self.button_rect.collidepoint(mouse_pos) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=5)

        # Center the text inside the button
        text_x = self.button_rect.x + (self.button_rect.width - self.button_text.get_width()) // 2
        text_y = self.button_rect.y + (self.button_rect.height - self.button_text.get_height()) // 2
        self.screen.blit(self.button_text, (text_x, text_y))

    def run(self):
        """Runs the intro screen loop."""
        while self.running:
            self.screen.fill(self.BLACK)
            self.handle_events()
            self.fade_in_text()
            self.animate_border()

            # Render message box only if still showing
            if self.show_message:
                pygame.draw.rect(self.screen, self.BORDER_COLOR, self.box_rect, int(self.border_thickness))
                self.draw_text()
                self.draw_button()

            pygame.display.update()
            pygame.time.delay(20)

        # pygame.quit()

# ==== Running the Intro Screen ====
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1020, 800))
    pygame.display.set_caption("Game Intro")

    intro = GameIntro(screen)
    intro.run()
