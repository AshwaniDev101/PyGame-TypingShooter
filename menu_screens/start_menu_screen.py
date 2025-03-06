import pygame
import random
import math
from config import utils
from effects.stars import StarBackground
from config.loader import Loader

# Meteor class: Represents a meteor that spawns off-screen (or on-screen if specified)
class Meteor:
    def __init__(self, screen, images, screen_width, screen_height, spawn_inside=False):
        self.screen = screen
        # Choose a random meteor image
        self.image = random.choice(images)
        self.rect = self.image.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height

        if spawn_inside:
            # Spawn at a random on-screen position
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.randint(0, screen_height - self.rect.height)
        else:
            # Use normal random.choice for spawn side
            side = random.choice(['top', 'left', 'right', 'bottom'])
            if side == 'top':
                # Force y-coordinate to be -100 for clarity
                self.rect.x = random.randint(-self.rect.width, screen_width)
                self.rect.y = -100
            elif side == 'bottom':
                self.rect.x = random.randint(-self.rect.width, screen_width)
                self.rect.y = screen_height
            elif side == 'left':
                self.rect.x = -self.rect.width
                self.rect.y = random.randint(-self.rect.height, screen_height)
            elif side == 'right':
                self.rect.x = screen_width
                self.rect.y = random.randint(-self.rect.height, screen_height)

        # Determine a random target position off-screen for the meteor to move toward.
        target_side = random.choice(['top', 'bottom', 'left', 'right'])
        if target_side == 'top':
            target_x = random.randint(-self.rect.width, screen_width)
            target_y = -self.rect.height
        elif target_side == 'bottom':
            target_x = random.randint(-self.rect.width, screen_width)
            target_y = screen_height
        elif target_side == 'left':
            target_x = -self.rect.width
            target_y = random.randint(-self.rect.height, screen_height)
        elif target_side == 'right':
            target_x = screen_width
            target_y = random.randint(-self.rect.height, screen_height)
        self.target = (target_x, target_y)

        # Calculate the normalized velocity vector to the target.
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1  # Prevent division by zero
        self.speed = random.uniform(1, 3)  # Random speed for variation
        self.velocity = (dx / distance * self.speed, dy / distance * self.speed)

    def update(self):
        # Update the meteor's position based on its velocity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # Remove the meteor if it's far off-screen (with a buffer)
        buffer = 50
        if (self.rect.x < -buffer or self.rect.x > self.screen_width + buffer or
            self.rect.y < -buffer or self.rect.y > self.screen_height + buffer):
            return False
        return True

    def draw(self):
        # Draw the meteor on the screen
        self.screen.blit(self.image, self.rect)

