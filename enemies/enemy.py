import string
from enum import Enum
import pygame
import math
import random
from config import utils, constants
from config.loader import Loader


# class DropType(Enum):
#     NONE = 0
#     HEALTH = 1
#     AMMO = 2
#     POWERUP = 3

# === Enemy Base Class (Mother Class) === #
class Enemy:
    def __init__(self, player):

        # Basic init
        self.player = player
        self.selected = False


        # Core attributes
        # self.image = pygame.image.load("assets/images/alien_ships/alien_ship_0.png").convert_alpha()
        self.image = Loader.load_image("assets/images/alien_ships/alien_ship_0.png")
        self.rect = self.image.get_rect(center=(200, 200))
        # self.font = pygame.font.Font("assets/fonts/Righteous-Regular.ttf", 21)
        self.font = Loader.load_font("assets/fonts/Righteous-Regular.ttf", 21)
        self.word = utils.generate_random_word(4,8)  # Default word if not provided
        self.hit_count = max(len(self.word), 1)  # Hit count based on word length
        self.set_position(height=50)  # Set the initial position on the screen

        # Behavioral attributes
        self.drop_count = 0

        # Pushback effect attributes
        self.velocity_x = 0  # Velocity in x-direction
        self.velocity_y = 0  # Velocity in y-direction
        self.friction = 5 # Friction for gradual stop

        # Movement attributes
        self.original_speed = 1.5  # Store original speed
        self.speed = self.original_speed
        self.entry_speed = self.original_speed * 10  # Hyper-speed entry

        self.jet_effect = []  # List to store previous positions
        self.jet_effect_length = 10  # Adjust for a longer or shorter trail




    # === Set initial position on screen === #
    def set_position(self, height):
        text_width, _ = self.font.size(self.word)  # Get text width for positioning
        max_x = constants.SCREEN_WIDTH - text_width - 20  # Max X within screen bounds
        self.rect.x = random.randint(20, max_x)  # Random X position within the screen
        self.rect.y = -self.rect.height - height  # Spawn just above the screen

    def move(self, game_over):
        """Handles enemy movement and stores previous positions for trail effect."""

        # Save the current position for trail effect
        self.jet_effect.append(self.rect.center)

        # Limit the trail length to avoid excessive memory usage
        if len(self.jet_effect) > self.jet_effect_length:
            self.jet_effect.pop(0)

        self.move_handle_pushback()  # Handle pushback if hit

        # === If game is over, move straight down ===
        if game_over:
            self.rect.y += self.speed * 2  # Keep moving downward
            return

        # === Phase 1: Hyperspeed Entry (Fast Drop Until y = 200) ===
        if self.rect.y < 200:
            self.rect.y += self.entry_speed  # Move downward quickly
            self.entry_speed *= 0.92  # Smooth deceleration effect
            return  # Skip other phases until y = 200 is reached





    # === Draw the enemy on the screen === #
    def draw(self, screen):
        """Draws the enemy and its trail effect on the screen."""

        # Draw the trail effect (fade-out effect)
        for i, pos in enumerate(self.jet_effect):
            alpha = int(255 * (i / len(self.jet_effect)))  # Create a fading effect
            trail_surface = self.image.copy()
            trail_surface.set_alpha(alpha)  # Apply transparency
            screen.blit(trail_surface, (pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2))

        # Draw the enemy's main sprite
        screen.blit(self.image, self.rect.topleft)

        # Draw the enemy's word
        self.draw_word(screen)

    # === Draw the enemy's word on the screen === #
    def draw_word(self, screen):
        if self.word:
            first_letter_surface = self.font.render(self.word[0], True, (utils.color("FF0002")))  # Red for the first letter
            remaining_surface = self.font.render(self.word[1:], True, (255, 255, 255))  # White for remaining text

            total_text_width = first_letter_surface.get_width() + remaining_surface.get_width()

            # Set initial text position based on the enemy rectangle
            text_x = self.rect.right
            text_y = self.rect.bottom

            # === Prevent text overflow off-screen === #
            if text_x + total_text_width > constants.SCREEN_WIDTH:
                text_x = constants.SCREEN_WIDTH - total_text_width - 10  # Adjust position if text exceeds right bound
            elif text_x < 0:
                text_x = 10  # Adjust position if text exceeds left bound

            # Draw selection circle if the enemy is selected
            if self.selected:
                pygame.draw.circle(screen, (0, 255, 0), (text_x - 10, text_y + 15), 5)

            # Render text surfaces on the screen
            screen.blit(first_letter_surface, (text_x, text_y))
            screen.blit(remaining_surface, (text_x + first_letter_surface.get_width(), text_y))

    # === Remove the first letter from the enemy's word === #
    def remove_letter(self):
        if self.word:
            self.word = self.word[1:]  # Remove the first letter from the word

    # === Reduce the hit count of the enemy === #
    def reduce_hit_count(self):
        self.hit_count -= 1  # Decrement the enemy's hit count

    # === Check if the enemy is defeated (no letters left) === #
    def is_defeated(self):
        return self.word == ""  # Enemy is defeated when the word is empty


    def apply_pushback(self, bullet, force=5):
        dx = self.rect.centerx - bullet.rect.centerx  # X distance from bullet
        dy = self.rect.centery - bullet.rect.centery  # Y distance from bullet
        distance = math.hypot(dx, dy)  # Distance calculation
        if distance > 0:
            dx /= distance  # Normalize
            dy /= distance  # Normalize
        self.velocity_x = dx * force  # Apply force in x-direction
        self.velocity_y = dy * force  # Apply force in y-direction

    def move_handle_pushback(self):
        # Clamp friction between 0 and 100
        self.friction = max(0, min(self.friction, 100))

        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y

            # If friction is 100, stop movement instantly
            if self.friction == 100:
                self.velocity_x = 0
                self.velocity_y = 0
            else:
                # For any other friction, apply smooth resistance
                friction_multiplier = 1 + (self.friction / 10)
                self.velocity_x /= friction_multiplier
                self.velocity_y /= friction_multiplier
        else:
            self.velocity_x = 0
            self.velocity_y = 0



    # # === Rotation logic separated from move === #
    # def rotate_towards_player(self):
    #     dx = self.player.rect.centerx - self.rect.centerx  # X difference
    #     dy = self.player.rect.centery - self.rect.centery  # Y difference
    #     self.angle = math.degrees(math.atan2(-dy, dx)) + 90  # Calculate angle and adjust
    #     return pygame.transform.rotate(self.image, self.angle)  # Return rotated image
    #
    # # === Draw the enemy on the screen === #
    # def draw(self, screen):
    #     rotated_image = self.rotate_towards_player()  # Call rotation method
    #     new_rect = rotated_image.get_rect(center=self.rect.center)  # Center the rotated image
    #     screen.blit(rotated_image, new_rect.topleft)  # Draw the enemy image
    #     self.draw_word(screen)  # Draw the associated word below the enemy
