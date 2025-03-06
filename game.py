import random
import sys

import pygame

from campaign.checkpoint_manager import CheckpointManager
from config import constants, game_settings as settings
from enemies.enemy import Enemy
from enemies.enemy_battleship import EnemyBattleship
from enemies.enemy_cluster_bomb import EnemyClusterBomb
from enemies.enemy_gunship import EnemyGunship
from enemies.enemy_meteor import EnemyMeteor
from enemies.enemy_proximity_mine import EnemyProximityMines
from enemies.enemy_sucide_drone import EnemySuicideDrone
from config.loader import Loader
from player import Player
from shooting.bullet_manager import BulletManager
from effects.stars import StarBackground
from menu_screens.in_game_menu import InGameMenu
from game_window import GameWindow
from campaign import jcon


# ----------------- Game Class (Main Game Logic) -----------------
class Game:
    def __init__(self, level_selected, star_background, screen=None):
        pygame.init()

        if screen is None:
            self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        else:
            self.screen = screen

        # self.screen = pygame.display.set_mode(
        #     (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        # )
        self.clock = pygame.time.Clock()  # Controls FPS


        self.player = Player()  # Create the player object
        self.bullets_manager = BulletManager(self.player)  # Bullet manager
        self.stars = star_background  # Star background effect for gameplay
        self.enemy_list: list[Enemy] = []  # List to store enemy objects


        # Menus and Windows
        self.menu = InGameMenu(self.screen)  # In-game menu (for pause/resume)
        self.game_window = GameWindow(self.screen, self.player)  # HUD/info window
        self.game_over = False      # Game over flag
        self.paused = False         # Pause flag
        self.start_time = pygame.time.get_ticks()  # Record game start time


        # Set time for next meteor spawn using a random interval
        self.next_meteor_spawn_time = self.get_next_meteor_spawn_delay()
        self.meteor_shower = False # When True Start spawning meteors
        # Additional game state variables
        self.enemy_selection_mode = False # if True player would need to select the enemy first before shooting
        self.selected_enemy = None  # Currently targeted enemy




        # Campaign Management
        self.checkpoint_manager = CheckpointManager()
        self.game_campaign_event_list = {}
        self.last_campaign_event_time = 0
        self.next_campaign_event_index = 0


        # Checkpoint handling
        self.selected_level = level_selected
        self.checkpoint_map = {}
        self.load_game_campaign()

        # self.triggered_events = set()  # Track which JSON events have been triggered


    def reset_game(self):
        # Reset game state for a new game session
        self.start_time = pygame.time.get_ticks()

        # Resetting window elements
        self.game_window = GameWindow(self.screen, self.player)
        self.menu.active = False
        self.menu.hover_index = None
        self.menu.option_rects.clear()
        self.game_over = False
        self.paused = False

        # Resetting Player
        self.player = Player()
        self.bullets_manager = BulletManager(self.player)
        self.enemy_list.clear()

        # Resetting Enemy
        self.next_meteor_spawn_time = self.get_next_meteor_spawn_delay()
        self.meteor_shower = False
        self.selected_enemy = None

        # Reset campaign events so they start from the beginning
        # self.triggered_events.clear()
        self.load_game_campaign()


    def load_game_campaign(self):
        data = Loader.load_json("campaign/game_event.json")
        self.game_campaign_event_list = data["events"]  # Extract the list of events from the JSON data
        # self.next_campaign_event_index = start_from_index  # Reset the event index from 0

        self.build_checkpoint_map()
        checkpoint_index = self.checkpoint_map.get(f"{self.selected_level}")
        self.next_campaign_event_index = checkpoint_index

        self.last_campaign_event_time = pygame.time.get_ticks()  # Record the current time for delays

    def build_checkpoint_map(self):

        for index, event in enumerate(self.game_campaign_event_list):
            action = event.get("action", {})
            # Check if the action contains a 'checkpoint'
            if "checkpoint" in action:
                checkpoint_info = action["checkpoint"]
                # Ensure checkpoint_info is a dictionary and has an 'id'
                if isinstance(checkpoint_info, dict) and "id" in checkpoint_info:
                    checkpoint_id = checkpoint_info["id"]
                    self.checkpoint_map[checkpoint_id] = index



    def handle_json_event(self, json_campaign_data):
        # Process one or more actions for an event
        if isinstance(json_campaign_data, list):
            for json_campaign in json_campaign_data:
                self.spawn_entities(json_campaign)  # Process each action in the list
        else:
            self.spawn_entities(json_campaign_data)  # Process a single action


    def spawn_entities(self, json_campaign_data):
        # Execute game actions based on the keys in the action data
        for key, jsonObject in json_campaign_data.items():

            if self.player.health > 0 and not self.paused:
                if key == "spawn":

                    # Spawn an enemy based on its type
                    if jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_METEOR:
                        self.enemy_list.append(EnemyMeteor(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_PROXIMITY_MINE:
                        self.enemy_list.append(EnemyProximityMines(self.player))
                        self.enemy_list.append(EnemyProximityMines(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_CLUSTER_BOMB:
                        self.enemy_list.append(EnemyClusterBomb(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_SUICIDE_DRONE:
                        self.enemy_list.append(EnemySuicideDrone(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_GUNSHIP:
                        self.enemy_list.append(EnemyGunship(self.player, self.enemy_list))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_BATTLESHIP:
                        self.enemy_list.append(EnemyBattleship(self.player, self.enemy_list))

                    print(f"({key}) Enemy-spawn {jsonObject[jcon.ENEMY_TYPE]}")

                elif key == "message":
                    # Display a message on the game window
                    self.game_window.start_message(jsonObject[jcon.SENDER], jsonObject[jcon.TEXT_MESSAGE])
                    print(f"{jsonObject[jcon.SENDER]}: {jsonObject[jcon.TEXT_MESSAGE]}")

                elif key == "trigger":

                    # Set the state for triggers (e.g., meteor shower)
                    self.meteor_shower = jsonObject[jcon.METEOR_SHOWER]
                    print(f"Trigger {jsonObject}")

                elif key == "music":

                    print(f"Change music {jsonObject}")
                elif key == "cutscenes":

                    print(f"Cutscene triggered! {jsonObject}")


                elif key == "checkpoint":

                    print(f"Starting from checkpoint id {jsonObject["id"]}")

                    # if isinstance(jsonObject["action"], dict):
                        # checkpoint_id = jsonObject["action"]["checkpoint"]  # Extract checkpoint (string)
                        # print(f"Checkpoint {checkpoint_id} print")

                    # # Build the checkpoint data.
                    # checkpoint_data = self.checkpoint_manager.build_checkpoint(jsonObject, self.player)
                    # self.checkpoint_manager.save_checkpoint(checkpoint_data)



    def process_json_campaign(self):
        # Don't process campaign events while paused
        if self.paused:
            return

        current_time = pygame.time.get_ticks()  # Current time in milliseconds
        if self.next_campaign_event_index < len(self.game_campaign_event_list):  # If there are remaining events
            next_event = self.game_campaign_event_list[self.next_campaign_event_index]
            delay = next_event.get("delay", 0)  # Get the event's delay (ms)
            if current_time - self.last_campaign_event_time >= delay:
                self.handle_json_event(next_event["action"])  # Trigger the event action
                self.last_campaign_event_time = current_time  # Update reference time
                self.next_campaign_event_index += 1  # Move to the next event



    def handle_keydown(self, event):
        # Process keyboard input during gameplay
        if event.key == pygame.K_ESCAPE:
            self.menu.toggle()
            self.paused = self.menu.active

        elif event.key == pygame.K_F10:
            # self.reset_game()
            # self.load_game_campaign(start_from_index=15)
            self.next_campaign_event_index = 15
            print("F10 pressed!")
        elif event.key == pygame.K_F11:
            # checkpoints = self.checkpoint_manager.load_checkpoints()
            self.checkpoint_manager.print_checkpoints()

        elif event.key == pygame.K_INSERT:
            pygame.image.save(self.screen, "screenshot.png")

        elif event.key == pygame.K_TAB:
            if self.selected_enemy:
                self.selected_enemy.selected = False
            self.selected_enemy = None
        elif event.key == pygame.K_HOME:
            self.stars.set_top_speed(1)
        elif event.key == pygame.K_END:
            self.stars.set_top_speed(2)
        elif event.key == pygame.K_PAGEUP:

            self.stars.set_top_speed(10)
        elif event.key == pygame.K_PAGEDOWN:
            self.stars.set_top_speed(5)

        else:
            # Handle letter input for shooting enemies
            #
            if self.enemy_selection_mode:
                self.shooting_on_keypress_selection_mode(event)
            else:
                self.shooting_on_keypress(event)


    def shooting_on_keypress_selection_mode(self, event):
        letter_typed = event.unicode.lower()
        if self.player.health > 0:
            if self.selected_enemy is None or self.selected_enemy.is_defeated():
                if self.selected_enemy:
                    self.selected_enemy.selected = False
                self.selected_enemy = None

                # Select the closed enemy to the player
                closest_enemy = None
                min_distance = float('inf')
                for enemy in self.enemy_list:
                    if enemy.word and enemy.word[0].lower() == letter_typed:
                        # Calculate the Euclidean distance between the enemy and the player.
                        dx = enemy.rect.centerx - self.player.rect.centerx
                        dy = enemy.rect.centery - self.player.rect.centery
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_enemy = enemy

                if closest_enemy:
                    self.selected_enemy = closest_enemy
                    self.selected_enemy.selected = True

            if self.selected_enemy:
                if self.selected_enemy.word and self.selected_enemy.word[0].lower() == letter_typed:
                    if self.player.ammo > 0:
                        self.player.gun_rotate_toward(self.selected_enemy)  # this point the gun toward the enemy
                        self.selected_enemy.remove_letter()

                        self.bullets_manager.shoot(
                            self.player.get_gun_end_firing_point(),
                            self.selected_enemy,
                            letter_typed,
                        )
                        self.player.loss_ammo()

                else:
                    # pygame.mixer.Sound("assets/sounds/spring.wav").play()
                    Loader.load_sound("assets/sounds/spring.wav").play()

    def shooting_on_keypress(self, event):
        # Handle letter input for shooting enemies directly without selection.
        letter_typed = event.unicode.lower()

        # Only process letters between a and z.
        if not letter_typed.isalpha():
            return

        if self.player.health > 0:
            # Iterate over enemies and shoot the first enemy whose word starts with the typed letter.
            for enemy in self.enemy_list:
                if enemy.word and enemy.word[0].lower() == letter_typed:
                    if self.player.ammo > 0:
                        # Rotate the player's gun toward this enemy.
                        self.player.gun_rotate_toward(enemy)
                        # Remove the letter from the enemy.
                        enemy.remove_letter()
                        # Shoot a bullet at the enemy.
                        self.bullets_manager.shoot(
                            self.player.get_gun_end_firing_point(),
                            enemy,
                            letter_typed,
                        )
                        self.player.loss_ammo()
                    else:
                        # Play a sound if there’s no ammo.
                        Loader.load_sound("assets/sounds/no_ammo.mp3").play()
                    # Stop after handling the first matching enemy.
                    break
                else:
                    pass
                    # If no enemy starts with the letter, you can play an error sound.
                    # Loader.load_sound("assets/sounds/spring.wav").play()

    def process_events(self):
        # Process all game events (keyboard, mouse, etc.)
        self.process_json_campaign()
        for event in pygame.event.get():

            self.player.handle_event_continuously(event)

            if event.type == pygame.QUIT:
                sys.exit() # Close the window when close button is clicked


            if event.type == pygame.KEYDOWN:
                # handle key events
                self.handle_keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_option = self.menu.handle_mouse_click(event.pos)
                if clicked_option == "resume":
                    self.paused = False
                elif clicked_option == "restart":
                    self.reset_game()
                elif clicked_option == "main_menu":
                    return "main_menu"  # Return the flag to signal a return to the start screen
            if event.type == pygame.MOUSEMOTION:
                self.menu.handle_mouse_hover(event.pos)
        return True

    def update_game_state(self):
        # Update all game objects and check for collisions
        if not self.paused:
            self.stars.update_and_draw(self.screen, pygame.time.get_ticks())
            self.bullets_manager.update_and_draw(self.screen, self.enemy_list)
            self.player.handle_movement()
            self.player.draw(self.screen) # updated
            if not self.game_over:

                # Update Meteors in the game
                if self.meteor_shower:
                    current_time = pygame.time.get_ticks()
                    if current_time >= self.next_meteor_spawn_time:
                        self.enemy_list.append(EnemyMeteor(self.player))
                        self.next_meteor_spawn_time = current_time + self.get_next_meteor_spawn_delay()


            for enemy in self.enemy_list[:]:
                enemy.move(self.game_over)
                enemy.draw(self.screen)

                # Shoot() function specific to Enemy Gunships
                # if isinstance(enemy, EnemyGunship):  # Ensure only gunships shoot
                #     enemy.shoot()

                # # If the enemy is a battleship, update its shells too.
                # if isinstance(enemy, EnemyBattleship):
                #     for shell in enemy.shells[:]:
                #         shell.move()  # Update the shell's position
                #         shell.draw(self.screen)  # Draw the shell
                #
                #         # Optionally, remove the shell if it's off-screen
                #         if shell.rect.top >= constants.SCREEN_HEIGHT:
                #             enemy.shells.remove(shell)


                if (
                    enemy.rect.top >= constants.SCREEN_HEIGHT + 20
                    or enemy.rect.left <= -50
                    or enemy.rect.right >= constants.SCREEN_WIDTH + 50
                ):
                    self.enemy_list.remove(enemy)
                    if enemy == self.selected_enemy:
                        self.selected_enemy = None
                if not self.game_over and enemy.rect.colliderect(self.player.rect):
                    self.player.take_damage(1, self.game_window)
                    # pygame.mixer.Sound("assets/sounds/player_got_hit.mp3").play()
                    self.enemy_list.remove(enemy)
                    self.selected_enemy = None
                if self.player.health == 0:
                    self.game_over = True
                    self.player.set_dead()
            self.game_window.display_states()
        self.menu.draw_menu()
        self.game_window.draw_player_hit_effect()

    def get_next_meteor_spawn_delay(self):
        return random.randint(
            settings.meteor_spawn_interval[0],
            settings.meteor_spawn_interval[1]
        )

    def manage_game_sounds(self):
        # Centralized global sound management:
        if self.paused:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
        # Check if the player's engine sound is playing; if not, restart it.
        # Only play the engine sound if the player is alive.
        if self.player.health > 0 and not self.player.engine_channel.get_busy():
            self.player.engine_channel.play(self.player.engine_sound, loops=-1)
        elif self.player.health == 0:
            self.player.engine_channel.stop()


    def run(self):
        # Main game loop
        running = True
        while running:

            self.clock.tick(constants.FPS)

            result = self.process_events()
            if result == "main_menu":
                return "main_menu"
            elif not result:
                return False

            if not self.paused:
                self.screen.fill(constants.BLACK)
            self.update_game_state()

            self.manage_game_sounds()
            pygame.display.update()
        pygame.quit()



