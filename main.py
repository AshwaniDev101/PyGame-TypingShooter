# To build the .exe:
# 1. Open a terminal / command prompt
# 2. Run: auto-py-to-exe
#
# To build the .exe using the existing config file:
# auto-py-to-exe --config "output/ashwanis_game_output_config_file.json"

import ctypes
import pygame
from config import constants
from config.loader import Loader  # We'll use this to load the icon
from game import Game
from menu_screens.about_menu_screen import AboutMenuScreen
from menu_screens.level_loading_screen import LevelLoadingScreen
from menu_screens.layout_menu_screen import LayoutMenuScreen
from menu_screens.start_menu_screen import StartScreen
from effects.stars import StarBackground


# Set DPI awareness (Windows only) - makes window scaling crisp on high-DPI screens
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass  # Not on Windows or failed - no problem


def get_monitor_height_width():
    """ Returns a scaled width and height based on the monitor's resolution. """
    pygame.init()  # Safe to call multiple times
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
    """ Runs the start menu and returns the selected option. """
    start_screen = StartScreen(screen, star_background)
    while True:
        events = pygame.event.get()
        chosen_option = start_screen.handle_events(events)
        if chosen_option:
            return chosen_option
        start_screen.draw()
        clock.tick(60)


def run_level_loading_screen(screen, star_background, clock):
    """ Runs level selection. Returns level number or None/"Exit". """
    level_screen = LevelLoadingScreen(screen, star_background)
    while True:
        events = pygame.event.get()
        result = level_screen.handle_events(events)
        if result == "Escape":
            return None
        if result == "Exit":
            return "Exit"
        if isinstance(result, dict) and "Level-Selected" in result:
            return result["Level-Selected"]  # Actual level number
        level_screen.draw()
        clock.tick(60)


def run_settings_menu(screen, clock):
    """ Runs the Layout/Settings placeholder screen. """
    settings_menu = LayoutMenuScreen(screen)
    return settings_menu.run()  # Returns "Escape" or "Exit"


def run_about_menu(screen, clock):
    """ Runs the About screen. """
    about_menu = AboutMenuScreen(screen)
    return about_menu.run()  # Returns "Escape" or "Exit"

# VERSION Details on "constants.py"
def main():
    pygame.init()

    # Set window size
    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = get_monitor_height_width()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

    # === CUSTOM WINDOW TITLE & ICON ===
    pygame.display.set_caption("Typing Shooter")  # Change to your game name!

    # Load and set custom icon (size: 32x32 or 64x64 PNG)
    try:
        icon = Loader.load_image("assets/images/icon/game_icon.png")
        pygame.display.set_icon(icon)
    except Exception as e:
        print("Could not load game icon:", e)
        # Falls back to default Pygame icon if file missing

    # ===================================

    star_background = StarBackground()
    clock = pygame.time.Clock()

    while True:
        # Main menu
        choice = run_start_screen(screen, star_background, clock)

        if choice == "Exit":
            break

        elif choice == "Start Game":
            level = run_level_loading_screen(screen, star_background, clock)
            if level == "Exit":
                break
            if level is not None:  # Valid level selected
                game = Game(checkpoint_selected=level, star_background=star_background)
                game_result = game.run()
                if game_result == "Exit":
                    break
                # If "main_menu", just loop back

        elif choice == "Layout":  # Settings / Layout placeholder
            result = run_settings_menu(screen, clock)
            if result == "Exit":
                break

        elif choice == "About":
            result = run_about_menu(screen, clock)
            if result == "Exit":
                break

    pygame.quit()


if __name__ == "__main__":
    main()