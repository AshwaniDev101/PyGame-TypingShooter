import pygame

from config import utils, constants
from config.loader import Loader
from shooting.bullet import Bullet
from effects.particles import Particle
from effects.plus_one import PlusXEffect
from effects.shockwave import Shockwave


# =============================================
# Bullet Manager Class
# =============================================
class BulletManager:
    def __init__(self, player):
        self.player = player
        self.bullets = []  # Active bullets
        self.enemy_bullets = []  # Enemy bullets list
        self.shockwaves = []  # Shockwave animated
        self.plus_x_effects = []  # '+X' ammo animated
        self.particles = []  # Bullet hit particles

        # Load and set up sounds
        # self.bullet_hit_sound = pygame.mixer.Sound("assets/sounds/bullet_hit.ogg")
        # self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.bullet_hit_sound = Loader.load_sound("assets/sounds/bullet_hit.ogg")
        self.explosion_sound = Loader.load_sound("assets/sounds/explosion.wav")

        self.bullet_hit_sound.set_volume(1.0)
        self.explosion_sound.set_volume(1.0)
        pygame.mixer.set_num_channels(32)
        self.explosion_channel = pygame.mixer.Channel(31)

    # =============================================
    # Bullet-related Functions
    # =============================================
    def shoot(self, firing_point, target_enemy, letter):
        # Create a new bullet and add it to the list
        bullet = Bullet(firing_point, target_enemy, letter)
        self.bullets.append(bullet)

    def handle_bullet_collision(self, bullet, enemies):
        # Handle what happens when a bullet hits an enemy
        if bullet.rect.colliderect(bullet.target.rect):
            bullet.target.reduce_hit_count()
            self.create_particle_effect(bullet.rect.centerx, bullet.rect.centery)
            bullet.target.apply_pushback(bullet, force=2)
            self.bullets.remove(bullet)
            self.bullet_hit_sound.play()

            if bullet.target.is_defeated():
                self.handle_enemy_defeated(bullet.target, enemies)


    # =============================================
    # Enemy Interaction Functions
    # =============================================
    def handle_enemy_defeated(self, enemy, enemies):
        # Handle the logic when an enemy is defeated
        self.explosion_channel.play(self.explosion_sound)
        self.create_shockwave(enemy.rect.centerx, enemy.rect.centery)

        drop_count = enemy.drop_count
        if drop_count > 0:
            self.create_plus_x_effect(enemy.rect.centerx, enemy.rect.centery, drop_count)
            self.player.ammo += drop_count
        pygame.time.delay(50)
        enemies.remove(enemy)

    # =============================================
    # Main Update and Draw Function
    # =============================================
    def update_and_draw(self, screen, enemies):
        # Update and draw all bullets, particles, shockwaves, and animated
        self.update_bullets(screen, enemies)
        self.update_enemy_bullets(screen)
        self.update_particles(screen)
        self.update_shockwaves(screen)
        self.update_plus_x_effects(screen)

    # =============================================
    # Individual Update and Draw Methods
    # =============================================
    def update_bullets(self, screen, enemies):
        # Update and draw all bullets
        for bullet in self.bullets[:]:
            if bullet.target not in enemies:
                self.bullets.remove(bullet)
                continue
            bullet.update()
            bullet.draw(screen)
            self.handle_bullet_collision(bullet, enemies)

    def update_enemy_bullets(self, screen):
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            bullet.draw(screen)

            # Check collision with player
            if bullet.rect.colliderect(self.player.rect):
                self.player.take_damage()  # Assuming player has a take_damage method
                self.enemy_bullets.remove(bullet)

            # Remove bullet if off screen
            elif bullet.y > constants.SCREEN_HEIGHT:
                self.enemy_bullets.remove(bullet)

    def update_particles(self, screen):
        # Update and draw all particles
        for particle in self.particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def update_shockwaves(self, screen):
        # Update and draw all shockwaves
        for shockwave in self.shockwaves[:]:
            shockwave.update()
            shockwave.draw(screen)
            if shockwave.alpha == 0:
                self.shockwaves.remove(shockwave)

    def update_plus_x_effects(self, screen):
        # Update and draw all '+X' ammo animated
        for plus_x in self.plus_x_effects[:]:
            plus_x.update()
            plus_x.draw(screen)
            if plus_x.lifetime <= 0:
                self.plus_x_effects.remove(plus_x)

    # =============================================
    # Visual Effects Functions
    # =============================================
    def create_particle_effect(self, x, y, color=(utils.color("FFF300")), amount=20):
        # Generate particle animated at a given position
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))

    def create_shockwave(self, x, y):
        # Create a shockwave effect at a given position
        self.shockwaves.append(Shockwave(x, y))

    def create_plus_x_effect(self, x, y, amount):
        # Create a '+X' effect at a given position with specified amount
        self.plus_x_effects.append(PlusXEffect(x, y, amount))
