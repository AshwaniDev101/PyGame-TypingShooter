#
# #Old code test
# import pygame
# from config import constants
# import math
# import random
# from enemies.enemy import Enemy
# from config.loader import Loader
#
#
# def load_words():
#     txt_path = Loader.resource_path("config/meteor_names.txt")
#     with open(txt_path, "r", encoding="utf-8") as file:
#         words = [word for line in file for word in line.strip().split()]
#     random.shuffle(words)
#     return words
#
#
# # ENEMY_METEOR CLASS (CHILD OF ENEMY)
# class EnemyMeteor(Enemy):
#     WORD_LIST = load_words()  # Global word list for all EnemyMeteor instances
#     word_index = 0  # Shared index to iterate through WORD_LIST
#
#     def __init__(self, player, target_player=False):
#         super().__init__(player)  # Call the base class constructor
#
#         self.is_target_player = target_player
#
#         # Set a random speed for the meteor
#         self.speed = random.uniform(1.5, 3.5)
#         self.rotate = 0  # Initial rotation angle
#
#         self.rotate_direction = random.choice([-1, 1])
#
#         # Assign a word from the global WORD_LIST to this meteor
#         if EnemyMeteor.word_index < len(EnemyMeteor.WORD_LIST):
#             self.word = EnemyMeteor.WORD_LIST[EnemyMeteor.word_index][:15]  # Limit word length
#             EnemyMeteor.word_index += 1
#         else:
#             EnemyMeteor.word_index = 0  # Reset index when list is exhausted
#             self.word = EnemyMeteor.WORD_LIST[EnemyMeteor.word_index][:15]
#
#         # Set ammo drop count based on word length
#         self.drop_count = random.randint(len(self.word), len(self.word) + 10)
#
#         # Load and set meteor image
#         rand_num = random.randint(0, 9)
#         rand_binary = random.randint(0, 1) #this for selecting meteor color type, 1 for white and 0 for brown
#         # self.original_image = pygame.image.load(f"assets/images/meteors/meteor_{rand_num}.png").convert_alpha()
#         self.original_image = Loader.load_image(f"assets/images/meteors/meteor_{rand_binary}_{rand_num}.png")
#         self.image = self.original_image
#
#
#         # Set up the collision rectangle and spawn position
#         # self.rect = pygame.Rect(0, 0, 40, 40)
#
#         self.rect = self.image.get_rect()
#         self.rect.x = random.randint(50, constants.SCREEN_WIDTH - 50)
#         self.rect.y = -150
#
#
#         # Calculate falling direction using a random angle
#         angle = random.uniform(-30, 30)  # Angle range for diagonal movement
#         radians = math.radians(angle)
#         self.dx = math.sin(radians) * self.speed
#         self.dy = math.cos(radians) * self.speed
#
#
#     # this move follow the player
#     # def move(self, game_over):
#     #     if game_over:
#     #         self.rect.y += self.speed
#     #         return
#     #
#     #     self.move_handle_pushback()  # Apply any pushback
#     #
#     #     if self.is_target_player:
#     #         # Recalculate direction toward the player every frame.
#     #         player_x, player_y = self.player.rect.center
#     #         meteor_x, meteor_y = self.rect.center
#     #         angle = math.atan2(player_y - meteor_y, player_x - meteor_x)
#     #         self.dx = math.cos(angle) * self.speed
#     #         self.dy = math.sin(angle) * self.speed
#     #
#     #     self.rect.x += self.dx  # Update horizontal position
#     #     self.rect.y += self.dy  # Update vertical position
#     #     self.rotate += self.rotate_direction  # Update rotation for visual effect
#
#     def move(self, game_over):
#         if game_over:
#             self.rect.y += self.speed  # Continue moving downwards if the game is over
#             return
#
#         self.move_handle_pushback()  # Apply any pushback if needed
#
#         # While the meteor is above y=100, update its direction toward the player's current position.
#         if self.rect.y < 50:
#             player_x, player_y = self.player.rect.center
#             meteor_x, meteor_y = self.rect.center
#             angle = math.atan2(player_y - meteor_y, player_x - meteor_x)
#             self.dx = math.cos(angle) * self.speed
#             self.dy = math.sin(angle) * self.speed
#
#         # Continue moving along the current direction.
#         self.rect.x += self.dx
#         self.rect.y += self.dy
#         self.rotate += self.rotate_direction  # Update rotation for visual effect
#
#     # Override move methods
#     # def move(self, game_over):
#     #
#     #
#     #     if game_over:
#     #         self.rect.y += self.speed   # Keep moving downward
#     #         return
#     #
#     #     self.move_handle_pushback()  # Apply pushback if any
#     #     self.rect.x += self.dx  # Move meteor along the x-axis
#     #     self.rect.y += self.dy  # Move meteor along the y-axis
#     #     self.rotate += self.rotate_direction   # Increase rotation angle for visual effect
#
#     # Override draw methods
#     def draw(self, screen):
#         rotated_image = pygame.transform.rotate(self.image, self.rotate)  # Rotate the meteor image
#         rect = rotated_image.get_rect(center=self.rect.center)  # Center the rotated image
#         screen.blit(rotated_image, rect.topleft)  # Draw the meteor on the screen
#         self.draw_word(screen)  # Draw the associated word below the meteor
#






