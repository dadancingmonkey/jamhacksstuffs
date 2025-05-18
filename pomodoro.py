# pomodoro.py
import pygame
import time
import math

class PomodoroScreen:
    def __init__(self, screen, give_reward_callback):
        self.screen = screen
        self.give_reward_callback = give_reward_callback

        pygame.init()
        """pygame.mixer.init()
        pygame.mixer.music.load("images\study.mp3")
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1)

        self.change_sound = pygame.mixer.Sound("images/change.mp3")   """

        self.WIDTH, self.HEIGHT = screen.get_size()
        self.bg = pygame.image.load("images/timer_run.png").convert()
        bg_height = self.bg.get_height()
        bg_width = self.bg.get_width()
        new_height = self.HEIGHT
        new_width = int(bg_width * (new_height / bg_height))
        self.bg = pygame.transform.scale(self.bg, (new_width, new_height))
        self.bg_width = new_width

        self.bg_x = 0
        self.scroll_speed = 0

        self.font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 32)
        self.WORK_DURATION = 10  # For demo, use 25*60 for real
        self.BREAK_DURATION = 5
        self.is_running = False
        self.is_break = False
        self.time_left = self.WORK_DURATION
        self.last_tick = time.time()
        self.purple = pygame.Color("#C3B1E1")

        self.previous_state = "paused"

        # Sprites
        self.working_sprites = [
            pygame.image.load("images/bunnySprite_right1.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_right2.PNG").convert_alpha()
        ]
        self.break_sprites = [
            pygame.image.load("images/bunnySprite_right1.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_right2.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_right1.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_left1.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_left2.PNG").convert_alpha(),
            pygame.image.load("images/bunnySprite_left1.PNG").convert_alpha()
        ]
        SCALE_FACTOR = 2
        self.working_sprites = [pygame.transform.rotozoom(sprite, 0, SCALE_FACTOR) for sprite in self.working_sprites]
        self.break_sprites = [pygame.transform.rotozoom(sprite, 0, SCALE_FACTOR) for sprite in self.break_sprites]
        self.current_sprite_index = 0
        self.sprite_change_interval = 0.5
        self.last_sprite_change = time.time()

    def format_time(self, seconds):
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02}:{secs:02}"

    def draw_circle_progress(self, center, radius, progress, color, thickness):
        start_angle = -math.pi / 2
        end_angle = start_angle + 2 * math.pi * progress
        rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        if progress > 0:
            pygame.draw.arc(self.screen, color, rect, start_angle, end_angle, thickness)

    def draw(self):
        # Draw scrolling background
        self.screen.blit(self.bg, (self.bg_x, 0))
        self.screen.blit(self.bg, (self.bg_x + self.bg_width, 0))
        # Timer circle and text
        total_time = self.BREAK_DURATION if self.is_break else self.WORK_DURATION
        progress = self.time_left / total_time if total_time > 0 else 0
        self.draw_circle_progress((self.WIDTH // 2, self.HEIGHT // 2 - 50), 120, progress, self.purple, 8)
        timer_text = self.font.render(self.format_time(self.time_left), True, (176, 152, 215))
        self.screen.blit(timer_text, timer_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50)))
        status = "BREAK" if self.is_break else "WORK"
        status_text = self.small_font.render(status, True, (118, 77, 186))
        self.screen.blit(status_text, (20, 20))
        instructions = self.small_font.render("SPACE = Start/Pause   R = Reset   ESC = Quit", True, (176, 152, 215))
        self.screen.blit(instructions, (20, self.HEIGHT - 40))
        # Sprite
        active_sprites = self.working_sprites if self.is_running and not self.is_break else self.break_sprites

        # --- Make sure the index is valid for the current sprite list ---
        if self.current_sprite_index >= len(active_sprites):
            self.current_sprite_index = 0

        current_sprite = active_sprites[self.current_sprite_index]
        sprite_rect = current_sprite.get_rect()
        sprite_rect.midbottom = (self.WIDTH // 2, self.HEIGHT - 100)
        self.screen.blit(current_sprite, sprite_rect)


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.is_running = not self.is_running
                self.last_tick = time.time()
            elif event.key == pygame.K_r:
                self.is_running = False
                self.is_break = False
                self.time_left = self.WORK_DURATION
            elif event.key == pygame.K_ESCAPE:
                pygame.mixer.music.set_volume(0)
                return "exit"

    def update(self):
        now = time.time()
        # Only move background when timer is running and working
        self.scroll_speed = 2 if self.is_running and not self.is_break else 0
        self.bg_x -= self.scroll_speed
        if self.bg_x <= -self.bg_width:
            self.bg_x = 0
        # Timer update
        if self.is_running:
            delta = now - self.last_tick
            self.last_tick = now
            self.time_left -= delta
            current_state = "break" if self.is_break else "work"
            if self.time_left <= 0:
                if self.is_break:
                    # Finished break, go back to work session
                    self.is_break = False
                    self.time_left = self.WORK_DURATION
                    self.last_tick = time.time()
                else:
                    # Finished work session, reward!
                    self.give_reward_callback()
                    self.is_break = True
                    self.time_left = self.BREAK_DURATION
                    self.last_tick = time.time()
        else:
            current_state = "paused"

        if current_state != self.previous_state:
            """self.change_sound.play()"""
            self.previous_state = current_state
        # Animate sprite
        active_sprites = self.working_sprites if self.is_running and not self.is_break else self.break_sprites
        if self.is_running and now - self.last_sprite_change > self.sprite_change_interval:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(active_sprites)
            self.last_sprite_change = now
        elif not self.is_running:
            self.current_sprite_index = 0
