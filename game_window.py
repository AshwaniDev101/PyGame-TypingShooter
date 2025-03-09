import pygame
from config import utils, constants
from config.loader import Loader
from effects.player_hit_effect import HitEffect
from menu_screens.gui_button import HintButton

# Module-level constants for UI elements

TYPING_SPEED = 10                 # milliseconds delay between typing characters
MESSAGE_DURATION = 6000           # duration to display messages in milliseconds
SPEECH_PADDING = 15               # padding inside the speech bubble
SPEECH_GAP = 10                   # gap between avatar image and speech bubble
SPEECH_FONT_SIZE = 22             # font size for speech bubbles

class SpeechBubble:
    def __init__(self, image_path, side="right", gap=SPEECH_GAP, padding=SPEECH_PADDING,
                 font=None, max_width=400):
        """
        :param image_path: Path to the avatar image.
        :param side: 'right' or 'left' determines which side the speech bubble appears.
        :param gap: Gap between the image and the speech bubble.
        :param padding: Internal padding for the speech bubble.
        :param font: pygame.font.Font instance to render text.
        :param max_width: Maximum width of the speech bubble before text wraps.
        """
        self.image_path = image_path
        self.side = side
        self.gap = gap
        self.padding = padding
        self.font = font or pygame.font.Font(None, SPEECH_FONT_SIZE)
        self.max_width = max_width
        self.image = Loader.load_image(image_path)
        self.image = pygame.transform.smoothscale(self.image, (50, 50))

    def wrap_text(self, text):
        """Wrap text into multiple lines so that each line does not exceed max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            # Allow some padding within max_width
            if self.font.size(test_line)[0] <= self.max_width - 2 * self.padding:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def render(self, screen, current_text, image_pos):
        if not current_text:
            return

        # Wrap the text and determine dimensions
        lines = self.wrap_text(current_text)
        line_height = self.font.get_linesize()
        box_width = self.max_width
        box_height = line_height * len(lines) + self.padding * 2

        # Determine bubble position based on side
        if self.side == "right":
            box_x = image_pos[0] + self.image.get_width() + self.gap
        else:
            box_x = image_pos[0] - box_width - self.gap
        box_y = image_pos[1]

        # Create and draw the speech bubble surface
        speech_box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(speech_box_surface, (50, 50, 50, 200), speech_box_surface.get_rect(), border_radius=10)
        pygame.draw.rect(speech_box_surface, (200, 200, 200, 255), speech_box_surface.get_rect(), 2, border_radius=10)

        # Render and blit text line-by-line
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            speech_box_surface.blit(text_surface, (self.padding, self.padding + i * line_height))

        # Draw tail based on the side
        if self.side == "right":
            tip_x = image_pos[0] + self.image.get_width()
            tip_y = image_pos[1] + self.image.get_height() / 2
            tail_points = [
                (box_x, box_y + box_height // 2),
                (tip_x, tip_y),
                (box_x, box_y + box_height // 2 + 10)
            ]
        else:
            tip_x = image_pos[0]
            tip_y = image_pos[1] + self.image.get_height() / 2
            tail_points = [
                (box_x + box_width, box_y + box_height // 2),
                (tip_x, tip_y),
                (box_x + box_width, box_y + box_height // 2 + 10)
            ]
        pygame.draw.polygon(screen, (50, 50, 50, 200), tail_points)
        pygame.draw.polygon(screen, (200, 200, 200, 255), tail_points, 2)

        # Blit the speech bubble and avatar image
        screen.blit(speech_box_surface, (box_x, box_y))
        screen.blit(self.image, image_pos)




class GameWindow:
    """
    Main game window class handling UI, messaging, and game state display.
    """
    def __init__(self, screen, player):
        """
        :param screen: The pygame display surface.
        :param player: The player object containing attributes such as ammo and health.
        """
        self.screen = screen
        self.player = player

        # Load UI icons for ammo and health
        self.ammo_icon = utils.loader_scale_image("assets/images/game_window/ammo_label.png", 20)
        self.health_icon = utils.loader_scale_image("assets/images/game_window/health_label.png", 20)

        # Cache fonts for UI elements
        self.default_font = pygame.font.Font(None, 25)
        self.control_font = pygame.font.Font(pygame.font.match_font("arial"), 15)
        self.speech_font = pygame.font.Font(None, SPEECH_FONT_SIZE)

        # Initialize hit effect component
        self.hit_effect = HitEffect(screen)

        # Message and typing effect variables
        self.incoming_message = None
        self.incoming_message_sound = Loader.load_sound("assets/sounds/enemy_sound.mp3")
        self.outgoing_message = None
        self.outgoing_message_sound = Loader.load_sound("assets/sounds/ai_sound.mp3")
        
        self.current_enemy_text = ""
        self.current_ship_ai_text = ""
        self.text_index_enemy = 0
        self.text_index_ship_ai = 0
        self.incoming_message_timer = 0
        self.outgoing_message_timer = 0
        self.message_end_time = 0
        self.message_duration = MESSAGE_DURATION

        # Instantiate speech bubble components
        # For enemy: avatar on right so speech bubble appears on left
        self.enemy_speech_bubble = SpeechBubble("assets/images/game_window/alien_in_monitor.png", side="left", font=self.speech_font)
        # For ship AI: avatar on left so speech bubble appears on right
        self.ship_ai_speech_bubble = SpeechBubble("assets/images/game_window/player_in_monitor.png", side="right", font=self.speech_font)

        # Default avatar positions (can be updated when messages are triggered)
        self.enemy_image_pos = [constants.SCREEN_WIDTH - 50, constants.SCREEN_HEIGHT- 400]
        self.player_ship_pos = [constants.SCREEN_WIDTH - 525, constants.SCREEN_HEIGHT - 280]

    def trigger_player_hit_effect(self):
        """Activate the player's hit effect."""
        self.hit_effect.trigger()

    def draw_player_hit_effect(self):
        """Draw the player's hit effect if active."""
        self.hit_effect.update_and_draw()

    def show_incoming_message(self, message):
        """
        Initiate an incoming message with a typewriter effect.
        :param message: The full incoming message string to be displayed.
        """
        now = pygame.time.get_ticks()
        self.incoming_message = message
        self.current_enemy_text = ""
        self.text_index_enemy = 0
        self.incoming_message_timer = now
        self.incoming_message_sound.play()
        self.message_end_time = now + self.message_duration

    def show_outgoing_message(self, message):
        """
        Initiate an outgoing message with a typewriter effect.
        :param message: The full outgoing message string to be displayed.
        """
        now = pygame.time.get_ticks()
        self.outgoing_message = message
        self.current_ship_ai_text = ""
        self.text_index_ship_ai = 0
        self.outgoing_message_timer = now
        self.outgoing_message_sound.play()
        self.message_end_time = now + self.message_duration




    def _update_text(self, full_message, current_text, text_index, last_update_time, now, typing_speed=TYPING_SPEED):
        """
        Update text for the typewriter effect.
        :return: A tuple (updated_text, updated_index, updated_last_update_time)
        """
        if text_index < len(full_message) and now - last_update_time > typing_speed:
            current_text += full_message[text_index]
            text_index += 1
            last_update_time = now
        return current_text, text_index, last_update_time

    def update_messages(self):
        """Update the typing effect for enemy and ship AI messages."""
        now = pygame.time.get_ticks()
        if self.incoming_message:
            self.current_enemy_text, self.text_index_enemy, self.incoming_message_timer = self._update_text(
                self.incoming_message, self.current_enemy_text, self.text_index_enemy, self.incoming_message_timer, now)
        if self.outgoing_message:
            self.current_ship_ai_text, self.text_index_ship_ai, self.outgoing_message_timer = self._update_text(
                self.outgoing_message, self.current_ship_ai_text, self.text_index_ship_ai, self.outgoing_message_timer, now)
        # Clear messages if their duration has expired
        if self.message_end_time and now > self.message_end_time:
            self.incoming_message = None
            self.outgoing_message = None
            self.current_enemy_text = ""
            self.current_ship_ai_text = ""

    def draw_messages(self):
        """Update and render speech bubble messages on screen."""
        self.update_messages()
        if self.incoming_message:
            self.enemy_speech_bubble.render(self.screen, self.current_enemy_text, self.enemy_image_pos)
        if self.outgoing_message:
            self.ship_ai_speech_bubble.render(self.screen, self.current_ship_ai_text, self.player_ship_pos)

    def display_buttons(self):
        """Render control buttons and on-screen instructions."""
        esc_button = HintButton("ESC", (10, 10), self.control_font)
        left_arrow_button = HintButton("Left-Arrow /", (10, constants.SCREEN_HEIGHT - 30 - 45), self.control_font)
        l_shift_button = HintButton("L-Shift", (10, constants.SCREEN_HEIGHT - 30 - 10), self.control_font)
        # tab_button = HintButton("Tab", (120, constants.SCREEN_HEIGHT - 30 - 10), self.control_font)

        right_arrow_width = self.control_font.size("Right-Arrow")[0] + 30
        right_arrow_button = HintButton("Right-Arrow /", (constants.SCREEN_WIDTH - right_arrow_width - 10,
                                                            constants.SCREEN_HEIGHT - 30 - 45), self.control_font)
        r_shift_button = HintButton("R-Shift", (constants.SCREEN_WIDTH - right_arrow_width - 10,
                                                constants.SCREEN_HEIGHT - 30 - 10), self.control_font)

        esc_button.draw(self.screen)
        left_arrow_button.draw(self.screen)
        l_shift_button.draw(self.screen)
        # tab_button.draw(self.screen)
        right_arrow_button.draw(self.screen)
        r_shift_button.draw(self.screen)

        switch_text = self.control_font.render("Press A to Z Keys to Type and Shoot", True, (255, 255, 255))
        self.screen.blit(switch_text, (200, constants.SCREEN_HEIGHT - 30))

    # def display_states(self):
    #     """Display UI elements including player status and messages."""
    #     # Render control buttons and messages
    #     self.display_buttons()
    #     self.draw_messages()
    #
    #     # Display player ammo icon and count
    #     self.screen.blit(self.ammo_icon, (10, 50 + 30))
    #     ammo_text = self.default_font.render(f"{self.player.ammo}", True, (255, 255, 255))
    #     self.screen.blit(ammo_text, (10 + 30, 50 + 35))
    #
    #     # Display player health icon and count
    #     self.screen.blit(self.health_icon, (10, 50 + 40 + 30))
    #     health_text = self.default_font.render(f"{self.player.health}", True, (255, 255, 255))
    #     self.screen.blit(health_text, (10 + 30, 50 + 40 + 35))


    def display_states(self):
        """Display UI elements including player status and messages."""
        # Render control buttons and messages
        self.display_buttons()
        self.draw_messages()

        # Place the status UI on the right side using constants
        ui_x_offset = constants.SCREEN_WIDTH - 120  # Adjust this value for desired right-side margin
        y_offset = 50

        # Display player ammo icon and count on the right side
        self.screen.blit(self.ammo_icon, (ui_x_offset, y_offset + 30))
        ammo_text = self.default_font.render(f"{self.player.ammo}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (ui_x_offset + 30, y_offset + 35))

        # Display player health icon and count on the right side
        self.screen.blit(self.health_icon, (ui_x_offset, y_offset + 70))
        health_text = self.default_font.render(f"{self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (ui_x_offset + 30, y_offset + 75))