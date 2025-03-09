import pygame


class InGameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width() // 4  # Menu covers 25% of the left screen
        self.active = False
        self.font = pygame.font.Font(None, 22)  # Thinner text
        self.menu_options = ["Resume", "Load Last Checkpoint", "Main Menu", "Quit"]  # Added "Restart"
        self.option_rects = []
        self.hover_index = None
        self.transparency = 5  # Always ultra-transparent

    def toggle(self):
        """Show/hide the menu_screens when called."""
        self.active = not self.active

    def handle_mouse_click(self, pos):
        """Detect if the mouse clicked on a menu_screens option."""
        if self.active:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    return self.handle_option_click(i)
            return None

    def handle_mouse_hover(self, pos):
        """Detect if the mouse is hovering over a menu_screens option."""
        previous_hover = self.hover_index
        self.hover_index = None

        if self.active:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self.hover_index = i

        if self.hover_index != previous_hover:
            self.draw_menu()

    def handle_option_click(self, index):
        """Perform actions based on menu_screens selection."""
        if self.menu_options[index] == "Resume":
            self.toggle()
            return "resume"
        elif self.menu_options[index] == "Load Last Checkpoint":
            return "Load Last Checkpoint"  # Return "restart" to notify main.py
        elif self.menu_options[index] == "Main Menu":
            return "main_menu"  # Signal to return to the start screen
        elif self.menu_options[index] == "Quit":
            pygame.quit()
            exit()
        return None

    def draw_menu(self):
        """Draw the menu_screens only when active."""
        if self.active:
            menu_surface = pygame.Surface((self.width, self.screen.get_height()), pygame.SRCALPHA)
            menu_surface.fill((50, 50, 50, self.transparency))  # Fixed ultra-transparent background

            self.screen.blit(menu_surface, (0, 0))

            self.option_rects.clear()

            # Layout settings (perfected by you)
            option_spacing = 40
            start_y = 120
            box_width = int(self.width * 0.8)
            box_height = 30

            for i, option in enumerate(self.menu_options):
                box_rect = pygame.Rect(
                    (self.width - box_width) // 2,
                    start_y + i * option_spacing,
                    box_width,
                    box_height
                )

                # Grey border by default, white when hovered
                border_color = (255, 255, 255) if i == self.hover_index else (150, 150, 150)
                pygame.draw.rect(self.screen, border_color, box_rect, 1, border_radius=5)

                # Centered text with 1px stroke
                text_surface = self.font.render(option, True, (255, 255, 255))
                text_outline = self.font.render(option, True, (0, 0, 0))  # 1px black stroke

                text_rect = text_surface.get_rect(center=box_rect.center)

                # Stroke effect
                self.screen.blit(text_outline, (text_rect.x - 1, text_rect.y))
                self.screen.blit(text_outline, (text_rect.x + 1, text_rect.y))
                self.screen.blit(text_outline, (text_rect.x, text_rect.y - 1))
                self.screen.blit(text_outline, (text_rect.x, text_rect.y + 1))

                self.screen.blit(text_surface, text_rect)

                self.option_rects.append(box_rect)  # Store full button area for clicking
