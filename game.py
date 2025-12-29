import random
import sys

import pygame

from campaign_manager.checkpoint_manager import CheckpointManager
from config import constants, game_settings as settings
from enemies.checkpoint_divider import CheckpointDivider
from enemies.enemy import Enemy
from enemies.enemy_battleship import EnemyBattleship
from enemies.enemy_cluster_bomb import EnemyClusterBomb
from enemies.enemy_gunship import EnemyGunship
from enemies.enemy_meteor import EnemyMeteor
from enemies.enemy_proximity_mine import EnemyProximityMines
from enemies.enemy_sucide_drone import EnemySuicideDrone
from config.loader import Loader
from menu_screens.upgrade_screen import UpgradeWindow
from player import Player
from shooting.bullet_manager import BulletManager
from menu_screens.in_game_menu import InGameMenu
from game_window import GameWindow
from campaign_manager import jcon


# ----------------- Game Class (Main Game Logic) -----------------
class Game:
    def __init__(self, checkpoint_selected, star_background, screen=None):
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
        self.game_over = False      # Game over a flag
        self.paused = False         # Pause flag
        self.start_time = pygame.time.get_ticks()  # Record game start time

        # Set time for the next meteor spawn using a random interval
        self.next_meteor_spawn_time = self.get_next_meteor_spawn_delay()
        self.meteor_shower = False # When True Start spawning meteors
        # Additional game state variables
        self.enemy_selection_mode = False # if True player needs to select the enemy first before shooting
        self.selected_enemy = None  # Currently focused on an enemy

        self.is_boss_active = False  # Temp way to tigger the end of a Boss fight so that a campaign_manager can continue

        # Campaign Management
        self.checkpoint_manager = CheckpointManager()
        self.game_campaign_event_list = {}
        self.last_campaign_event_time = 0
        self.next_campaign_event_index = 0

        # # Checkpoint handling

        self.checkpoint_map = {}
        self.load_game_campaign(checkpoint_selected)

        # Upgrade window screen
        self.upgrade_window = UpgradeWindow(self.screen)


    def reset_game(self):
        # Reset game state for a new game session
        self.start_time = pygame.time.get_ticks()

        # Resetting Player
        self.player = Player()
        self.player.ammo = 100
        self.player.health = 3


        # Resetting window elements
        self.game_window = GameWindow(self.screen, self.player)
        self.menu.active = False
        self.menu.hover_index = None
        self.menu.option_rects.clear()
        self.game_over = False
        self.paused = False



        self.bullets_manager = BulletManager(self.player)
        self.enemy_list.clear()

        # Resetting Enemy
        self.next_meteor_spawn_time = self.get_next_meteor_spawn_delay()
        self.meteor_shower = False
        self.selected_enemy = None

        self.is_boss_active = False  # Temp way to tigger the end of a Boss fight so that a campaign_manager can continue

        # Reset campaign_manager events so they start from the beginning
        # self.triggered_events.clear()

        # the get number of the checkpoints
        checkpoint_level = len(self.checkpoint_manager.get_list_of_unlocked_checkpoints())
        self.load_game_campaign(checkpoint_level)


    def load_game_campaign(self,checkpoint_level):
        # data = Loader.load_json("campaign_manager/campaigns/game_jam_campaign.json")
        data = Loader.load_json("campaign_manager/campaigns/fastpace_campaign.json")
        self.game_campaign_event_list = data["events"]  # Extract the list of events from the JSON data
        # self.next_campaign_event_index = start_from_index  # Reset the event index from 0

        self.build_checkpoint_map()
        checkpoint_index = self.checkpoint_map.get(f"{checkpoint_level}")
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
                        self.enemy_list.append(EnemyMeteor(self.player,target_player=True))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_PROXIMITY_MINE:
                        self.enemy_list.append(EnemyProximityMines(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_CLUSTER_BOMB:
                        self.enemy_list.append(EnemyClusterBomb(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_SUICIDE_DRONE:
                        self.enemy_list.append(EnemySuicideDrone(self.player))

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_GUNSHIP:
                        self.enemy_list.append(EnemyGunship(self.player, self.enemy_list))
                        self.is_boss_active = True

                    elif jsonObject[jcon.ENEMY_TYPE] == jcon.EnemyType.ENEMY_BATTLESHIP:
                        self.enemy_list.append(EnemyBattleship(self.player, self.enemy_list))
                        self.is_boss_active = True

                    print(f"({key}) Enemy-spawn {jsonObject[jcon.ENEMY_TYPE]}")

                elif key == "message":
                    # Display a message on the game window
                    sender = jsonObject[jcon.SENDER]
                    message = jsonObject[jcon.TEXT_MESSAGE]

                    if sender == "alien":
                        self.game_window.show_incoming_message(message)
                    elif sender == "player":
                        self.game_window.show_outgoing_message(message)

                    print(f"{sender} : {message}")

                elif key == "trigger":
                    # Set the state for triggers (e.g., meteor shower)
                    self.meteor_shower = jsonObject[jcon.METEOR_SHOWER]
                    print(f"Trigger {jsonObject}")

                elif key == "music":

                    print(f"Change music {jsonObject}")
                elif key == "cutscenes":

                    print(f"Cutscene triggered! {jsonObject}")


                elif key == "checkpoint":

                    id = int(jsonObject["id"])
                    print(f"Starting from checkpoint id {id}")
                    self.enemy_list.append(CheckpointDivider(self.player, self.checkpoint_manager, id))


                    # if isinstance(jsonObject["action"], dict):
                        # checkpoint_id = jsonObject["action"]["checkpoint"]  # Extract checkpoint (string)
                        # print(f"Checkpoint {checkpoint_id} print")

                    # # Build the checkpoint data.
                    # checkpoint_data = self.checkpoint_manager.build_checkpoint(jsonObject, self.player)
                    # self.checkpoint_manager.save_checkpoint(checkpoint_data)



    def process_json_campaign(self):
        # Don't process campaign_manager events while paused
        if self.paused:
            return

        # Check if there's an active enemy that's still alive
        if self.is_boss_active:
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

        elif event.key == pygame.K_TAB:

            pass
            # self.paused = not self.paused  # Toggle pause state
            # self.upgrade_window.toggle()

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
                self.selected_enemy.selected = False # Selection Mode can be turned ON or OFF using Boolean Toggle
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
        """Selection mode: Type a letter to select the CLOSEST matching enemy (highlight it)
        + shoot bullets at ALL matching enemies.
        - Visual selection on closest for focus
        """
        letter_typed = event.unicode.lower()
        if not letter_typed.isalpha():
            return

        if self.player.health <= 0:
            return

        matching_enemies = [
            enemy for enemy in self.enemy_list
            if enemy.word and enemy.word[0].lower() == letter_typed
        ]

        if not matching_enemies:
            Loader.load_sound("assets/sounds/spring.wav").play()
            return

        # Sort closest first
        player_center = self.player.rect.center

        def distance_sq(enemy):
            dx = enemy.rect.centerx - player_center[0]
            dy = enemy.rect.centery - player_center[1]
            return dx * dx + dy * dy

        matching_enemies.sort(key=distance_sq)

        if self.player.ammo <= 0:
            Loader.load_sound("assets/sounds/no_ammo.mp3").play()
            return

        # Deselect old, select closest new one
        if self.selected_enemy:
            self.selected_enemy.selected = False
        self.selected_enemy = matching_enemies[0]
        self.selected_enemy.selected = True

        # Multi-shot
        for enemy in matching_enemies:
            enemy.remove_letter()
            self.player.gun_rotate_toward(enemy)
            shoot_pos = self.player.get_gun_end_firing_point()
            self.bullets_manager.shoot(shoot_pos, enemy, letter_typed)

        self.player.loss_ammo()  # 1 ammo total
        # No success sound



    def shooting_on_keypress(self, event):
        """Direct mode: Type a letter to shoot bullets at ALL enemies whose word starts with that letter.
        - 1 ammo per keypress (Option A)
        - Sort closest to farthest
        - Rotate gun toward each (rapid flick effect via sequential rotates)
        """

        letter_typed = event.unicode.lower()
        if not letter_typed.isalpha():
            return

        if self.player.health <= 0:
            return

        # Find all enemies whose word starts with the typed letter
        matching_enemies = [
            enemy for enemy in self.enemy_list
            if enemy.word and enemy.word[0].lower() == letter_typed
        ]

        if not matching_enemies:
            # Optional: keep silent (like original), or uncomment below for miss feedback
            # Loader.load_sound("assets/sounds/spring.wav").play()
            return

        # Sort by distance: closest first
        player_center = self.player.rect.center

        def distance_sq(enemy):
            dx = enemy.rect.centerx - player_center[0]
            dy = enemy.rect.centery - player_center[1]
            return dx * dx + dy * dy

        matching_enemies.sort(key=distance_sq)

        # Check ammo once
        if self.player.ammo <= 0:
            Loader.load_sound("assets/sounds/no_ammo.mp3").play()
            return

        # Shoot ALL matching enemies
        for enemy in matching_enemies:
            enemy.remove_letter()  # Remove letter from this enemy
            self.player.gun_rotate_toward(enemy)  # Flick gun toward it
            shoot_pos = self.player.get_gun_end_firing_point()
            self.bullets_manager.shoot(shoot_pos, enemy, letter_typed)

        # Only 1 ammo used, no matter how many hits
        self.player.loss_ammo()
        # No success sound — silent, just like you want


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
                elif clicked_option == "Load Last Checkpoint":
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


                # Checking for a boss enemy and resuming the campaign_manager
                if isinstance(enemy, (EnemyGunship, EnemyBattleship)):
                    if enemy.is_defeated():
                        self.is_boss_active = False

                # Shoot() function specific to Enemy Gunships
                # if isinstance(enemy, EnemyGunship):  # Ensure only battleships shoot
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


                # Delete off-screen enemy
                if (
                    enemy.rect.top >= constants.SCREEN_HEIGHT + 20
                    or enemy.rect.left <= -50
                    or enemy.rect.right >= constants.SCREEN_WIDTH + 50
                ):
                    self.enemy_list.remove(enemy)
                    if enemy == self.selected_enemy:
                        self.selected_enemy = None

                # Player Coalition detection
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

            # Upgrade window
            self.upgrade_window.draw()

            pygame.display.update()
        pygame.quit()



