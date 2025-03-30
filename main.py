import ctypes
import pygame

from config import constants
from game import Game
from menu_screens.layout_menu_screen import LayoutMenu
from menu_screens.level_loading_screen import LevelLoadingScreen
from menu_screens.setting_menu_screen import SettingsMenu
from menu_screens.start_menu_screen import StartScreen
from effects.stars import StarBackground

# Set DPI awareness (Windows only)
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    print("Could not set DPI Awareness:", e)


def get_monitor_height_width():
    """
    Returns a scaled width and height based on the monitor's resolution.
    """
    # Ensure Pygame is initialized.
    if not pygame.get_init():
        pygame.init()

    info = pygame.display.Info()
    full_width = info.current_w
    full_height = info.current_h

    scale_width = 0.6
    scale_height = 0.92

    monitor_width = int(full_width * scale_width)
    monitor_height = int(full_height * scale_height)

    print(f"Monitor resolution: {full_width}x{full_height}")
    print(f"Scaled window dimensions: {monitor_width}x{monitor_height}")

    return monitor_width, monitor_height


def run_start_screen(screen, star_background, clock):
    """
    Runs the start screen until the user selects an option.
    Returns the chosen option.
    """
    start_screen = StartScreen(screen, star_background)
    chosen_option = None

    while not chosen_option:
        events = pygame.event.get()
        chosen_option = start_screen.handle_events(events)
        start_screen.draw()
        clock.tick(60)

    return chosen_option


def run_level_loading_screen(screen, star_background, clock):
    """
    Runs the level loading screen and returns the result.
    The result can be "Escape", "Exit", or a dictionary with the selected level.
    """
    load_game_screen = LevelLoadingScreen(screen, star_background)
    running_load = True
    result = None

    while running_load:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running_load = False
                result = "Exit"
        result = load_game_screen.handle_events(events)

        if result == "Escape":
            running_load = False
        elif isinstance(result, dict) and "Level-Selected" in result:
            level_selected = result["Level-Selected"]
            running_load = False
            return level_selected

        load_game_screen.draw()
        clock.tick(60)

    return result


def run_settings_menu(screen, clock):
    """
    Runs the settings menu until the user exits (via escape or window close).
    """
    settings_menu = SettingsMenu(screen)
    running_settings = True
    result = None

    while running_settings:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running_settings = False
                result = "Exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_settings = False
                result = "Escape"
        result = settings_menu.handle_events(events)

        if result == "Escape":
            running_settings = False

        settings_menu.draw()
        clock.tick(60)

    return result


def run_layout_menu(screen, clock):
    """
    Runs the layout (About) menu until the user exits.
    """
    layout_menu = LayoutMenu(screen)
    running_layout = True
    result = None

    while running_layout:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running_layout = False
                result = "Exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_layout = False
                result = "Escape"
        result = layout_menu.handle_events(events)

        if result == "Escape":
            running_layout = False

        layout_menu.draw()
        clock.tick(60)

    return result


def main():
    pygame.init()

    # Calculate dimensions only once and create the display window.
    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = get_monitor_height_width()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    star_background = StarBackground()
    clock = pygame.time.Clock()

    running = True

    while running:
        # Run the start screen and retrieve the chosen option.
        chosen_option = run_start_screen(screen, star_background, clock)

        if chosen_option == "Exit":
            running = False

        elif chosen_option == "Start Game":
            result = run_level_loading_screen(screen, star_background, clock)

            if result == "Exit":
                running = False
            elif result and result != "Escape":  # result is assumed to be the selected level.
                game = Game(checkpoint_selected=result, star_background=star_background)
                game_result = game.run()
                if game_result == "main_menu":
                    continue  # Return to the start screen.

        elif chosen_option == "Layout":
            result = run_settings_menu(screen, clock)
            if result == "Exit":
                running = False

        elif chosen_option == "About":
            result = run_layout_menu(screen, clock)
            if result == "Exit":
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()
