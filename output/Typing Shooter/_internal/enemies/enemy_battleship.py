import pygame
import math
import random

from config import utils
from config.loader import Loader
from enemies.enemy import Enemy
from enemies.enemy_shell import EnemyShell
from enemies.enemy_sucide_drone import EnemySuicideDrone


class EnemyBattleship(Enemy):
    def __init__(self, player, enemy_list):
        super().__init__(player)  # Initialize using Enemy class
        # Load the battleship image using Loader
        self.image = Loader.load_image("assets/images/battleships/battleship_0.png")
        # Set a random starting X position and off-screen Y position
        self.rect = self.image.get_rect(center=(random.randint(100, 700), -50))
        self.speed = 2  # Movement speed
        self.entry_done = False  # Track entry completion
        self.direction = random.choice([-1, 1])  # Random start direction (left or right)
        self.jet_effect_length = 5  # Adjust jet effect length for smoother trail
        self.word = utils.generate_random_word(15,20)

        # Store reference to the main enemy list (passed from main game)
        self.enemy_list = enemy_list

        # List to store previous positions for jet trail effect
        self.jet_effect = []

    def move(self, game_over):
        """Handles Battleship movement: Entry, Shell & Drone Spawning, and Horizontal Patrol"""

        # Store previous positions for jet effect
        self.jet_effect.append(self.rect.center)
        if len(self.jet_effect) > self.jet_effect_length:
            self.jet_effect.pop(0)

        # === If game is over, move straight down ===
        if game_over:
            self.rect.y += self.speed * 2  # Fall downward
            return

        # === Entry Phase: Move Down With Jet Trail ===
        if not self.entry_done:
            if self.rect.y < 50:  # Continue moving down until reaching Y = 50
                self.rect.y += self.speed * 3  # Move downward quickly
            else:
                self.entry_done = True  # Entry complete; start normal movement
            return  # Prevent further movement during entry phase

        # === Spawn Shell and Suicide Drone after entry ===
        # Spawn a shell with a random horizontal drift.
        if self.entry_done and self.should_fire():
            new_shell = self.spawn_shell()
            self.enemy_list.append(new_shell)
        # Spawn a suicide drone at the battleship's position.
        if self.entry_done and self.should_spawn_drone():
            new_drone = self.spawn_suicide_drone()
            self.enemy_list.append(new_drone)

        # === After Entry: Move Left-Right Horizontally ===
        self.rect.x += self.speed * self.direction

        # Reverse direction at screen edges.
        if self.rect.right >= 800:
            self.direction = -1
        elif self.rect.left <= 0:
            self.direction = 1

    def draw(self, screen):
        """
        Draws the battleship and its jet effect:
        - Jet effect is active during hyperspeed entry.
        - Draws the battleship image and its associated word.
        """
        if not self.entry_done:
            for i, pos in enumerate(self.jet_effect):
                alpha = int(255 * (i / len(self.jet_effect)))  # Create a fading effect for the trail
                trail_surface = self.image.copy()
                trail_surface.set_alpha(alpha)
                screen.blit(trail_surface, (int(pos[0] - self.rect.width / 2), int(pos[1] - self.rect.height / 2)))
        # Draw the battleship image at its current position
        screen.blit(self.image, self.rect.topleft)
        # Draw the associated word (using method from the parent class)
        self.draw_word(screen)

    def spawn_shell(self):
        """
        Create a new shell at the battleship's position.
        The shell will have a random horizontal drift.
        """
        return EnemyShell(self.player, self, horizontal_speed=random.choice([-2, -1, 0, 1, 2]))

    def should_fire(self):
        """
        Determine if the battleship should fire a shell.
        For demonstration purposes, we use a random chance.
        """
        return random.random() < 0.01  # Adjust probability as needed

    def spawn_suicide_drone(self):
        """
        Create a new suicide drone at the battleship's position.
        After instantiation, override its position to match the battleship's center.
        """
        new_drone = EnemySuicideDrone(self.player)
        new_drone.rect.center = self.rect.center  # Set the drone's position to the battleship's center
        return new_drone

    def should_spawn_drone(self):
        """
        Determine if the battleship should spawn a suicide drone.
        For demonstration purposes, we use a random chance.
        """
        return random.random() < 0.005  # Adjust probability as needed
