import pygame
from config import constants, utils
import math
from config.loader import Loader





class Player:
    def __init__(self):
        # Load and scale the player image (no rotation applied later)
        self.image = Loader.load_image("assets/images/player_ship.png")
        self.image = pygame.transform.smoothscale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (constants.SCREEN_WIDTH // 2, int(constants.SCREEN_HEIGHT * 0.89))

        # Gun angle used solely for drawing the gun line
        self.gun_angle = 0
        # self.gun_end_firing_point = 0,0
        self.health = 3
        self.ammo = 100
        self.shield_health = 0

        # Load flame sprites (no rotation needed)
        self.flame_sprites = [
            pygame.transform.smoothscale(
                Loader.load_image(f"assets/images/animated/jet_flames/flame_{i}.png"), (48, 40)
            ) for i in range(3)
        ]
        self.flame_index = 0
        self.flame_timer = pygame.time.get_ticks()
        self.flame_delay = 5

        self.hit_flash = False
        self.flash_start_time = 0
        self.FLASH_DURATION = 300

        # Engine sound setup
        self.engine_sound = Loader.load_sound("assets/sounds/jet_engine.ogg")
        self.engine_sound.set_volume(0.2)
        self.engine_channel = pygame.mixer.Channel(1)
        if not self.engine_channel.get_busy():
            self.engine_channel.play(self.engine_sound, loops=-1)

    def draw(self, screen):

        # Update and draw flame effect (if player is alive).
        if self.health > 0:
            self.draw_gun(screen)
            self.draw_and_update_flame(screen)
            self.draw_shield(screen)

        # Draw the player image
        screen.blit(self.image, self.rect.topleft)

        # Handle hit flash effect.
        if self.hit_flash:
            elapsed = pygame.time.get_ticks() - self.flash_start_time
            if elapsed < self.FLASH_DURATION:
                if elapsed // 50 % 2 == 0:
                    screen.blit(self.image, self.rect.topleft)
            else:
                self.hit_flash = False
                screen.blit(self.image, self.rect.topleft)

    def draw_and_update_flame(self, screen):
        now = pygame.time.get_ticks()
        if now - self.flame_timer > self.flame_delay:
            self.flame_index = (self.flame_index + 1) % len(self.flame_sprites)
            self.flame_timer = now
        flame = self.flame_sprites[self.flame_index]
        flame_rect = flame.get_rect(center=(self.rect.centerx, self.rect.bottom - 3))
        screen.blit(flame, flame_rect.topleft)


    def handle_movement(self):

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_LSHIFT]) and self.rect.left > 0:
            self.rect.move_ip(-constants.PLAYER_SPEED, 0)
        if (keys[pygame.K_RIGHT] or keys[pygame.K_RSHIFT]) and self.rect.right < constants.SCREEN_WIDTH:
            self.rect.move_ip(constants.PLAYER_SPEED, 0)

    def handle_event_continuously(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.shield_health = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.shield_health = 0

    # This method now only updates the gun's angle, not the player image.
    def gun_rotate_toward(self, enemy):
        dx = enemy.rect.centerx - self.rect.centerx
        dy = enemy.rect.centery - self.rect.centery
        self.gun_angle = math.degrees(math.atan2(dy, dx)) + 90

    def take_damage(self, damage=1, game_window=None):
        self.health = max(0, self.health - damage)
        if self.health == 0:
            Loader.load_sound("assets/sounds/explosion.wav").play()
            self.set_dead()
        else:
            Loader.load_sound("assets/sounds/player_hit.wav").play()
            self.hit_flash = True
            self.flash_start_time = pygame.time.get_ticks()
            if game_window:
                game_window.trigger_player_hit_effect()

    def loss_ammo(self):
        self.ammo -= 1
        Loader.load_sound("assets/sounds/gun_shooting.wav").play()
        if self.ammo <= 0:
            Loader.load_sound("assets/sounds/jamgun.mp3").play()

    def set_dead(self):
        self.image = Loader.load_image("assets/images/game_window/alien_in_monitor.png")
        self.image = pygame.transform.smoothscale(self.image, (100, 100))
        self.engine_channel.stop()


    def get_gun_end_firing_point(self):
        # Use the current gun_angle to compute the firing point

        gun_start =  self.get_center_start_gun()
        gun_length = 20
        angle_radians = math.radians(self.gun_angle)
        return (
           gun_start[0] + gun_length * math.sin(angle_radians),
            gun_start[1] - gun_length * math.cos(angle_radians)
        )


    def get_center_start_gun(self):
        return self.rect.centerx, self.rect.top + 5



    def draw_shield(self, screen):

        if self.shield_health==1:
            utils.draw_transparent_circle_with_gradient(
                screen, (100, 100, 200), (self.rect.centerx, self.rect.centery), 80, 128
            )



    def draw_gun(self,screen):
        # Get the firing point from the un-rotated image's rect.
        gun_starting_point = self.get_center_start_gun()  # self.get_firing_point()
        # Draw a transparent circle at the firing point.
        utils.draw_transparent_circle(screen, (60, 63, 65), gun_starting_point, 13, 200)

        # Gun
        pygame.draw.line(screen, (255, 0, 255), gun_starting_point, self.get_gun_end_firing_point(), 3)


