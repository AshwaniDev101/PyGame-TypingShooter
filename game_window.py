import pygame

from campaign.jcon import Sender
from config import utils, constants
import math

from config.loader import Loader
from menu_screens.gui_button import HintButton


class GameWindow:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        # Load player icons for ammo and health display
        self.ammo_icon = utils.loader_scale_image("assets/images/game_window/ammo_label.png", 20)
        self.health_icon = utils.loader_scale_image("assets/images/game_window/health_label.png", 20)

        # Player hit effect settings
        self.player_hit_active = False
        self.hit_start_time = 0
        self.HIT_EFFECT_DURATION = 1000  # Duration in milliseconds
        self.max_alpha = 120  # Maximum opacity for the effect

        # AI and Enemy messages with typing effect
        self.enemy_message = None
        self.ship_ai_message = None
        self.enemy_message_start_time = None
        self.ship_ai_message_start_time = None
        self.current_enemy_text = ""
        self.current_ship_ai_text = ""
        self.text_index_enemy = 0
        self.text_index_ship_ai = 0

        # Animation positions for AI image and speech box
        self.enemy_image_pos = [200, 200]  # Fixed AI position
        self.enemy_speech_box_pos = [260, 200]  # AI speech box position to the right
        self.ship_ai_image_pos = [500, 500]  # Fixed Enemy position
        self.ship_ai_speech_box_pos = [740, 800]  # Enemy speech box position to the left
        self.animation_speed = 5  # Speed for the animation movement

        # Message display timer
        self.message_duration = 5000  # 5 seconds duration
        self.message_end_time = None  # Timer to track when to remove message

    def trigger_player_hit_effect(self):
        # Activate the player hit effect
        self.player_hit_active = True
        self.hit_start_time = pygame.time.get_ticks()

    def draw_player_hit_effect(self):
        # Draw pulsating border around the screen when player is hit
        if self.player_hit_active:
            elapsed_time = pygame.time.get_ticks() - self.hit_start_time
            if elapsed_time < self.HIT_EFFECT_DURATION:
                alpha = int(self.max_alpha * abs(math.sin(elapsed_time / 200)))
                overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA)
                border_thickness = 20

                for i in range(1, 4):
                    pygame.draw.rect(overlay, (0, 200, 255, alpha // (i + 1)),
                                     (i, i, constants.SCREEN_WIDTH - 2 * i, border_thickness))
                    pygame.draw.rect(overlay, (0, 200, 255, alpha // (i + 1)),
                                     (i, constants.SCREEN_HEIGHT - border_thickness - i,
                                      constants.SCREEN_WIDTH - 2 * i, border_thickness))
                    pygame.draw.rect(overlay, (0, 200, 255, alpha // (i + 1)),
                                     (i, i, border_thickness, constants.SCREEN_HEIGHT - 2 * i))
                    pygame.draw.rect(overlay, (0, 200, 255, alpha // (i + 1)),
                                     (constants.SCREEN_WIDTH - border_thickness - i, i,
                                      border_thickness, constants.SCREEN_HEIGHT - 2 * i))
                self.screen.blit(overlay, (0, 0))
            else:
                self.player_hit_active = False  # Turn off effect after duration

    def start_message(self, sender, message):
        if sender == Sender.ALIEN:
            self.enemy_message = message
            self.current_enemy_text = ""
            self.text_index_enemy = 0
            self.enemy_message_start_time = pygame.time.get_ticks()
            self.enemy_image_pos = [constants.SCREEN_WIDTH - 260, 200]  # AI now on the right side
            self.enemy_speech_box_pos = [constants.SCREEN_WIDTH - 320, 200]  # Speech box to the left of AI
            # pygame.mixer.Sound("assets/sounds/enemy_sound.mp3").play()
            Loader.load_sound("assets/sounds/enemy_sound.mp3").play()
        elif sender == Sender.PLAYER:
            self.ship_ai_message = message
            self.current_ship_ai_text = ""
            self.text_index_ship_ai = 0
            self.ship_ai_message_start_time = pygame.time.get_ticks()
            self.ship_ai_image_pos = [200, 200]  # Enemy now on the left side
            self.ship_ai_speech_box_pos = [260, 200]  # Speech box to the right of Enemy
            # pygame.mixer.Sound("assets/sounds/ai_sound.mp3").play()
            Loader.load_sound("assets/sounds/ai_sound.mp3").play()
        self.message_end_time = pygame.time.get_ticks() + self.message_duration

    def update_message(self, is_ai=True):  # Add speed parameter
        typing_speed = 10

        now = pygame.time.get_ticks()
        if is_ai and self.enemy_message:
            if self.text_index_enemy < len(self.enemy_message) and now - self.enemy_message_start_time > typing_speed:
                self.current_enemy_text += self.enemy_message[self.text_index_enemy]
                self.text_index_enemy += 1
                self.enemy_message_start_time = now
        elif not is_ai and self.ship_ai_message:
            if self.text_index_ship_ai < len(self.ship_ai_message) and now - self.ship_ai_message_start_time > typing_speed:
                self.current_ship_ai_text += self.ship_ai_message[self.text_index_ship_ai]
                self.text_index_ship_ai += 1
                self.ship_ai_message_start_time = now

        if self.message_end_time and now > self.message_end_time:
            self.enemy_message = None
            self.ship_ai_message = None
            self.current_enemy_text = ""
            self.current_ship_ai_text = ""

    def display_ai_speech_box(self, image_path, current_text):
        if not current_text:
            return

        image_x, image_y = (constants.SCREEN_WIDTH // 2) + 50, constants.SCREEN_HEIGHT / 2 + 100  # AI image position
        box_x, box_y = image_x + 60, image_y  # AI speech box on the right

        # image = pygame.image.load(image_path).convert_alpha()
        image = Loader.load_image(image_path)
        image = pygame.transform.smoothscale(image, (50, 50))
        font = pygame.font.Font(None, 22)
        text_surface = font.render(current_text, True, (255, 255, 255))

        text_width, text_height = text_surface.get_size()
        padding = 15
        box_width = text_width + padding * 2
        box_height = text_height + padding * 2

        speech_box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(speech_box_surface, (50, 50, 50, 200), speech_box_surface.get_rect(), border_radius=10)
        pygame.draw.rect(speech_box_surface, (200, 200, 200, 255), speech_box_surface.get_rect(), 2, border_radius=10)

        tip_x, tip_y = image_x + image.get_width(), image_y + image.get_height()/2  # Center of AI image
        tail_points = [
            (box_x, box_y + box_height // 2),
            (tip_x, tip_y),
            (box_x, box_y + box_height // 2 + 10)
        ]

        pygame.draw.polygon(self.screen, (50, 50, 50, 200), tail_points)
        pygame.draw.polygon(self.screen, (200, 200, 200, 255), tail_points, 2)

        self.screen.blit(speech_box_surface, (box_x, box_y))
        self.screen.blit(text_surface, (box_x + padding, box_y + padding))
        self.screen.blit(image, (image_x, image_y))

    def display_enemy_speech_box(self, image_path, current_text):
        if not current_text:
            return

        image_x, image_y = constants.SCREEN_WIDTH - 50, constants.SCREEN_HEIGHT / 2  # Enemy image position
        box_x, box_y = image_x - 160, image_y  # Speech box on the left side

        # image = pygame.image.load(image_path).convert_alpha()
        image = Loader.load_image(image_path)
        image = pygame.transform.smoothscale(image, (50, 50))
        font = pygame.font.Font(None, 22)

        # Render the current text (starting from right and growing left)
        text_surface = font.render(current_text, True, (255, 255, 255))

        text_width, text_height = text_surface.get_size()
        padding = 15
        box_width = text_width + padding * 2
        box_height = text_height + padding * 2

        # Adjust box position as text grows to the left
        box_x = image_x - box_width - 15

        speech_box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(speech_box_surface, (50, 50, 50, 200), speech_box_surface.get_rect(), border_radius=10)
        pygame.draw.rect(speech_box_surface, (200, 200, 200, 255), speech_box_surface.get_rect(), 2, border_radius=10)

        # Tail remains fixed at the center of the image
        tip_x, tip_y = image_x , image_y+image.get_height()/2
        tail_points = [
            (box_x + box_width, box_y + box_height // 2),  # Right edge of the box
            (tip_x, tip_y),  # Center of the enemy image
            (box_x + box_width, box_y + box_height // 2 + 10)
        ]
        pygame.draw.polygon(self.screen, (50, 50, 50, 200), tail_points)
        pygame.draw.polygon(self.screen, (200, 200, 200, 255), tail_points, 2)

        # Blit the box and text
        self.screen.blit(speech_box_surface, (box_x, box_y))
        self.screen.blit(text_surface, (box_x + padding, box_y + padding))  # Text starts from the right edge
        self.screen.blit(image, (image_x, image_y))

    def display_states(self):
        # Display player health, ammo, buttons, and messages
        font = pygame.font.Font(None, 25)
        x_offset = 10
        y_offset = 50
        ui_spacing = 40

        # Display control buttons
        self.display_buttons()

        # Update and show AI message with animation
        if self.enemy_message:
            self.update_message(is_ai=True)
            self.display_enemy_speech_box("assets/images/game_window/alien_in_monitor.png", self.current_enemy_text)

        # Update and show Enemy message with animation
        if self.ship_ai_message:
            self.update_message(is_ai=False)
            self.display_ai_speech_box("assets/images/game_window/player_in_monitor.png", self.current_ship_ai_text)

        # Display player ammo icon and count
        self.screen.blit(self.ammo_icon, (x_offset, y_offset + 30))
        ammo_text = font.render(f"{self.player.ammo}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (x_offset + 30, y_offset + 35))

        # Display player health icon and count
        self.screen.blit(self.health_icon, (x_offset, y_offset + ui_spacing + 30))
        health_text = font.render(f"{self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (x_offset + 30, y_offset + ui_spacing + 35))

    def display_buttons(self):
        # Define button properties
        button_height = 30
        control_font = pygame.font.Font(pygame.font.match_font("arial"), 15)

        # Create button instances
        esc_button = HintButton("ESC", (10, 10), control_font)
        left_arrow_button = HintButton("Left-Arrow /", (10, constants.SCREEN_HEIGHT - button_height - 45), control_font)
        l_shift_button = HintButton("L-Shift", (10, constants.SCREEN_HEIGHT - button_height - 10), control_font)
        tab_button = HintButton("Tab", (120, constants.SCREEN_HEIGHT - button_height - 10), control_font)

        right_arrow_width = control_font.size("Right-Arrow")[0] + 30  # Dynamic width calculation
        right_arrow_button = HintButton("Right-Arrow /", (
        constants.SCREEN_WIDTH - right_arrow_width - 10, constants.SCREEN_HEIGHT - button_height - 45), control_font)
        r_shift_button = HintButton("R-Shift", (
        constants.SCREEN_WIDTH - right_arrow_width - 10, constants.SCREEN_HEIGHT - button_height - 10), control_font)

        # Draw buttons
        esc_button.draw(self.screen)
        left_arrow_button.draw(self.screen)
        l_shift_button.draw(self.screen)
        tab_button.draw(self.screen)
        right_arrow_button.draw(self.screen)
        r_shift_button.draw(self.screen)

        # Draw "Switch Target" text
        switch_text = control_font.render("Switch Target. Press A to Z Keys to Type and Shoot", True, (255, 255, 255))
        self.screen.blit(switch_text,
                         (tab_button.rect.right + 5, tab_button.rect.centery - switch_text.get_height() // 2))



