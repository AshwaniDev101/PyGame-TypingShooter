import pygame
import sys

from config import constants

from game import Game
from menu_screens.layout_menu_screen import LayoutMenu
from menu_screens.level_loading_screen import LevelLoadingScreen
from menu_screens.setting_menu_screen import SettingsMenu
from menu_screens.start_menu_screen import StartScreen

from effects.stars import StarBackground



def get_monitor_height_width():
    # Ensure Pygame is initialized
    if not pygame.get_init():
        pygame.init()

    # Retrieve available display modes (highest resolution is usually first)
    modes = pygame.display.list_modes()

    if modes:
        monitor_width = modes[0][0] - 800
        monitor_height = modes[0][1] - 100  # Adjust height as needed
    else:
        # Fallback if no modes are returned
        monitor_width = 1280  # Default width
        monitor_height = 720  # Default height

    return monitor_width, monitor_height


def main(star_background=None):
    pygame.init()

    # setting dynamic height and width
    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = get_monitor_height_width()
    screen = pygame.display.set_mode(
        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    )

    # Create the star_background only once.
    if star_background is None:
        star_background = StarBackground()

    clock = pygame.time.Clock()

    # =========  Debugging ====================================================
    debug_mode = False  # Set to True to skip the start menu_screens for debugging
    if debug_mode:
        # Optionally run an intro screen if needed:
        # intro = GameIntro(screen)
        # intro.run()

        # Directly run the game:
        game = Game(screen,star_background)
        result = game.run()

        # Optionally, to test the "Load Game" screen instead:
        # load_game_screen = LoadGameScreen(screen)
        # while True:
        #     events = pygame.event.get()
        #     for event in events:
        #         if event.type == pygame.QUIT:
        #             pygame.quit()
        #             return
        #     result = load_game_screen.handle_events(events)
        #     load_game_screen.draw()
        #     clock.tick(60)

        # Or test the "Settings" screen:
        # settings_menu = SettingsMenu(screen)
        # while True:
        #     events = pygame.event.get()
        #     for event in events:
        #         if event.type == pygame.QUIT:
        #             pygame.quit()
        #             return
        #     result = settings_menu.handle_events(events)
        #     settings_menu.draw()
        #     clock.tick(60)
        return
        # ===============================================================

    # Create and show the start screen until an option is chosen
    start_screen = StartScreen(screen,star_background)
    chosen_option = None

    while not chosen_option:
        events = pygame.event.get()
        chosen_option = start_screen.handle_events(events)
        start_screen.draw()
        clock.tick(60)

    # Process the chosen option
    if chosen_option == "Exit":
        pygame.quit()
        return
    # elif chosen_option == "New Game":
    #
    #     # Show the intro screen (like your Settings or Load Game screens)
    #     intro = GameIntro(screen)
    #     intro.run()  # Waits until user clicks "Next"
    #
    #
    #     game = Game()
    #     result = game.run()
    #     if result == "main_menu":
    #         # If "Main Menu" was selected during gameplay, return to the start screen.
    #         main()

    elif chosen_option == "Start Game":
        load_game_screen = LevelLoadingScreen(screen,star_background)  # LevelSelectionScreen(screen)
        running_load = True

        while running_load:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running_load = False

                # # Press ESC key as an alternative to clicking the escape button
                # if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                #     running_load = False

            result = load_game_screen.handle_events(events)

            # print(result)
            if result == "Escape":
                running_load = False

            # elif result == "Level-Selected":
            elif isinstance(result, dict) and "Level-Selected" in result:
                level_selected = result["Level-Selected"]

                running_load = False  # Exit selection loop
                if level_selected is not None:
                    game = Game(checkpoint_selected=level_selected, star_background=star_background)
                    game_result = game.run()

                    if game_result == "main_menu":
                        # If "Main Menu" was selected during gameplay, return to the start screen.
                        main(star_background)







            load_game_screen.draw()
            clock.tick(60)
        # After closing the load screen, return to the start screen
        main(star_background)

    elif chosen_option == "Layout":

        settings_menu = SettingsMenu(screen)
        running_settings = True
        while running_settings:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running_settings = False
                # Press ESC key as an alternative to clicking the escape button
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running_settings = False

            result = settings_menu.handle_events(events)
            if result == "Escape":
                running_settings = False
            settings_menu.draw()
            clock.tick(60)
        # After closing the load screen, return to the start screen
        main(star_background)



    elif chosen_option == "About":
        print("Layout option selected.")

        layout_menu = LayoutMenu(screen)
        running_layout = True
        while running_layout:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running_layout = False
                # Press ESC key as an alternative to clicking the escape button
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running_layout = False
            result = layout_menu.handle_events(events)
            if result == "Escape":
                running_layout = False
            layout_menu.draw()
            clock.tick(60)
        # After closing the load screen, return to the start screen
        main(star_background)


if __name__ == "__main__":
    main()
