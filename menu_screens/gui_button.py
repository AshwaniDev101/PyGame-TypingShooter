import pygame
from config import utils

# Button appearance settings
BTN_PADDING_X = 15
BTN_HEIGHT = 30
BTN_ALPHA = 150
BTN_BORDER_RADIUS = 5

base_color=(50, 50, 50, BTN_ALPHA)
hover_color=(70, 70, 70, BTN_ALPHA)
border_color=(200, 200, 200)


class HintButton:
    def __init__(self, text, pos, font, width=None, can_hover=False):
        self.text = text  # Button label
        self.font = font  # Font for rendering text
        self.pos = pos  # Top-left position of the button
        self.width = width  # Fixed width if provided
        self.padding = BTN_PADDING_X if width is None else 0  # Padding for dynamic width buttons
        self.is_btn_can_hover = can_hover  # New variable to determine if hover effect is enabled
        self.hover = False  # Hover state flag
        self.create_surface()  # Create the button surface and rect

    def create_surface(self):
        # Render the text in white
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        # Calculate the width based on text size and padding if width is not fixed
        if self.width is None:
            text_width, _ = text_surf.get_size()
            width = text_width + self.padding * 2
        else:
            width = self.width
        # Create a transparent surface for the button
        self.surface = pygame.Surface((width, BTN_HEIGHT), pygame.SRCALPHA)
        # Create a rectangle for positioning and collision detection
        self.rect = pygame.Rect(self.pos[0], self.pos[1], width, BTN_HEIGHT)
        self.text_surf = text_surf  # Store the rendered text surface
        # Center the text on the button surface
        self.text_rect = text_surf.get_rect(center=(width // 2, BTN_HEIGHT // 2))

    def update_hover(self, mouse_pos):
        # Update the hover flag only if the button is hoverable
        if self.is_btn_can_hover:
            self.hover = self.rect.collidepoint(mouse_pos)
        else:
            self.hover = False

    def draw(self, screen):
        # Clear the button surface and set the colorkey to ensure transparency
        self.surface.fill((0, 0, 0, 0))
        self.surface.set_colorkey((0, 0, 0, 0))

        # Determine color: if hover is enabled and active, use hover_color; otherwise, use base_color
        color = hover_color if (self.is_btn_can_hover and self.hover) else base_color
        # Change border color to emphasize hover (or lack thereof)
        border = (255, 255, 255) if (self.is_btn_can_hover and self.hover) else (180, 180, 180)

        # Draw the button background with rounded corners
        pygame.draw.rect(self.surface, color, self.surface.get_rect(), border_radius=BTN_BORDER_RADIUS)
        # Draw the border around the button with rounded corners
        pygame.draw.rect(self.surface, border, self.surface.get_rect(), 2, border_radius=BTN_BORDER_RADIUS)
        # Blit the text onto the button surface
        self.surface.blit(self.text_surf, self.text_rect)
        # Blit the button surface onto the main screen at the button's position
        screen.blit(self.surface, self.rect.topleft)


class ColorfullyButton:
    def __init__(self, text, pos, font, width=None, height=None,
                 prefix_image_path=None, prefix_spacing=10, callback=None, max_width=None):
        self.text = text  # Button label text
        self.pos = pos  # Top-left position of the button
        self.font = font  # Font used for rendering text
        self.width = width  # Optional fixed width; if None, calculated dynamically
        self.height = height if height is not None else BTN_HEIGHT  # Provided height or default
        self.prefix_spacing = prefix_spacing  # Spacing between prefix image and text
        self.callback = callback  # Callback function (if needed)
        self.max_width = max_width  # Maximum allowed width for the button
        # Load and scale the prefix image if a path is provided; else None.
        self.prefix_image = utils.loader_scale_image(prefix_image_path, target_height=20) if prefix_image_path else None
        self.base_color = (200, 0, 0, 255)  # Base red color
        self.hover_color = (255, 0, 0, 255)  # Lighter red when hovered
        self.border_color = (255, 255, 255)  # White border for contrast
        self.hover = False  # Hover state flag
        self.create_surface()  # Build the composite and main button surface

    def create_surface(self):
        # Render the text in white.
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        # If a prefix image is provided, composite it with the text side by side.
        if self.prefix_image is not None:
            prefix_surf = self.prefix_image
            composite_width = prefix_surf.get_width() + self.prefix_spacing + text_surf.get_width()
            composite_height = max(prefix_surf.get_height(), text_surf.get_height())
            composite_surf = pygame.Surface((composite_width, composite_height), pygame.SRCALPHA)
            # Blit the prefix image on the left, centered vertically.
            composite_surf.blit(prefix_surf, (0, (composite_height - prefix_surf.get_height()) // 2))
            # Blit the text to the right of the prefix image.
            composite_surf.blit(text_surf, (prefix_surf.get_width() + self.prefix_spacing,
                                            (composite_height - text_surf.get_height()) // 2))
        else:
            composite_surf = text_surf
            composite_width, composite_height = text_surf.get_size()

        # If no fixed width is provided, calculate width based on composite plus padding.
        if self.width is None:
            computed_width = composite_width + 2 * BTN_PADDING_X
            # If a maximum width is provided and computed width exceeds it, scale the composite down.
            if self.max_width is not None and computed_width > self.max_width:
                self.width = self.max_width
                available_width = self.width - 2 * BTN_PADDING_X
                scale_factor = available_width / composite_width
                new_composite_width = int(composite_width * scale_factor)
                new_composite_height = int(composite_height * scale_factor)
                composite_surf = pygame.transform.smoothscale(composite_surf,
                                                              (new_composite_width, new_composite_height))
            else:
                self.width = computed_width
        # If a fixed width was provided, use that.

        self.composite_surf = composite_surf
        # Create a transparent surface for the button with the final width and height.
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Create a rectangle for positioning and collision detection.
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        # Center the composite (prefix image + text) on the button surface.
        self.text_rect = self.composite_surf.get_rect(center=(self.width // 2, self.height // 2))

    def update_hover(self, mouse_pos):
        # Update the hover flag based on whether the mouse is within the button's rect.
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        # Choose the hover color if hovered; otherwise, use the base color.
        color = self.hover_color if self.hover else self.base_color
        self.surface.fill((0, 0, 0, 0))  # Clear previous drawing with transparency.
        # Draw the button background with rounded corners.
        pygame.draw.rect(self.surface, color, self.surface.get_rect(), border_radius=8)
        # Draw a white border around the button (thickness=3).
        pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), 3, border_radius=8)
        # Blit the composite (prefix image + text) onto the button's surface.
        self.surface.blit(self.composite_surf, self.text_rect)
        # Finally, blit the button surface onto the main screen at its designated position.
        screen.blit(self.surface, self.rect.topleft)

    def handle_event(self, event):
        # On mouse button down within the button area, call the callback (if provided).
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if callable(self.callback):
                self.callback(self.text)

