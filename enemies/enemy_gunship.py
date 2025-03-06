import random
import math
import pygame

from config import constants
from config.loader import Loader
from enemies.enemy import Enemy
# Note: Removed EnemyBullet and bullet_manager references


class EnemyGunship(Enemy):
    def __init__(self, player, enemy_list):
        super().__init__(player)
        # Load the enemy gunship image using Loader
        self.image = Loader.load_image("assets/images/alien_ships/alien_ship_0.png")
        # Start off-screen (centered at X=400; adjust as needed)
        self.rect = self.image.get_rect(center=(400, 0))

        # === We need this to follow player's movements ===
        self.player_x_history = []  # Store past x-positions of the player
        self.delay_frames = 20  # How many frames behind the enemy follows

        self.oscillation_range = 100  # How far it moves left and right
        self.oscillation_speed = 0.04  # Controls oscillation speed (lower = slower)
        self.oscillation_offset = 0  # Keeps track of wave motion
        self.follow_speed = 0.05  # Controls how fast it follows the player

        # Just jet effect
        self.is_show_flame_effect = True  # Flag to show flame effect during fall
        self.fall_speed = 10  # Initial fast drop; speed becomes normal later
        self.jet_effect = []  # Store positions for jet trail effect
        self.jet_effect_length = 15  # Number of trail points to display
        self.stop_at = 50  # Stop moving down at this Y position

        # Removed bullet_manager and shooting timers;
        # Store reference to the main enemy list to add shells directly
        self.enemy_list = enemy_list

    # Removed the 'shoot' method since we're replacing it with shell spawning

    def move(self, game_over):
        """ Move the enemy downward, then follow a delayed version of the player's x-position. """
        # === If game is over, move straight down ===
        if game_over:
            self.rect.y -= 5  # Continue moving downward
            return

        # === Gunship movements ========================
        if self.rect.y < self.stop_at:
            self.rect.y += self.fall_speed
            self.fall_speed *= 0.9  # Slow down gradually (reduce y-speed by 10% each frame)

            # If the enemy gets pushed back up after stopping due to player pushback, restart fall gently
            if self.fall_speed < 0.5:  # If speed is almost zero
                self.fall_speed = 2  # Give it a small push downward
        else:
            self.is_show_flame_effect = False
            # Store player's x-position history for delayed following
            self.player_x_history.append(self.player.rect.centerx)
            if len(self.player_x_history) > self.delay_frames:
                delayed_x = self.player_x_history.pop(0)  # Get the oldest x-position
            else:
                delayed_x = self.player.rect.centerx  # Fallback if not enough data

            # Oscillation logic for horizontal movement
            self.oscillation_offset += self.oscillation_speed
            oscillation = math.sin(self.oscillation_offset) * self.oscillation_range

            # Smoothly follow the delayed x-position plus oscillation
            target_x = delayed_x + oscillation
            self.rect.x += (target_x - self.rect.x) * self.follow_speed

            # Prevent going off-screen horizontally
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > constants.SCREEN_WIDTH:  # Assuming screen width is 800
                self.rect.right = constants.SCREEN_WIDTH

            # === Spawn shell logic for Gunship ===
            # Once the gunship has finished falling (flame effect off), attempt to fire a shell.
            if self.should_fire():
                new_shell = self.spawn_shell()
                self.enemy_list.append(new_shell)

        # Store jet trail positions only when moving downward
        if self.rect.y < self.stop_at:
            self.jet_effect.append((self.rect.centerx, self.rect.centery))
            if len(self.jet_effect) > self.jet_effect_length:
                self.jet_effect.pop(0)  # Keep the trail length fixed

        # Handle pushback if hit (assumed to be implemented in the parent or elsewhere)
        self.move_handle_pushback()

    def spawn_shell(self):
        """Spawn a new shell at the gunship's current position."""
        from enemies.enemy_shell import EnemyShell  # Import here if not already imported at top
        return EnemyShell(self.player, self)

    def should_fire(self):
        """Determine if the gunship should fire a shell.
           Using a random chance for demonstration purposes."""
        return random.random() < 0.01  # Adjust probability as needed

    def draw(self, screen):
        """ Draw the enemy and its trail effect. """
        if self.is_show_flame_effect:
            for i, pos in enumerate(self.jet_effect):
                alpha = int(255 * (i / len(self.jet_effect)))  # Create a fade effect for the trail
                trail_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (0, 255, 255, alpha), (5, 5), 5)
                screen.blit(trail_surface, (pos[0] - 5, pos[1] - 5))

        # Draw the enemy gunship image at its current position
        screen.blit(self.image, self.rect.topleft)
        # Draw the enemy's associated word (using the parent's method)
        self.draw_word(screen)


