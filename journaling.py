import pygame, sys

class JournalingScreen:
    def __init__(self, screen, on_exit=None):
        self.screen = screen
        self.on_exit = on_exit
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("images/journal.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.base_font = pygame.font.Font(None, 32)
        self.input_rect = pygame.Rect(50, 50, 700, 500)
        self.bg_colour = pygame.Color("#C3B1E1")
        self.border_colour_active = pygame.Color("#C3B1E1")
        self.border_colour_passive = pygame.Color("#C3B1E1")
        self.user_text = ''
        self.active = True  # Always active in this context
        self.max_width = self.input_rect.width - 10
        self.caret_visible = True
        self.caret_timer = 0
        self.caret_interval = 500
        self.holding_backspace = False
        self.backspace_timer = 0
        self.backspace_delay = 300
        self.backspace_interval = 50
        self.running = True

    def wrap_text(self, text):
        font = self.base_font
        max_width = self.max_width
        lines = []
        for paragraph in text.split('\n'):
            current_line = ''
            for char in paragraph:
                test_line = current_line + char
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            lines.append(current_line)
        return lines

    def count_words(self):
        # Split on spaces/newlines, remove empties
        return len([w for w in self.user_text.replace('\n',' ').split(' ') if w.strip()])

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False  # Allow exit with ESC
                pygame.mixer.music.set_volume(0)
            elif event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
                self.holding_backspace = True
                self.backspace_timer = 0
            elif event.key == pygame.K_RETURN:
                self.user_text += '\n'
            elif event.key == pygame.K_TAB:
                self.user_text += '    '
            else:
                self.user_text += event.unicode

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.holding_backspace = False

    def update(self, dt):
        # Handle caret blink
        self.caret_timer += dt
        if self.caret_timer >= self.caret_interval:
            self.caret_visible = not self.caret_visible
            self.caret_timer = 0

        # Handle backspace repeat
        if self.holding_backspace:
            self.backspace_timer += dt
            if self.backspace_timer > self.backspace_delay:
                if (self.backspace_timer - self.backspace_delay) % self.backspace_interval < dt:
                    self.user_text = self.user_text[:-1]

    def draw(self):
        screen = self.screen
        base_font = self.base_font
        input_rect = self.input_rect
        bg_colour = self.bg_colour

        screen.fill(bg_colour)
        pygame.draw.rect(screen, bg_colour, input_rect)
        pygame.draw.rect(screen, self.border_colour_active, input_rect, 2)

        lines = self.wrap_text(self.user_text)
        y = input_rect.y + 5
        caret_x = input_rect.x + 5
        caret_y = y

        if self.user_text:
            for i, line in enumerate(lines):
                text_surface = base_font.render(line, True, (83, 54, 134))
                screen.blit(text_surface, (input_rect.x + 5, y))
                y += base_font.get_height()
                if i == len(lines) - 1:
                    caret_x = input_rect.x + 5 + base_font.size(line)[0]
                    caret_y = y - base_font.get_height()
        else:
            # Show placeholder if no text
            placeholder_surface = base_font.render("Start journaling! (ESC to exit)", True, (180, 157, 217))
            screen.blit(placeholder_surface, (input_rect.x + 5, input_rect.y + 5))

        # Draw blinking caret
        if self.active and self.caret_visible:
            pygame.draw.line(screen, (83, 54, 134), (caret_x, caret_y), (caret_x, caret_y + base_font.get_height()), 2)

        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        # Calculate coin reward
        word_count = self.count_words()
        coins_earned = word_count // 5
        if self.on_exit:
            self.on_exit(coins_earned)
