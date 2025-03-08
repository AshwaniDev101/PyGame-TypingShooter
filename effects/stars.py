import pygame
import random
import math
from config import constants
from config.loader import Loader

# Named constants for cloud positioning
CLOUD_SPAWN_Y = -1000         # Y position where clouds spawn
CLOUD_DELETE_Y = 1000         # Y position beyond which clouds are removed
CLOUD_X_MARGIN = 200          # Extra horizontal margin for cloud spawn

# Optional: Cloud spawn interval range in milliseconds
CLOUD_SPAWN_INTERVAL_MIN = 2000
CLOUD_SPAWN_INTERVAL_MAX = 4000

class StarBackground:
    def __init__(self):
        # Number of stars and twinkling stars per layer.
        self.num_stars = 80
        self.num_twinkles = 100

        # Set speeds for each star layer:
        # Bottom (farthest) is slow, middle is moderate, top (closest) is fast.
        self.bottom_star_speed = 0.5
        self.middle_star_speed = 1
        self.top_layer_star_speed = 2

        # Generate star layers as mutable lists (using list comprehensions).
        self.bottom_layer_stars = self.generate_stars(self.num_stars, sizes=[1, 2])
        self.bottom_layer_twinkles = self.generate_twinkling_stars(self.num_twinkles, sizes=[1, 2])
        self.middle_layer_stars = self.generate_stars(self.num_stars, sizes=[1, 2])
        self.top_layer_stars = self.generate_stars(self.num_stars, sizes=[1, 2])

        # Cache cloud images (load once).
        self.cloud_images = [Loader.load_image(f"assets/images/space_elements/cloud_{i}.png") for i in range(10)]

        # Pre-populate clouds: their y positions are randomized between CLOUD_SPAWN_Y and SCREEN_HEIGHT.
        self.clouds = self.generate_initial_clouds(10)

        # Timer-based cloud spawning.
        self.last_cloud_spawn_time = pygame.time.get_ticks()
        self.cloud_spawn_interval = random.randint(CLOUD_SPAWN_INTERVAL_MIN, CLOUD_SPAWN_INTERVAL_MAX)

    # Generate regular stars as lists [x, y, size] (in-place updates)
    def generate_stars(self, count, sizes):
        return [[random.randint(0, constants.SCREEN_WIDTH),
                 random.randint(0, constants.SCREEN_HEIGHT),
                 random.choice(sizes)] for _ in range(count)]

    # Generate twinkling stars as lists [x, y, size, phase]
    def generate_twinkling_stars(self, count, sizes):
        return [[random.randint(0, constants.SCREEN_WIDTH),
                 random.randint(0, constants.SCREEN_HEIGHT),
                 random.choice(sizes),
                 random.uniform(0, 2 * math.pi)] for _ in range(count)]

    # Update a star's vertical position; reset if off-screen.
    def update_star_position(self, star, speed):
        star[1] += speed
        if star[1] > constants.SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, constants.SCREEN_WIDTH)
        return star

    # Update a twinkling star's position (preserving phase).
    def update_twinkle_position(self, star, speed):
        star[1] += speed
        if star[1] > constants.SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, constants.SCREEN_WIDTH)
        return star

    # Draw a regular star as a white rectangle.
    def draw_star(self, screen, star):
        x, y, size = star
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(x, y, size, size))

    # Draw a twinkling star using sine modulation for brightness.
    # Here we compute base_time once per call to reduce redundant calculations.
    def draw_twinkle(self, screen, star, base_time):
        x, y, size, phase = star
        brightness_factor = (math.sin(base_time + phase) + 1) / 2
        brightness = int(200 * brightness_factor + 55)
        color = (brightness, brightness, brightness)
        pygame.draw.rect(screen, color, pygame.Rect(x, y, size, size))

    # Update and draw a star layer. Uses in-place updates.
    def update_and_draw_layer(self, screen, current_time, stars, speed, twinkles=None):
        # Update and draw regular stars.
        for star in stars:
            self.update_star_position(star, speed)
            self.draw_star(screen, star)
        # Update and draw twinkling stars if provided.
        if twinkles is not None:
            base_time = current_time / 300.0  # Compute base time once.
            for star in twinkles:
                self.update_twinkle_position(star, speed)
                self.draw_twinkle(screen, star, base_time)

    # Draw the bottom (farthest) layer (includes twinkling stars).
    def draw_bottom_layer(self, screen, current_time):
        self.update_and_draw_layer(screen, current_time, self.bottom_layer_stars, self.bottom_star_speed, self.bottom_layer_twinkles)

    # Draw the middle layer (only regular stars).
    def draw_middle_layer(self, screen, current_time):
        self.update_and_draw_layer(screen, current_time, self.middle_layer_stars, self.middle_star_speed)

    # Draw the top layer (only regular stars).
    def draw_top_layer(self, screen, current_time):
        self.update_and_draw_layer(screen, current_time, self.top_layer_stars, self.top_layer_star_speed)

    # Update and draw all layers (stars and clouds) to create the parallax effect.
    def update_and_draw(self, screen, current_time):
        self.draw_bottom_layer(screen, current_time)
        self.draw_middle_layer(screen, current_time)
        self.draw_top_layer(screen, current_time)
        self.update_and_draw_clouds(screen, current_time)

    # Set new top speed and adjust middle and bottom speeds proportionally.
    def set_top_speed(self, speed):
        self.top_layer_star_speed = speed
        self.middle_star_speed = speed / 2.0
        self.bottom_star_speed = speed / 4.0

    def set_middle_speed(self, speed):
        self.middle_star_speed = speed

    def set_bottom_speed(self, speed):
        self.bottom_star_speed = speed

    # ------------------ Cloud Functions ------------------ #

    # Helper to get a random cloud image from the cached list.
    def load_random_cloud_image(self):
        return random.choice(self.cloud_images)

    # Create a single cloud that spawns at y = CLOUD_SPAWN_Y.
    # The x position is random between -CLOUD_X_MARGIN and SCREEN_WIDTH + CLOUD_X_MARGIN.
    def create_random_cloud(self):
        cloud_image = self.load_random_cloud_image()
        rect = cloud_image.get_rect()
        rect.x = random.randint(-CLOUD_X_MARGIN, constants.SCREEN_WIDTH + CLOUD_X_MARGIN)
        rect.y = CLOUD_SPAWN_Y
        speed = random.uniform(0.5, 1.0)
        return cloud_image, rect, speed

    # Generate an initial set of clouds that are already on screen.
    # Their y positions are randomized between CLOUD_SPAWN_Y and constants.SCREEN_HEIGHT.
    def generate_initial_clouds(self, count):
        clouds = []
        for _ in range(count):
            cloud_image = self.load_random_cloud_image()
            rect = cloud_image.get_rect()
            rect.x = random.randint(-CLOUD_X_MARGIN, constants.SCREEN_WIDTH + CLOUD_X_MARGIN)
            rect.y = random.randint(CLOUD_SPAWN_Y, constants.SCREEN_HEIGHT)
            speed = random.uniform(0.5, 1.0)
            clouds.append((cloud_image, rect, speed))
        return clouds

    # Update and draw clouds:
    # - Spawn a new cloud when the spawn interval has elapsed.
    # - Move each cloud downward.
    # - Remove clouds that have moved past CLOUD_DELETE_Y.
    def update_and_draw_clouds(self, screen, current_time):
        # Check if it's time to spawn a new cloud.
        if current_time - self.last_cloud_spawn_time >= self.cloud_spawn_interval:
            new_cloud = self.create_random_cloud()
            self.clouds.append(new_cloud)
            # Reset the spawn timer and choose a new interval.
            self.last_cloud_spawn_time = current_time
            self.cloud_spawn_interval = random.randint(CLOUD_SPAWN_INTERVAL_MIN, CLOUD_SPAWN_INTERVAL_MAX)
        updated_clouds = []
        for cloud_image, rect, speed in self.clouds:
            rect.y += speed
            screen.blit(cloud_image, rect)
            if rect.y <= CLOUD_DELETE_Y:
                updated_clouds.append((cloud_image, rect, speed))
        self.clouds = updated_clouds
