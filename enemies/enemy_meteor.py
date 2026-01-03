
import pygame
import math
import random
from typing import ClassVar, Optional, List

from config import constants
from enemies.enemy import Enemy
from config.loader import Loader


def load_words(file_name: str) -> List[str]:
    """Loads and shuffles words from the specified text file."""
    txt_path = Loader.resource_path(f"config/meteor_names/{file_name}")
    with open(txt_path, "r", encoding="utf-8") as file:
        words = [word for line in file for word in line.strip().split() if word]
    random.shuffle(words)
    return words


class EnemyMeteor(Enemy):
    """Falling meteor enemy with size-dependent word lists, speed, and rotation."""

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
    ROTATION_STEP: int = 2  # 180 images per variant (360 / 2)
    WORD_MAX_LEN: int = 15

    # Performance toggle: True uses real-time rotation (slower), False uses pre-cached sprites
    USE_REALTIME_ROTATION: bool = False

    # Class-level caches for pre-rotated images
    _ROTATION_CACHES: ClassVar[dict[tuple[int, int], List[pygame.Surface]]] = {}
    _BASE_IMAGES: ClassVar[dict[tuple[int, int], pygame.Surface]] = {}

    # Separate word lists for each size category
    SMALL_WORDS: ClassVar[Optional[List[str]]] = None
    MEDIUM_WORDS: ClassVar[Optional[List[str]]] = None
    LARGE_WORDS: ClassVar[Optional[List[str]]] = None

    # Indices for cycling through word lists
    small_index: ClassVar[int] = 0
    medium_index: ClassVar[int] = 0
    large_index: ClassVar[int] = 0

    def __init__(self, player, target_player: bool = False) -> None:
        super().__init__(player)
        self.is_target_player = target_player

        # Size selection (0–9)
        self.meteor_size = random.randint(0, 9)
        color_type = random.randint(0, 1)  # 0 or 1 for the two color variants

        # Size-based scaling
        size_factor = 1.0 + (self.meteor_size * self.SIZE_FACTOR_MULTIPLIER)
        self.speed = random.uniform(self.SPEED_MIN, self.SPEED_MAX) / size_factor

        self.rotate_direction = random.choice((-1, 1))

        # Select appropriate word list based on size
        if self.meteor_size <= 1:
            word_list = self._get_small_words()
            index_attr = "small_index"
        elif self.meteor_size <= 5:
            word_list = self._get_medium_words()
            index_attr = "medium_index"
        else:  # 6–9
            word_list = self._get_large_words()
            index_attr = "large_index"

        current_index = getattr(self.__class__, index_attr)
        if current_index >= len(word_list):
            random.shuffle(word_list)
            current_index = 0
        self.word = word_list[current_index][:self.WORD_MAX_LEN]
        setattr(self.__class__, index_attr, current_index + 1)

        self.drop_count = random.randint(len(self.word), len(self.word) + 10)

        # Image loading: format meteor_{color}_{size}.png
        image_path = f"assets/images/meteors/meteor_{color_type}_{self.meteor_size}.png"
        self.original_image = Loader.load_image(image_path)

        # Rotation setup
        if self.USE_REALTIME_ROTATION:
            self.current_rotation = 0.0
        else:
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

        # Spawn position and initial velocity
        self.rect = self.original_image.get_rect()
        self.rect.x = random.randint(
            self.EDGE_OFFSET, constants.SCREEN_WIDTH - self.EDGE_OFFSET - self.rect.width
        )
        self.rect.y = self.SPAWN_Y_OFFSET

        angle = random.uniform(*self.INITIAL_ANGLE_RANGE)
        radians = math.radians(angle)
        self.dx = math.sin(radians) * self.speed
        self.dy = math.cos(radians) * self.speed

    # ==================== Word List Loaders ====================
    @classmethod
    def _get_small_words(cls) -> List[str]:
        if cls.SMALL_WORDS is None:
            cls.SMALL_WORDS = load_words("small_meteor_names.txt")
        return cls.SMALL_WORDS

    @classmethod
    def _get_medium_words(cls) -> List[str]:
        if cls.MEDIUM_WORDS is None:
            cls.MEDIUM_WORDS = load_words("middum_meteor_names.txt")
        return cls.MEDIUM_WORDS

    @classmethod
    def _get_large_words(cls) -> List[str]:
        if cls.LARGE_WORDS is None:
            cls.LARGE_WORDS = load_words("large_meteor_names.txt")
        return cls.LARGE_WORDS

    # ==================== Rotation Cache ====================
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

        if self.is_target_player and not game_over and self.rect.y < self.HOMING_THRESHOLD_Y:
            px, py = self.player.rect.center
            mx, my = self.rect.center
            angle = math.atan2(py - my, px - mx)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed

        self.rect.x += self.dx
        self.rect.y += self.dy

        if not self.USE_REALTIME_ROTATION:
            self.rotation_accumulator += self.rotation_speed * self.rotate_direction
            self.rotation_index = int(self.rotation_accumulator) % len(self.rot_images)
        else:
            self.current_rotation += self.rotate_direction * 2.0

    # ==================== Draw ====================
    def draw(self, screen: pygame.Surface) -> None:
        if self.USE_REALTIME_ROTATION:
            rotated_image = pygame.transform.rotate(self.original_image, self.current_rotation)
            rect = rotated_image.get_rect(center=self.rect.center)
            screen.blit(rotated_image, rect.topleft)
        else:
            image = self.rot_images[self.rotation_index]
            rect = image.get_rect(center=self.rect.center)
            screen.blit(image, rect.topleft)

        self.draw_word(screen)

