import pygame
import sys
import time
import math

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pomodoro Timer")
clock = pygame.time.Clock()

# Load and scale background image
bg = pygame.image.load("timer_run.png").convert()

bg_height = bg.get_height()
bg_width = bg.get_width()
new_height = HEIGHT
new_width = int(bg_width * (new_height / bg_height))
bg = pygame.transform.scale(bg, (new_width, new_height))
bg_width = new_width

# Background scrolling setup
bg_x = 0
scroll_speed = 0  # start stationary

# Fonts for timer
font = pygame.font.Font(None, 80)
small_font = pygame.font.Font(None, 32)

# Timer settings
WORK_DURATION = 25 * 60
BREAK_DURATION = 5 * 60

# Timer state
is_running = False
is_break = False
time_left = WORK_DURATION
last_tick = time.time()

purple = pygame.Color("#C3B1E1")

# --- SPRITE ANIMATION SETUP ---
# Load sprites
working_sprites = [
    pygame.image.load("bunnySprite_right1.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_right2.PNG").convert_alpha()
]

break_sprites = [
    pygame.image.load("bunnySprite_right1.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_right2.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_right1.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_left1.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_left2.PNG").convert_alpha(),
    pygame.image.load("bunnySprite_left1.PNG").convert_alpha()
]

# Scale sprites bigger
SCALE_FACTOR = 2
working_sprites = [pygame.transform.rotozoom(sprite, 0, SCALE_FACTOR) for sprite in working_sprites]
break_sprites = [pygame.transform.rotozoom(sprite, 0, SCALE_FACTOR) for sprite in break_sprites]

current_sprite_index = 0
sprite_change_interval = 0.5
last_sprite_change = time.time()

def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02}:{secs:02}"

def draw_circle_progress(surface, center, radius, progress, color, thickness):
    start_angle = -math.pi / 2
    end_angle = start_angle + 2 * math.pi * progress
    rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    if progress > 0:
        pygame.draw.arc(surface, color, rect, start_angle, end_angle, thickness)

def draw_timer():
    total_time = BREAK_DURATION if is_break else WORK_DURATION
    progress = time_left / total_time if total_time > 0 else 0
    draw_circle_progress(screen, (WIDTH // 2, HEIGHT // 2 - 50), 120, progress, purple, 8)

    timer_text = font.render(format_time(time_left), True, (176, 152, 215))
    screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

    status = "BREAK" if is_break else "WORK"
    status_text = small_font.render(status, True, (118, 77, 186))
    screen.blit(status_text, (20, 20))

    instructions = small_font.render("SPACE = Start/Pause   R = Reset", True, (176, 152, 215))
    screen.blit(instructions, (20, HEIGHT - 40))

running = True
while running:
    clock.tick(60)
    now = time.time()

    # Only move background when timer is running and working
    if is_running and not is_break:
        scroll_speed = 2  # faster scroll speed
    else:
        scroll_speed = 0

    # Scroll background
    bg_x -= scroll_speed
    if bg_x <= -bg_width:
        bg_x = 0

    # Draw scrolling background
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + bg_width, 0))

    # Timer update
    if is_running:
        delta = now - last_tick
        last_tick = now
        time_left -= delta
        if time_left <= 0:
            is_break = not is_break
            time_left = BREAK_DURATION if is_break else WORK_DURATION
            last_tick = time.time()

    # Determine active sprite list
    active_sprites = working_sprites if is_running and not is_break else break_sprites

    # Animate sprite
    if is_running and now - last_sprite_change > sprite_change_interval:
        current_sprite_index = (current_sprite_index + 1) % len(active_sprites)
        last_sprite_change = now
    elif not is_running:
        current_sprite_index = 0

    # Draw current sprite at higher and center position
    current_sprite = active_sprites[current_sprite_index]
    sprite_rect = current_sprite.get_rect()
    sprite_rect.midbottom = (WIDTH // 2, HEIGHT - 100)  # move up (was HEIGHT - 10)
    screen.blit(current_sprite, sprite_rect)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_running = not is_running
                last_tick = time.time()
            elif event.key == pygame.K_r:
                is_running = False
                is_break = False
                time_left = WORK_DURATION

    # Draw timer
    draw_timer()
    pygame.display.flip()

pygame.quit()
sys.exit()

