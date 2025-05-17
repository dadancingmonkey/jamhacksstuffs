# breathing.py
import pygame
import math

class BreathingScreen:
    def __init__(self, screen, give_reward_callback=None):
        self.screen = screen
        self.give_reward_callback = give_reward_callback  # Called at end of cycle (optional)

        self.WIDTH, self.HEIGHT = screen.get_size()
        self.font = pygame.font.SysFont('helvetica', 40)

        self.current_frame = 0
        self.new = 0
        self.radius = 150
        self.radius2 = 85
        self.moving = True
        self.speed_changer = 1
        self.text_str = "Breath in..."
        self.cycle_completed = False

        self.bg_color = (195, 177, 225)
        self.circle_color = (150, 111, 214)
        self.inner_circle_color = (75, 56, 107)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "exit"
        if event.type == pygame.QUIT:
            return "exit"
        return None

    def update(self):
        if self.moving:
            self.current_frame += 1
        self.new += 1

        # Animation speed logic
        if self.moving:
            speed = ((5*math.pi)/(6*self.speed_changer)) * math.sin((math.pi*self.current_frame)/(60*self.speed_changer))
            speed2 = ((5*math.pi)/(4*self.speed_changer)) * math.sin((math.pi*self.current_frame)/(60*self.speed_changer))
        else:
            speed = 0
            speed2 = 0

        self.radius += speed
        self.radius2 += speed2

        # State transitions (timing logic)
        if self.new == 60:
            self.text_str = "Hold..."
            self.moving = False
        elif self.new == 120:
            self.text_str = "Breath out..."
            self.moving = True
            self.current_frame = 120
            self.speed_changer = 2
        elif self.new == 240:
            self.text_str = "Hold..."
            self.current_frame = 120
            self.moving = False
        elif self.new == 300:
            self.text_str = "Breath in..."
            self.new = 0
            self.speed_changer = 1
            self.current_frame = 0
            self.moving = True
            # Reward here after a full cycle if desired
            if self.give_reward_callback:
                self.give_reward_callback()

    def draw(self):
        self.screen.fill(self.bg_color)
        pygame.draw.circle(self.screen, self.circle_color, (400, 300), int(self.radius))
        pygame.draw.circle(self.screen, self.inner_circle_color, (400, 300), int(self.radius2))
        text_surface = self.font.render(self.text_str, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 300))
        self.screen.blit(text_surface, text_rect)