# import pygame
# import math
# import random
# from typing import ClassVar, Optional, List
#
# from config import constants
# from enemies.enemy import Enemy
# from config.loader import Loader
#
#
# def load_words() -> List[str]:
#     """Loads words from the text file, shuffles them, and returns the list."""
#     txt_path = Loader.resource_path("config/meteor_names.txt")
#     with open(txt_path, "r", encoding="utf-8") as file:
#         words = [word for line in file for word in line.strip().split()]
#     random.shuffle(words)
#     return words
#
#
# class EnemyMeteor(Enemy):
#     """
#     Optimized falling meteor enemy with:
#     - Efficient pre-rotated cached sprites (default)
#     - Option to fall back to real-time rotation for testing/performance comparison
#     - Size-based speed and rotation scaling
#     - Brief optional homing toward player
#     """
#
#     # Tunable constants
#     EDGE_OFFSET: int = 50
#     SPAWN_Y_OFFSET: int = -150
#     HOMING_THRESHOLD_Y: int = 50
#     INITIAL_ANGLE_RANGE: tuple[float, float] = (-30.0, 30.0)
#     SPEED_MIN: float = 1.2
#     SPEED_MAX: float = 2.5
#     SIZE_FACTOR_MULTIPLIER: float = 0.08
#     ROTATION_MIN_SPEED: float = 0.3
#     ROTATION_BASE_SPEED: float = 2.0
#     ROTATION_SPEED_DECREMENT: float = 0.18
#     ROTATION_STEP: int = 2                # Balanced smoothness vs memory (180 images per variant)
#     WORD_MAX_LEN: int = 15
#
#     # Performance toggle - set to True to use old real-time rotation method
#     USE_REALTIME_ROTATION: bool = False
#
#     # Shared class-level caches (only used when pre-caching is active)
#     _ROTATION_CACHES: ClassVar[dict[tuple[int, int], List[pygame.Surface]]] = {}
#     _BASE_IMAGES: ClassVar[dict[tuple[int, int], pygame.Surface]] = {}
#     WORD_LIST: ClassVar[Optional[List[str]]] = None
#     word_index: ClassVar[int] = 0
#
#     def __init__(self, player, target_player: bool = False) -> None:
#         super().__init__(player)
#
#         self.is_target_player = target_player
#
#         # Size selection (0-9) affects visuals, speed, and rotation rate
#         self.meteor_size = random.randint(0, 9)
#         size_factor = 1.0 + (self.meteor_size * self.SIZE_FACTOR_MULTIPLIER)
#         self.speed = random.uniform(self.SPEED_MIN, self.SPEED_MAX) / size_factor
#
#         self.rotate_direction = random.choice((-1, 1))
#
#         # Word handling
#         self.word = self._get_next_word()
#         self.drop_count = random.randint(len(self.word), len(self.word) + 10)
#
#         # Image loading
#         color_type = random.randint(0, 1)
#         image_path = f"assets/images/meteors/meteor_{color_type}_{self.meteor_size}.png"
#         self.original_image = Loader.load_image(image_path)
#
#         # Rotation setup
#         if self.USE_REALTIME_ROTATION:
#             # Fallback: old method - rotate every frame
#             self.current_rotation = 0.0
#         else:
#             # Optimized: pre-computed cache
#             key = (color_type, self.meteor_size)
#             self.rot_images = self._get_rotation_cache(color_type, self.meteor_size)
#             self.base_image = self._BASE_IMAGES[key]
#
#             # Size-aware rotation speed
#             self.rotation_speed = max(
#                 self.ROTATION_MIN_SPEED,
#                 self.ROTATION_BASE_SPEED - (self.meteor_size * self.ROTATION_SPEED_DECREMENT)
#             )
#
#             self.rotation_accumulator = random.uniform(0, len(self.rot_images))
#             self.rotation_index = int(self.rotation_accumulator) % len(self.rot_images)
#
#         # Spawn position and collision rect
#         self.rect = self.original_image.get_rect()
#         self.rect.x = random.randint(
#             self.EDGE_OFFSET, constants.SCREEN_WIDTH - self.EDGE_OFFSET
#         )
#         self.rect.y = self.SPAWN_Y_OFFSET
#
#         # Initial direction
#         angle = random.uniform(*self.INITIAL_ANGLE_RANGE)
#         radians = math.radians(angle)
#         self.dx = math.sin(radians) * self.speed
#         self.dy = math.cos(radians) * self.speed
#
#     # ==================== Helpers ====================
#
#     @classmethod
#     def _get_next_word(cls) -> str:
#         if cls.WORD_LIST is None:
#             cls.WORD_LIST = load_words()
#
#         if cls.word_index >= len(cls.WORD_LIST):
#             random.shuffle(cls.WORD_LIST)
#             cls.word_index = 0
#
#         word = cls.WORD_LIST[cls.word_index][:cls.WORD_MAX_LEN]
#         cls.word_index += 1
#         return word
#
#     @classmethod
#     def _get_rotation_cache(cls, color_type: int, meteor_size: int) -> List[pygame.Surface]:
#         key = (color_type, meteor_size)
#         if key not in cls._ROTATION_CACHES:
#             image_path = f"assets/images/meteors/meteor_{color_type}_{meteor_size}.png"
#             base_image = Loader.load_image(image_path)
#             cls._BASE_IMAGES[key] = base_image
#
#             cls._ROTATION_CACHES[key] = [
#                 pygame.transform.rotate(base_image, angle)
#                 for angle in range(0, 360, cls.ROTATION_STEP)
#             ]
#         return cls._ROTATION_CACHES[key]
#
#     # ==================== Update ====================
#
#     def move(self, game_over: bool) -> None:
#         self.move_handle_pushback()
#
#         if (
#             self.is_target_player
#             and not game_over
#             and self.rect.y < self.HOMING_THRESHOLD_Y
#         ):
#             px, py = self.player.rect.center
#             mx, my = self.rect.center
#             angle = math.atan2(py - my, px - mx)
#             self.dx = math.cos(angle) * self.speed
#             self.dy = math.sin(angle) * self.speed
#
#         self.rect.x += self.dx
#         self.rect.y += self.dy
#
#         if not self.USE_REALTIME_ROTATION:
#             # Pre-cached rotation update
#             self.rotation_accumulator += self.rotation_speed * self.rotate_direction
#             self.rotation_index = int(self.rotation_accumulator) % len(self.rot_images)
#         else:
#             # Real-time rotation update (old method)
#             self.current_rotation += self.rotate_direction * 2.0  # Adjust multiplier for desired speed
#
#     # ==================== Draw ====================
#
#     def draw(self, screen: pygame.Surface) -> None:
#         if self.USE_REALTIME_ROTATION:
#             # Old method: rotate every frame
#             rotated_image = pygame.transform.rotate(self.original_image, self.current_rotation)
#             rect = rotated_image.get_rect(center=self.rect.center)
#             screen.blit(rotated_image, rect.topleft)
#         else:
#             # Optimized: use pre-rotated image
#             image = self.rot_images[self.rotation_index]
#             rect = image.get_rect(center=self.rect.center)
#             screen.blit(image, rect.topleft)
#
#         self.draw_word(screen)