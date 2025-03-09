import pygame

from config import constants

import pygame

from config.loader import Loader


class UpgradeButton:
    def __init__(self,screen, x, y, image_path):

        self.screen = screen
        self.image = Loader.load_image(image_path)
        self.image = pygame.transform.smoothscale(self.image, (50, 50))  # Resize to 50x50
        self.lock_image = Loader.load_image("assets/images/upgrades/upgrade_lock.png")
        self.lock_image = pygame.transform.smoothscale(self.lock_image, (50, 50))  # Same size

        self.rect = self.image.get_rect(center=(x, y))
        self.is_locked = True  # Default state

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self):
        self.screen.blit(self.image, self.rect.topleft)

        if self.is_locked:
            self.screen.blit(self.lock_image, self.rect.topleft)  # Draw lock image on top

        if self.is_hovered(pygame.mouse.get_pos()):
            pygame.draw.circle(self.screen, (255, 255, 255), self.rect.center, 30, 2)  # Hover effect

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(event.pos) and not self.is_locked:
            print("Button pressed")


class UpgradeWindow:
    def __init__(self, screen):
        self.screen = screen
        self.width = 500
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2

        self.active = False  # Start with the pop-up hidden

        self.button = UpgradeButton(screen, 500, 500, "assets/images/upgrades/basic_gun.png")

    def toggle(self):
        self.active = not self.active  # Open/close the window

    def active(self,active):
        self.active = active

    def draw(self):


        if self.active:
            # Draw the outer rectangle (Black with white border)
            self.draw_centered_rectangles()

            self.button.draw()



            # self.screen.blit(self.image, (self.x, self.y))

    def draw_centered_rectangles(self):
        # Define colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)

        # Define rectangle sizes
        OUTER_RECT_SIZE = (500, 500)
        INNER_RECT_SIZE = (150, 150)
        BORDER_THICKNESS_OUTER = 5
        BORDER_THICKNESS_INNER = 2
        RADIUS = 5  # Rounded corners


        # Calculate center positions
        outer_x = (constants.SCREEN_WIDTH - OUTER_RECT_SIZE[0]) // 2
        outer_y = (constants.SCREEN_HEIGHT - OUTER_RECT_SIZE[1]) // 2

        inner_x = outer_x + (OUTER_RECT_SIZE[0] - INNER_RECT_SIZE[0]) // 2
        inner_y = outer_y + (OUTER_RECT_SIZE[1] - INNER_RECT_SIZE[1]) // 2

        # Draw outer rectangle with border
        pygame.draw.rect(self.screen, WHITE, (outer_x - BORDER_THICKNESS_OUTER // 2, outer_y - BORDER_THICKNESS_OUTER // 2,
                                         OUTER_RECT_SIZE[0] + BORDER_THICKNESS_OUTER,
                                         OUTER_RECT_SIZE[1] + BORDER_THICKNESS_OUTER),
                         border_radius=RADIUS)  # Border
        pygame.draw.rect(self.screen, BLACK, (outer_x, outer_y, OUTER_RECT_SIZE[0], OUTER_RECT_SIZE[1]),
                         border_radius=RADIUS)  # Fill

        # Draw inner rectangle with border only
        pygame.draw.rect(self.screen, WHITE, (inner_x - BORDER_THICKNESS_INNER // 2, inner_y - BORDER_THICKNESS_INNER // 2,
                                         INNER_RECT_SIZE[0] + BORDER_THICKNESS_INNER,
                                         INNER_RECT_SIZE[1] + BORDER_THICKNESS_INNER),
                         BORDER_THICKNESS_INNER, border_radius=RADIUS)