import pygame
import math
import random
from typing import ClassVar, Optional, List

from config import constants
from enemies.enemy import Enemy
from config.loader import Loader


def load_words() -> List[str]:
    """Loads words from the text file, shuffles them, and returns the list."""
    txt_path = Loader.resource_path("config/meteor_names.txt")
    with open(txt_path, "r", encoding="utf-8") as file:
        words = [word for line in file for word in line.strip().split()]
    random.shuffle(words)
    return words


class EnemyMeteor(Enemy):
    """
    Optimized falling meteor enemy with:
    - Efficient pre-rotated cached sprites (default)
    - Option to fall back to real-time rotation for testing/performance comparison
    - Size-based speed and rotation scaling
    - Brief optional homing toward player
    """

    # Tunable constants
    EDGE_OFFSET: int = 50
    SPAWN_Y_OFFSET: int = -150
    HOMING_THRESHOLD_Y: int = 50
    INITIAL_ANGLE_RANGE: tuple[float, float] = (-30.0, 30.0)
    SPEED_MIN: float = 1.2
    SPEED_MAX: float = 2.5
    SIZE_FACTOR_MULTIPLIER: float = 0.08
    ROTATION_MIN_SPEED: float = 0.3
    ROTATION_BASE_SPEED: float = 2.0
    ROTATION_SPEED_DECREMENT: float = 0.18
    ROTATION_STEP: int = 2                # Balanced smoothness vs memory (180 images per variant)
    WORD_MAX_LEN: int = 15

    # Performance toggle - set to True to use old real-time rotation method
    USE_REALTIME_ROTATION: bool = False

    # Shared class-level caches (only used when pre-caching is active)
    _ROTATION_CACHES: ClassVar[dict[tuple[int, int], List[pygame.Surface]]] = {}
    _BASE_IMAGES: ClassVar[dict[tuple[int, int], pygame.Surface]] = {}
    WORD_LIST: ClassVar[Optional[List[str]]] = None
    word_index: ClassVar[int] = 0

    def __init__(self, player, target_player: bool = False) -> None:
        super().__init__(player)

        self.is_target_player = target_player

        # Size selection (0-9) affects visuals, speed, and rotation rate
        self.meteor_size = random.randint(0, 9)
        size_factor = 1.0 + (self.meteor_size * self.SIZE_FACTOR_MULTIPLIER)
        self.speed = random.uniform(self.SPEED_MIN, self.SPEED_MAX) / size_factor

        self.rotate_direction = random.choice((-1, 1))

        # Word handling
        self.word = self._get_next_word()
        self.drop_count = random.randint(len(self.word), len(self.word) + 10)

        # Image loading
        color_type = random.randint(0, 1)
        image_path = f"assets/images/meteors/meteor_{color_type}_{self.meteor_size}.png"
        self.original_image = Loader.load_image(image_path)

        # Rotation setup
        if self.USE_REALTIME_ROTATION:
            # Fallback: old method - rotate every frame
            self.current_rotation = 0.0
        else:
            # Optimized: pre-computed cache
            key = (color_type, self.meteor_size)
            self.rot_images = self._get_rotation_cache(color_type, self.meteor_size)
            self.base_image = self._BASE_IMAGES[key]

            # Size-aware rotation speed
            self.rotation_speed = max(
                self.ROTATION_MIN_SPEED,
                self.ROTATION_BASE_SPEED - (self.meteor_size * self.ROTATION_SPEED_DECREMENT)
            )

            self.rotation_accumulator = random.uniform(0, len(self.rot_images))
            self.rotation_index = int(self.rotation_accumulator) % len(self.rot_images)

        # Spawn position and collision rect
        self.rect = self.original_image.get_rect()
        self.rect.x = random.randint(
            self.EDGE_OFFSET, constants.SCREEN_WIDTH - self.EDGE_OFFSET
        )
        self.rect.y = self.SPAWN_Y_OFFSET

        # Initial direction
        angle = random.uniform(*self.INITIAL_ANGLE_RANGE)
        radians = math.radians(angle)
        self.dx = math.sin(radians) * self.speed
        self.dy = math.cos(radians) * self.speed

    # ==================== Helpers ====================

    @classmethod
    def _get_next_word(cls) -> str:
        if cls.WORD_LIST is None:
            cls.WORD_LIST = load_words()

        if cls.word_index >= len(cls.WORD_LIST):
            random.shuffle(cls.WORD_LIST)
            cls.word_index = 0

        word = cls.WORD_LIST[cls.word_index][:cls.WORD_MAX_LEN]
        cls.word_index += 1
        return word

    @classmethod
    def _get_rotation_cache(cls, color_type: int, meteor_size: int) -> List[pygame.Surface]:
        key = (color_type, meteor_size)
        if key not in cls._ROTATION_CACHES:
            image_path = f"assets/images/meteors/meteor_{color_type}_{meteor_size}.png"
            base_image = Loader.load_image(image_path)
            cls._BASE_IMAGES[key] = base_image

            cls._ROTATION_CACHES[key] = [
                pygame.transform.rotate(base_image, angle)
                for angle in range(0, 360, cls.ROTATION_STEP)
            ]
        return cls._ROTATION_CACHES[key]

    # ==================== Update ====================

    def move(self, game_over: bool) -> None:
        self.move_handle_pushback()

        if (
            self.is_target_player
            and not game_over
            and self.rect.y < self.HOMING_THRESHOLD_Y
        ):
            px, py = self.player.rect.center
            mx, my = self.rect.center
            angle = math.atan2(py - my, px - mx)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed

        self.rect.x += self.dx
        self.rect.y += self.dy

        if not self.USE_REALTIME_ROTATION:
            # Pre-cached rotation update
            self.rotation_accumulator += self.rotation_speed * self.rotate_direction
            self.rotation_index = int(self.rotation_accumulator) % len(self.rot_images)
        else:
            # Real-time rotation update (old method)
            self.current_rotation += self.rotate_direction * 2.0  # Adjust multiplier for desired speed

    # ==================== Draw ====================

    def draw(self, screen: pygame.Surface) -> None:
        if self.USE_REALTIME_ROTATION:
            # Old method: rotate every frame
            rotated_image = pygame.transform.rotate(self.original_image, self.current_rotation)
            rect = rotated_image.get_rect(center=self.rect.center)
            screen.blit(rotated_image, rect.topleft)
        else:
            # Optimized: use pre-rotated image
            image = self.rot_images[self.rotation_index]
            rect = image.get_rect(center=self.rect.center)
            screen.blit(image, rect.topleft)

        self.draw_word(screen)