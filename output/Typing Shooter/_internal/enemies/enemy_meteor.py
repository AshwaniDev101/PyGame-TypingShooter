import pygame
from config import constants
import math
import random
from enemies.enemy import Enemy
from config.loader import Loader


def load_words():
    txt_path = Loader.resource_path("config/meteor_names.txt")
    with open(txt_path, "r", encoding="utf-8") as file:
        words = [word for line in file for word in line.strip().split()]
    random.shuffle(words)
    return words


# ENEMY_METEOR CLASS (CHILD OF ENEMY)
class EnemyMeteor(Enemy):
    WORD_LIST = load_words()  # Global word list for all EnemyMeteor instances
    word_index = 0  # Shared index to iterate through WORD_LIST

    def __init__(self, player, target_player=False):
        super().__init__(player)  # Call the base class constructor

        self.is_target_player = target_player

        # Set a random speed for the meteor
        self.speed = random.uniform(1.5, 3.5)
        self.rotate = 0  # Initial rotation angle

        self.rotate_direction = random.choice([-1, 1])

        # Assign a word from the global WORD_LIST to this meteor
        if EnemyMeteor.word_index < len(EnemyMeteor.WORD_LIST):
            self.word = EnemyMeteor.WORD_LIST[EnemyMeteor.word_index][:15]  # Limit word length
            EnemyMeteor.word_index += 1
        else:
            EnemyMeteor.word_index = 0  # Reset index when list is exhausted
            self.word = EnemyMeteor.WORD_LIST[EnemyMeteor.word_index][:15]

        # Set ammo drop count based on word length
        self.drop_count = random.randint(len(self.word), len(self.word) + 10)

        # Load and set meteor image
        rand_num = random.randint(0, 19)
        # self.original_image = pygame.image.load(f"assets/images/meteors/meteor_{rand_num}.png").convert_alpha()
        self.original_image = Loader.load_image(f"assets/images/meteors/meteor_{rand_num}.png")
        self.image = self.original_image


        # Set up the collision rectangle and spawn position
        # self.rect = pygame.Rect(0, 0, 40, 40)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, constants.SCREEN_WIDTH - 50)
        self.rect.y = -150


        # Calculate falling direction using a random angle
        angle = random.uniform(-30, 30)  # Angle range for diagonal movement
        radians = math.radians(angle)
        self.dx = math.sin(radians) * self.speed
        self.dy = math.cos(radians) * self.speed


    # this move follow the player
    # def move(self, game_over):
    #     if game_over:
    #         self.rect.y += self.speed
    #         return
    #
    #     self.move_handle_pushback()  # Apply any pushback
    #
    #     if self.is_target_player:
    #         # Recalculate direction toward the player every frame.
    #         player_x, player_y = self.player.rect.center
    #         meteor_x, meteor_y = self.rect.center
    #         angle = math.atan2(player_y - meteor_y, player_x - meteor_x)
    #         self.dx = math.cos(angle) * self.speed
    #         self.dy = math.sin(angle) * self.speed
    #
    #     self.rect.x += self.dx  # Update horizontal position
    #     self.rect.y += self.dy  # Update vertical position
    #     self.rotate += self.rotate_direction  # Update rotation for visual effect

    def move(self, game_over):
        if game_over:
            self.rect.y += self.speed  # Continue moving downwards if the game is over
            return

        self.move_handle_pushback()  # Apply any pushback if needed

        # While the meteor is above y=100, update its direction toward the player's current position.
        if self.rect.y < 50:
            player_x, player_y = self.player.rect.center
            meteor_x, meteor_y = self.rect.center
            angle = math.atan2(player_y - meteor_y, player_x - meteor_x)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed

        # Continue moving along the current direction.
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.rotate += self.rotate_direction  # Update rotation for visual effect

    # Override move methods
    # def move(self, game_over):
    #
    #
    #     if game_over:
    #         self.rect.y += self.speed   # Keep moving downward
    #         return
    #
    #     self.move_handle_pushback()  # Apply pushback if any
    #     self.rect.x += self.dx  # Move meteor along the x-axis
    #     self.rect.y += self.dy  # Move meteor along the y-axis
    #     self.rotate += self.rotate_direction   # Increase rotation angle for visual effect

    # Override draw methods
    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.rotate)  # Rotate the meteor image
        rect = rotated_image.get_rect(center=self.rect.center)  # Center the rotated image
        screen.blit(rotated_image, rect.topleft)  # Draw the meteor on the screen
        self.draw_word(screen)  # Draw the associated word below the meteor