# import random
#
# from config import constants
# from config.loader import Loader
# from enemies.enemy import Enemy
# import pygame
# import math
#
#
# from shooting.enemy_bullet import EnemyBullet
#
#
# class EnemyGunship(Enemy):
#     def __init__(self, player, bullet_manager):
#         super().__init__(player)
#
#         # self.image = pygame.image.load("assets/images/alien_ships/alien_ship_0.png").convert_alpha()
#         self.image = Loader.load_image("assets/images/alien_ships/alien_ship_0.png")
#         self.rect = self.image.get_rect(center=(400, 0))  # Start off-screen
#
#         # === We need this to follow players movements
#         self.player_x_history = []  # Store past x-positions of the player
#         self.delay_frames = 20  # How many frames behind the enemy follows
#
#         self.oscillation_range = 100  # How far it moves left and right
#         self.oscillation_speed = 0.04  # Controls oscillation speed (lower = slower)
#         self.oscillation_offset = 0  # Keeps track of wave motion
#         self.follow_speed = 0.05  # Controls how fast it follows player
#
#         # Just jet effect
#         self.is_show_flame_effect = True # is is to
#         self.fall_speed = 10  # Initial fast drop, Speed become normal later
#         self.jet_effect = []  # Store positions for effect
#         self.jet_effect_length = 15  # Number of trail points
#         self.stop_at = 50  # Stop moving down at this position
#
#         self.bullet_manager = bullet_manager
#         self.last_shot_time = pygame.time.get_ticks()
#         self.shoot_interval = random.randint(1000, 3000)  # Random interval between shots
#
#
#     def shoot(self):
#         now = pygame.time.get_ticks()
#         if now - self.last_shot_time > self.shoot_interval:
#             firing_point = (self.rect.centerx, self.rect.bottom)
#             enemy_bullet = EnemyBullet(firing_point, target=None)
#             self.bullet_manager.enemy_bullets.append(enemy_bullet)
#             self.last_shot_time = now
#
#     def move(self, game_over):
#         """ Move the enemy downward, then follow a delayed version of the player's x-position. """
#         # === If game is over, move straight down ===
#         if game_over:
#             self.rect.y -= 5 # Keep moving downward
#             return
#
#         # === Gun ship movements ========================
#         if self.rect.y < self.stop_at:
#             self.rect.y += self.fall_speed
#             self.fall_speed *= 0.9  # Slow down gradually each frame y-speed reduce by 90% till it become 0
#
#             # If the enemy gets pushed back up after stopping due to player push back effect, restart fall gently
#             if self.fall_speed < 0.5:  # If speed is almost zero
#                 self.fall_speed = 2  # Give it a small push downward
#
#
#         else:
#
#             self.is_show_flame_effect = False
#             # Store player's x-position history
#             self.player_x_history.append(self.player.rect.centerx)
#             if len(self.player_x_history) > self.delay_frames:
#                 delayed_x = self.player_x_history.pop(0)  # Get older x-pos
#             else:
#                 delayed_x = self.player.rect.centerx  # Fallback if not enough data
#
#             # Oscillation logic
#             self.oscillation_offset += self.oscillation_speed
#             oscillation = math.sin(self.oscillation_offset) * self.oscillation_range
#
#             # Smoothly follow the delayed x-position
#             target_x = delayed_x + oscillation
#             self.rect.x += (target_x - self.rect.x) * self.follow_speed
#
#             # Prevent going off-screen
#             if self.rect.left < 0:
#                 self.rect.left = 0
#             if self.rect.right > constants.SCREEN_WIDTH:  # Assuming screen width is 800
#                 self.rect.right = constants.SCREEN_WIDTH
#
#         # Store trail positions only when moving downward
#         if self.rect.y < self.stop_at:
#             self.jet_effect.append((self.rect.centerx, self.rect.centery))
#             if len(self.jet_effect) > self.jet_effect_length:
#                 self.jet_effect.pop(0)  # Keep trail length fixed
#
#         # Handle pushback if hit
#         self.move_handle_pushback()
#
#     def draw(self, screen):
#         """ Draw the enemy and its trail effect. """
#         if self.is_show_flame_effect:
#             for i, pos in enumerate(self.jet_effect):
#                 alpha = int(255 * (i / len(self.jet_effect)))  # Fade effect
#                 trail_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
#                 pygame.draw.circle(trail_surface, (0, 255, 255, alpha), (5, 5), 5)
#                 screen.blit(trail_surface, (pos[0] - 5, pos[1] - 5))
#
#         screen.blit(self.image, self.rect.topleft)
#         # Draw the enemy's word
#         self.draw_word(screen)
