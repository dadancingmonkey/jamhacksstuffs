import pygame
import sys
import time
import math

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pomodoro Timer")

# Fonts
font = pygame.font.Font(None, 120)
small_font = pygame.font.Font(None, 48)

# Timer settings
WORK_DURATION = 1 * 60  # 25 minutes
BREAK_DURATION = 5 * 60  # 5 minutes

# State
is_running = False
is_break = False
time_left = WORK_DURATION
last_tick = time.time()

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
    screen.fill((255, 255, 255))  # White background

    total_time = BREAK_DURATION if is_break else WORK_DURATION
    progress = time_left / total_time

    # Draw progress circle (larger now)
    draw_circle_progress(screen, (WIDTH // 2, HEIGHT // 2), 200, progress, (0, 0, 0), 12)

    # Draw timer text
    timer_text = font.render(format_time(time_left), True, (0, 0, 0))
    screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    # Status label
    status = "BREAK" if is_break else "WORK"
    status_text = small_font.render(status, True, (0, 0, 0))
    screen.blit(status_text, (20, 20))

    # Instructions
    instructions = small_font.render("SPACE = Start/Pause   R = Reset", True, (0, 0, 0))
    screen.blit(instructions, (20, HEIGHT - 60))

# Main loop
clock = pygame.time.Clock()
while True:
    clock.tick(60)

    if is_running:
        now = time.time()
        delta = now - last_tick
        last_tick = now
        time_left -= delta
        if time_left <= 0:
            is_break = not is_break
            time_left = BREAK_DURATION if is_break else WORK_DURATION
            last_tick = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_running = not is_running
                last_tick = time.time()
            elif event.key == pygame.K_r:
                is_running = False
                is_break = False
                time_left = WORK_DURATION

    draw_timer()
    pygame.display.flip()