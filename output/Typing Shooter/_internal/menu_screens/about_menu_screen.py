import pygame
import webbrowser
import pyperclip

from config.constants import VERSION
from config import utils
from config.loader import Loader
from menu_screens.gui_button import HintButton


class ClickableLink:
    def __init__(self, text, url, copy_text, font, centerx, y, copy_icon):
        self.text = text
        self.url = url
        self.copy_text = copy_text
        self.font = font
        self.copy_icon = copy_icon

        self.base_color = (100, 149, 237)
        self.hover_color = (100, 200, 255)
        self.icon_hover_color = (220, 220, 220)

        self.color = self.base_color
        self.surface = font.render(text, True, self.color)
        self.rect = self.surface.get_rect(centerx=centerx, top=y)

        self.icon_rect = self.copy_icon.get_rect(
            midleft=(self.rect.right + 10, self.rect.centery)
        )

        self.hover_text = False
        self.hover_icon = False

    def update(self, mouse_pos):
        self.hover_text = self.rect.collidepoint(mouse_pos)
        self.hover_icon = self.icon_rect.collidepoint(mouse_pos)

        new_color = self.hover_color if self.hover_text else self.base_color
        if new_color != self.color:
            self.color = new_color
            self.surface = self.font.render(self.text, True, self.color)

        return self.hover_text or self.hover_icon

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

        if self.hover_text:
            pygame.draw.line(
                screen,
                self.hover_color,
                (self.rect.left, self.rect.bottom + 2),
                (self.rect.right, self.rect.bottom + 2),
                1
            )

        icon = self.copy_icon.copy()
        if self.hover_icon:
            icon.fill(self.icon_hover_color, special_flags=pygame.BLEND_RGB_ADD)

        screen.blit(icon, self.icon_rect)

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            webbrowser.open(self.url)
            return None
        elif self.icon_rect.collidepoint(mouse_pos):
            pyperclip.copy(self.copy_text)
            return "copied"
        return None


class AboutMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.active = True

        self.width = screen.get_width()
        self.height = screen.get_height()

        # Images
        self.creator_image = utils.loader_scale_image(
            "assets/images/game_window/bunny.jpg", 100
        )
        self.copy_icon = utils.loader_scale_image(
            "assets/images/icon/copy.png", 18
        )

        # ---------------- Fonts ----------------
        # bungeinline_path = "assets/fonts/BungeeInline-Regular.ttf"
        # roboto_path = "assets/fonts/Roboto-Regular.ttf"

        # Font paths
        bungee_font_path = "assets/fonts/BungeeInline-Regular.ttf"
        roboto_font_path = "assets/fonts/Roboto-Regular.ttf"

        # Title / subtitle
        self.title_font = Loader.load_font(bungee_font_path, 48)
        self.subtitle_font = Loader.load_font(roboto_font_path, 48)

        # Body / links / meta
        self.body_font = Loader.load_font(roboto_font_path, 18)
        self.small_font = Loader.load_font(roboto_font_path, 18)
        self.toast_font = Loader.load_font(roboto_font_path, 20)
        self.roboto_button_font = Loader.load_font(roboto_font_path, 18)

        # Title
        self.title_surf = self.title_font.render(
            "Typing Shooter: Space Adventure", True, (255, 255, 255)
        )
        self.title_rect = self.title_surf.get_rect(center=(self.width // 2, 90))

        self.subtitle_surf = self.subtitle_font.render(
            "A Fast-Paced Typing Shooter Game", True, (200, 200, 255)
        )
        self.subtitle_rect = self.subtitle_surf.get_rect(center=(self.width // 2, 140))

        # Description
        self.desc_lines = [
            "Hey! Thanks so much for playing my game <3",
            "This little thing started as an itch.io game jam project...",
            "but I got way too ambitious and totally missed the deadline (•_•)",
            "Life's been super busy with other stuff, so this is the version I can share right now.",
            "I wish I could've added more... but I'm still really proud of it!",
            "Building this pushed my brain to its absolute limits and taught me a crazy amount about game dev.",
            "Massive respect to every dev out there — especially solo ones",
            "Pygame is wild: powerful, flexible, but definitely not for the faint of heart.",
            "You can do pretty much anything with it... though next time I'd probably grab a full engine heh.",
            "If you're reading this, you're already awesome. Seriously - thank you for sticking around <3",
            "Feel free to drop a hi on my socials anytime!",
            "Love hearing feedback, ideas, or even your rants ^_^"
        ]

        self.desc_surfaces = [
            self.body_font.render(line, True, (185, 190, 200))
            for line in self.desc_lines
        ]

        # Creator info
        self.creator_text = self.body_font.render(
            "Created by Ashwani", True, (240, 240, 200)
        )
        self.version_text = self.small_font.render(
            f"Version (v{VERSION}) • Made with Pygame",
            True, (170, 170, 170)
        )

        # Links
        link_start_y = self.height - 200
        self.links = [
            ClickableLink(
                "GitHub: AshwaniDev101",
                "https://github.com/AshwaniDev101",
                "https://github.com/AshwaniDev101",
                self.small_font,
                self.width // 2,
                link_start_y,
                self.copy_icon
            ),
            ClickableLink(
                "LinkedIn: ashwanidev101",
                "https://www.linkedin.com/in/ashwanidev101/",
                "https://www.linkedin.com/in/ashwanidev101/",
                self.small_font,
                self.width // 2,
                link_start_y + 35,
                self.copy_icon
            ),
            ClickableLink(
                "X: @AshwaniDev101",
                "https://x.com/AshwaniDev101",
                "https://x.com/AshwaniDev101",
                self.small_font,
                self.width // 2,
                link_start_y + 70,
                self.copy_icon
            ),
            ClickableLink(
                "Email: ashwani.yadav.dev@gmail.com",
                "mailto:ashwani.yadav.dev@gmail.com",
                "ashwani.yadav.dev@gmail.com",
                self.small_font,
                self.width // 2,
                link_start_y + 105,
                self.copy_icon
            ),
        ]

        # Back button (keeps default font internally)
        self.esc_button = HintButton(
            text="Back (Esc)",
            pos=(20, 20),
            # font=pygame.font.Font(None, 18),
            font=self.roboto_button_font,
            can_hover=True
        )

        self.toast_surface = None
        self.toast_until = 0

    def show_toast(self, text, duration=1.2):
        self.toast_surface = self.toast_font.render(text, True, (220, 255, 220))
        self.toast_until = pygame.time.get_ticks() + int(duration * 1000)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        any_link_hover = False

        self.esc_button.update_hover(mouse_pos)
        for link in self.links:
            if link.update(mouse_pos):
                any_link_hover = True

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.esc_button.rect.collidepoint(mouse_pos):
                    self.active = False
                    return "Escape"

                for link in self.links:
                    if link.handle_click(mouse_pos) == "copied":
                        self.show_toast("Copied to clipboard")

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.active = False
                return "Escape"

            elif event.type == pygame.QUIT:
                self.active = False
                return "Exit"

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if any_link_hover else pygame.SYSTEM_CURSOR_ARROW
        )
        return None

    def draw(self):
        self.screen.fill((15, 15, 25))

        self.screen.blit(self.title_surf, self.title_rect)
        self.screen.blit(self.subtitle_surf, self.subtitle_rect)

        y = 180
        for surf in self.desc_surfaces:
            self.screen.blit(surf, (120, y))
            y += 30

        creator_rect = self.creator_text.get_rect(centerx=self.width // 2, top=y + 40)
        self.screen.blit(self.creator_text, creator_rect)

        bunny_rect = self.creator_image.get_rect(
            centerx=self.width // 2, top=creator_rect.bottom + 10
        )
        self.screen.blit(self.creator_image, bunny_rect)

        version_rect = self.version_text.get_rect(
            centerx=self.width // 2, top=bunny_rect.bottom + 15
        )
        self.screen.blit(self.version_text, version_rect)

        for link in self.links:
            link.draw(self.screen)

        self.esc_button.draw(self.screen)

        if self.toast_surface and pygame.time.get_ticks() < self.toast_until:
            rect = self.toast_surface.get_rect(
                centerx=self.width // 2,
                bottom=self.height - 20
            )
            pygame.draw.rect(
                self.screen,
                (40, 60, 40),
                rect.inflate(14, 10),
                border_radius=6
            )
            self.screen.blit(self.toast_surface, rect)
        else:
            self.toast_surface = None

        pygame.display.flip()

    def run(self):
        while self.active:
            events = pygame.event.get()
            action = self.handle_events(events)
            if action:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return action

            self.draw()
            self.clock.tick(60)

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return "Exit"
