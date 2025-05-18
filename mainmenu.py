import pygame


class HelpScreen:
    def __init__(self, screen_size):
        self.screen_w, self.screen_h = screen_size
        self.bg_color = (230, 210, 240) 
        self.title_font = pygame.font.SysFont("Ariel", 64, bold=True)
        self.text_font = pygame.font.SysFont("Ariel", 20, bold=True)
        self.back_button_rect = pygame.Rect(30, 30, 80, 80)

        self.arrow_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.arrow_surf,
            (120, 70, 160),  
            [(36, 8), (12, 24), (36, 40)]
        )
        pygame.draw.rect(
            self.arrow_surf,
            (120, 70, 160),
            (24, 20, 16, 8),
            border_radius=3
        )

    def draw(self, surface):
        surface.fill(self.bg_color)

        # Draw title at the top
        title_surf = self.title_font.render("How to Play", True, (160, 90, 170))
        title_rect = title_surf.get_rect(center=(self.screen_w // 2, 50))
        surface.blit(title_surf, title_rect)

        # Draw instructions
        instructions = [
            "Use the WASD keys to move around.",
            "Click on the buttons to open them",
            "Press 'ESC' to leave the menu.",
            "Press SPACE to plant your current seed",
            "Press 1,2,3,4 to select a seed (regular,cherry blossom, tulip, lavender)",
            "1. Complete the therapeutic and beneficial tasks to gain coins",
            "2. Spend coins in the shop to buy new seeds",
            "3. Plant your seeds in the garden",
            "4. Unlock new areas in the garden.",
            "5. Create a beautiful garden for your mind!",
        ]
        y = title_rect.bottom + 20  # start below the title
        for line in instructions:
            text_surf = self.text_font.render(line, True, (80, 55, 120))
            text_rect = text_surf.get_rect(center=(self.screen_w // 2, y))
            surface.blit(text_surf, text_rect)
            y += self.text_font.get_height() + 10  # spacing between lines

        pygame.draw.rect(surface, (220, 200, 240), self.back_button_rect, border_radius=24)
        surface.blit(self.arrow_surf, (self.back_button_rect.x+16, self.back_button_rect.y+16))


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False



class TitleButton:
    def __init__(self, text, center, width=240, height=80, color=(180,255,200,180)):
        self.width = width
        self.height = height
        self.center = center
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont("Comic Sans MS", 54, bold=True)
        self.rect = pygame.Rect(center[0]-width//2, center[1]-height//2, width, height)

    def draw(self, surface):
        button_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, self.color, (0,0,self.width,self.height), border_radius=40)
        text_surf = self.font.render(self.text, True, (120,180,130))
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2))
        button_surf.blit(text_surf, text_rect)
        surface.blit(button_surf, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class TitleScreen:
    def __init__(self, bg_image_path, screen_size):
        self.screen_w, self.screen_h = screen_size
        self.bg = pygame.image.load(bg_image_path).convert()
        self.bg = pygame.transform.scale(self.bg, (self.screen_w, self.screen_h))
        btn_y = self.screen_h//2 + 170
        self.buttons = [
            TitleButton("?", (self.screen_w//2 - 270, btn_y), width=90, height=90),
            TitleButton("START", (self.screen_w//2, btn_y)),
            TitleButton("X", (self.screen_w//2 + 270, btn_y), width=90, height=90)
        ]
        self.title_font = pygame.font.SysFont("Comic Sans MS", 128, bold=True)

    def draw(self, surface):
        surface.blit(self.bg, (0,0))
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 80))
        surface.blit(overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("Mindful", True, (170, 110, 140))
        garden_surf = self.title_font.render("Garden", True, (170, 110, 140))
        surface.blit(title_surf, title_surf.get_rect(center=(self.screen_w//2, self.screen_h//2-80)))
        surface.blit(garden_surf, garden_surf.get_rect(center=(self.screen_w//2, self.screen_h//2+50)))

        # Draw all buttons
        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.buttons):
                if btn.is_clicked(event.pos):
                    return i
        return None

    def get_button_rects(self):
        return [btn.rect for btn in self.buttons]