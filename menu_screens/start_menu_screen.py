import pygame
from config import utils
from effects.stars import StarBackground
from config.loader import Loader


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.active = True
        # Define menu_screens options and use a smaller font size
        # self.menu_options = ["Load Game", "New Game", "Settings", "Layout", "Exit"]
        self.menu_options = ["Load Game", "Settings", "Layout", "Exit"]
        # self.font = pygame.font.Font("assets/fonts/BungeeInline-Regular.ttf", 16)
        self.font = Loader.load_font("assets/fonts/BungeeInline-Regular.ttf", 16)
        self.option_rects = []  # To store clickable rectangles for each option
        self.hover_index = None  # Track which option is currently hovered

        # Instantiate the star effect
        self.star_background = StarBackground()

        # self.hover_sound = pygame.mixer.Sound("assets/sounds/menu_hover_sound.wav")
        self.hover_sound = Loader.load_sound("assets/sounds/menu_hover_sound.wav")

        # --- Music Setup ---
        self.music_on = True  # Flag to track whether music is on
        self.music_font = pygame.font.Font(None, 24)  # Font for the music toggle button
        # Load and play the music file in an infinite loop
        # pygame.mixer.music.load("assets/sounds/music/ambientmain_0.ogg")
        # pygame.mixer.music.play(-1)
        # Loader.load_sound("assets/sounds/music/ambientmain_0.ogg").play(-1)
        Loader.load_music("assets/sounds/music/ambientmain_0.ogg")
        pygame.mixer.music.play(-1)  # Play the music in an infinite loop
        # Define the rectangle for the music toggle button at the bottom right
        button_width = 130
        button_height = 40
        margin = 20
        self.music_button_rect = pygame.Rect(
            self.screen.get_width() - button_width - margin,
            self.screen.get_height() - button_height - margin,
            button_width,
            button_height
        )

    def handle_mouse_click(self, pos):
        # First, check if the click is on the music toggle button
        if self.music_button_rect.collidepoint(pos):
            self.toggle_music()
            return None  # Do not return a menu_screens option when toggling music
        # Otherwise, check if the click is on any menu_screens option
        if self.active:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    # Stop the music when any menu_screens option is clicked
                    pygame.mixer.music.stop()
                    self.music_on = False
                    print(f"{self.menu_options[i]} clicked!")
                    return self.menu_options[i]
        return None

    def toggle_music(self):
        # Toggle the music on/off and pause/unpause the mixer accordingly
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_on = False
            print("Music turned off")
        else:
            pygame.mixer.music.unpause()
            self.music_on = True
            print("Music turned on")

    def handle_mouse_hover(self, pos):
        # Save the previous hover index to detect changes
        previous_hover = self.hover_index
        self.hover_index = None
        if self.active:
            # Check if the mouse is over any option rectangle
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self.hover_index = i
        # If the hovered option has changed, redraw the home screen options
        if self.hover_index is not None and self.hover_index != previous_hover:
            self.hover_sound.play()
            self.draw_home_screen()
        elif self.hover_index is None and previous_hover is not None:
            # Optionally, you can redraw the home screen when the mouse leaves,
            # but do not play the hover sound.
            self.draw_home_screen()

    def handle_events(self, events):
        # Process events: quit, mouse clicks, and mouse motion
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
        # Clear the option rectangles list (we'll rebuild it each frame)
        self.option_rects.clear()
        BOX_WIDTH = 200
        BOX_HEIGHT = 40
        OPTION_SPACING = 60
        # Center the options vertically
        start_y = (self.screen.get_height() - len(self.menu_options) * OPTION_SPACING) // 2
        for i, option in enumerate(self.menu_options):
            # Create a rectangle for the menu_screens option centered horizontally
            box_rect = pygame.Rect(
                (self.screen.get_width() - BOX_WIDTH) // 2,
                start_y + i * OPTION_SPACING,
                BOX_WIDTH,
                BOX_HEIGHT
            )
            # Choose border color based on hover state
            border_color = utils.color("FF4D66") if i == self.hover_index else utils.color("FFB34B")
            pygame.draw.rect(self.screen, border_color, box_rect, 2, border_radius=5)
            # Render the text and its outline for clarity
            text_surface = self.font.render(option, True, (255, 255, 255))
            text_outline = self.font.render(option, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=box_rect.center)
            self.screen.blit(text_outline, (text_rect.x - 1, text_rect.y))
            self.screen.blit(text_outline, (text_rect.x + 1, text_rect.y))
            self.screen.blit(text_outline, (text_rect.x, text_rect.y - 1))
            self.screen.blit(text_outline, (text_rect.x, text_rect.y + 1))
            self.screen.blit(text_surface, text_rect)
            # Save the rectangle for click detection
            self.option_rects.append(box_rect)
        # Do not call pygame.display.flip() here

    def draw(self):
        # Clear the screen at the start of each frame
        self.screen.fill((0, 0, 0))
        # Draw the star effect in the background
        self.star_background.update_and_draw(self.screen, pygame.time.get_ticks())
        # Draw the home screen menu_screens options (without flipping the display yet)
        self.draw_home_screen()
        # --- Draw the Music Toggle Button ---
        pygame.draw.rect(self.screen, (100, 100, 100), self.music_button_rect)  # Button background
        pygame.draw.rect(self.screen, (255, 255, 255), self.music_button_rect, 2)  # Button outline
        # Determine the text for the button based on the music state
        music_text = "Music: On" if self.music_on else "Music: Off"
        text_surf = self.music_font.render(music_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.music_button_rect.center)
        self.screen.blit(text_surf, text_rect)
        # Update the display once per frame
        pygame.display.flip()
