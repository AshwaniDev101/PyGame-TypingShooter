import pygame
import random


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.active = True  # Flag for the settings loop

        # --- Font Setup ---
        self.font = pygame.font.Font(None, 24)  # General font for labels and text

        # --- Text Field Setup (Label: "Size") ---
        self.size_label = "Size:"  # Label text
        self.size_text = "100"  # Default text value
        self.size_rect = pygame.Rect(100, 100, 140, 30)  # Rectangle for the text field
        self.size_active = False  # Whether the text field is active for input

        # --- Option Menu Setup ---
        self.option_menu_options = ["Low", "Medium", "High"]
        # Choose a random default option
        self.current_option = random.choice(self.option_menu_options)
        self.option_rect = pygame.Rect(100, 150, 140, 30)  # Rectangle for the option menu_screens

        # --- Checkbox Setup ---
        self.checkbox_checked = False
        self.checkbox_rect = pygame.Rect(100, 200, 20, 20)  # Rectangle for the checkbox
        self.checkbox_label = "Enable Feature"

        # --- Restore Button Setup ---
        button_width = 90
        button_height = 30
        margin = 20
        # Place restore button at the bottom-right of the screen
        self.restore_button_rect = pygame.Rect(
            self.screen.get_width() - button_width - margin,
            self.screen.get_height() - button_height - margin,
            button_width,
            button_height
        )

    def handle_events(self, events):
        """Process events for the settings menu_screens."""
        for event in events:
            if event.type == pygame.QUIT:
                self.active = False
                return "Exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Check if click is in the size text field
                if self.size_rect.collidepoint(pos):
                    self.size_active = True
                else:
                    self.size_active = False
                # Check if click is in the option menu_screens rectangle; if so, cycle options
                if self.option_rect.collidepoint(pos):
                    current_index = self.option_menu_options.index(self.current_option)
                    current_index = (current_index + 1) % len(self.option_menu_options)
                    self.current_option = self.option_menu_options[current_index]
                # Check if click is in the checkbox rectangle; if so, toggle its state
                if self.checkbox_rect.collidepoint(pos):
                    self.checkbox_checked = not self.checkbox_checked
                # Check if click is in the restore button; if so, restore defaults
                if self.restore_button_rect.collidepoint(pos):
                    self.restore_defaults()
            if event.type == pygame.KEYDOWN:
                # If the text field is active, update the size_text value
                if self.size_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.size_text = self.size_text[:-1]
                    else:
                        # Append the typed character
                        self.size_text += event.unicode

    def restore_defaults(self):
        """Restore all settings to default values."""
        self.size_text = "100"
        self.current_option = "Medium"  # You can choose a default option here
        self.checkbox_checked = False
        print("Settings restored to default")

    def draw(self):
        """Draw the settings menu_screens elements."""
        # Fill background with a dark color
        self.screen.fill((30, 30, 30))

        # --- Draw the Text Field for "Size" ---
        # Draw the label "Size:" to the left of the text field
        label_surface = self.font.render(self.size_label, True, (255, 255, 255))
        self.screen.blit(label_surface, (self.size_rect.x - 70, self.size_rect.y))
        # Draw the text field rectangle
        pygame.draw.rect(self.screen, (255, 255, 255), self.size_rect, 2)
        # Draw the current text inside the text field
        size_surface = self.font.render(self.size_text, True, (255, 255, 255))
        self.screen.blit(size_surface, (self.size_rect.x + 5, self.size_rect.y + 5))

        # --- Draw the Option Menu ---
        pygame.draw.rect(self.screen, (255, 255, 255), self.option_rect, 2)
        option_surface = self.font.render(self.current_option, True, (255, 255, 255))
        self.screen.blit(option_surface, (self.option_rect.x + 5, self.option_rect.y + 5))

        # --- Draw the Checkbox ---
        pygame.draw.rect(self.screen, (255, 255, 255), self.checkbox_rect, 2)
        if self.checkbox_checked:
            # If checked, draw an "X" or a filled rectangle inside the checkbox
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.checkbox_rect.x, self.checkbox_rect.y),
                             (self.checkbox_rect.x + self.checkbox_rect.width,
                              self.checkbox_rect.y + self.checkbox_rect.height), 2)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.checkbox_rect.x + self.checkbox_rect.width, self.checkbox_rect.y),
                             (self.checkbox_rect.x, self.checkbox_rect.y + self.checkbox_rect.height), 2)
        checkbox_label_surface = self.font.render(self.checkbox_label, True, (255, 255, 255))
        self.screen.blit(checkbox_label_surface, (self.checkbox_rect.x + 30, self.checkbox_rect.y))

        # --- Draw the Restore Button ---
        pygame.draw.rect(self.screen, (100, 100, 100), self.restore_button_rect)  # Button background
        pygame.draw.rect(self.screen, (255, 255, 255), self.restore_button_rect, 2)  # Button border
        restore_surface = self.font.render("Restore", True, (255, 255, 255))
        restore_rect = restore_surface.get_rect(center=self.restore_button_rect.center)
        self.screen.blit(restore_surface, restore_rect)

        # Update the display
        pygame.display.flip()

    def run(self):
        """Run the settings menu_screens loop."""
        running = True
        while running and self.active:
            events = pygame.event.get()
            self.handle_events(events)
            self.draw()
            self.clock.tick(30)  # Limit to 30 frames per second