# StartScreen class: Manages the start menu, background space_elements, and meteor space_elements.
class StartScreen:
    def __init__(self, screen, star_background):
        self.screen = screen
        self.active = True

        self.star_background = star_background

        # Menu options
        self.menu_options = ["Load Game", "Settings", "Layout", "Exit"]
        self.font = Loader.load_font("assets/fonts/BungeeInline-Regular.ttf", 16)
        self.option_rects = []  # For clickable menu options
        self.hover_index = None  # Tracks the current hovered option

        # Star background effect

        self.hover_sound = Loader.load_sound("assets/sounds/menu_hover_sound.wav")

        # Music setup
        self.music_on = True
        self.music_font = pygame.font.Font(None, 24)
        Loader.load_music("assets/sounds/music/ambientmain_0.ogg")
        pygame.mixer.music.play(-1)  # Loop music indefinitely
        button_width = 130
        button_height = 40
        margin = 20
        self.music_button_rect = pygame.Rect(
            self.screen.get_width() - button_width - margin,
            self.screen.get_height() - button_height - margin,
            button_width,
            button_height
        )

        # Load meteor images (meteor_1.png to meteor_19.png)
        self.meteor_images = [Loader.load_image(f"assets/images/meteors/meteor_{i}.png") for i in range(1, 20)]
        self.meteors = []

        # Prepopulate initial on-screen meteors
        initial_meteor_count = 5  # Adjust the count as needed
        for _ in range(initial_meteor_count):
            meteor = Meteor(self.screen, self.meteor_images, self.screen.get_width(), self.screen.get_height(), spawn_inside=True)
            self.meteors.append(meteor)

    def handle_mouse_click(self, pos):
        # Toggle music if the music button is clicked
        if self.music_button_rect.collidepoint(pos):
            self.toggle_music()
            return None
        # Check if a menu option was clicked
        if self.active:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    pygame.mixer.music.stop()
                    self.music_on = False
                    print(f"{self.menu_options[i]} clicked!")
                    return self.menu_options[i]
        return None

    def toggle_music(self):
        # Toggle the music on or off
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_on = False
            print("Music turned off")
        else:
            pygame.mixer.music.unpause()
            self.music_on = True
            print("Music turned on")

    def handle_mouse_hover(self, pos):
        # Update which menu option is being hovered
        previous_hover = self.hover_index
        self.hover_index = None
        if self.active:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self.hover_index = i
        if self.hover_index is not None and self.hover_index != previous_hover:
            self.hover_sound.play()
            self.draw_home_screen()
        elif self.hover_index is None and previous_hover is not None:
            self.draw_home_screen()

    def handle_events(self, events):
        # Process events like quit, mouse click, and mouse movement
        for event in events:
            if event.type == pygame.QUIT:
                return "Exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                result = self.handle_mouse_click(pos)
                if result:
                    return result
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                self.handle_mouse_hover(pos)
        return None

    def draw_home_screen(self):
        # Clear the option rectangles list for fresh drawing
        self.option_rects.clear()
        BOX_WIDTH = 200
        BOX_HEIGHT = 40
        OPTION_SPACING = 60
        start_y = (self.screen.get_height() - len(self.menu_options) * OPTION_SPACING) // 2
        # Draw each menu option
        for i, option in enumerate(self.menu_options):
            box_rect = pygame.Rect(
                (self.screen.get_width() - BOX_WIDTH) // 2,
                start_y + i * OPTION_SPACING,
                BOX_WIDTH,
                BOX_HEIGHT
            )
            border_color = utils.color("FF4D66") if i == self.hover_index else utils.color("FFB34B")
            pygame.draw.rect(self.screen, border_color, box_rect, 2, border_radius=5)
            text_surface = self.font.render(option, True, (255, 255, 255))
            text_outline = self.font.render(option, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=box_rect.center)
            self.screen.blit(text_outline, (text_rect.x - 1, text_rect.y))
            self.screen.blit(text_outline, (text_rect.x + 1, text_rect.y))
            self.screen.blit(text_outline, (text_rect.x, text_rect.y - 1))
            self.screen.blit(text_outline, (text_rect.x, text_rect.y + 1))
            self.screen.blit(text_surface, text_rect)
            self.option_rects.append(box_rect)

    def update_meteors(self):
        # Update each meteor and remove it if it goes off-screen
        for meteor in self.meteors[:]:
            if not meteor.update():
                self.meteors.remove(meteor)
        # Spawn new meteors off-screen (spawn_inside=False)
        if random.random() < 0.01:
            new_meteor = Meteor(self.screen, self.meteor_images, self.screen.get_width(), self.screen.get_height(), spawn_inside=False)
            self.meteors.append(new_meteor)

    def draw(self):
        # Clear the screen and draw all elements
        self.screen.fill((0, 0, 0))
        self.star_background.update_and_draw(self.screen, pygame.time.get_ticks())
        self.update_meteors()
        for meteor in self.meteors:
            meteor.draw()
        self.draw_home_screen()
        pygame.draw.rect(self.screen, (100, 100, 100), self.music_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.music_button_rect, 2)
        music_text = "Music: On" if self.music_on else "Music: Off"
        text_surf = self.music_font.render(music_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.music_button_rect.center)
        self.screen.blit(text_surf, text_rect)
        pygame.display.flip()
