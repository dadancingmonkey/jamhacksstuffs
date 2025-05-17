import pygame, sys

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([800, 600])
base_font = pygame.font.Font(None, 32)
user_text = ''

input_rect = pygame.Rect(50, 50, 700, 500)
bg_colour = pygame.Color("#C3B1E1")
border_colour_active = pygame.Color("#C3B1E1")
border_colour_passive = pygame.Color("#C3B1E1")

active = False
max_width = input_rect.width - 10
caret_visible = True
caret_timer = 0
caret_interval = 500  # milliseconds

holding_backspace = False
backspace_timer = 0
backspace_delay = 300  # ms before repeating starts
backspace_interval = 50  # repeat rate after initial delay

def wrap_text(text, font, max_width):
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
        lines.append(current_line)  # Add last line of paragraph
    return lines

while True:
    dt = clock.tick(60)
    caret_timer += dt
    if caret_timer >= caret_interval:
        caret_visible = not caret_visible
        caret_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = active
            active = input_rect.collidepoint(event.pos)
            if active and not was_active:
                caret_visible = True
                caret_timer = 0

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
                holding_backspace = True
                backspace_timer = 0  # reset timer
            elif event.key == pygame.K_RETURN:
                user_text += '\n'
            elif event.key == pygame.K_TAB:
                user_text += '    '
            else:
                user_text += event.unicode

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                holding_backspace = False

        # Handle backspace repeat
    if holding_backspace and active:
        backspace_timer += dt
        if backspace_timer > backspace_delay:
            # Repeat delete at set interval
            if (backspace_timer - backspace_delay) % backspace_interval < dt:
                user_text = user_text[:-1]


    screen.fill(bg_colour)

    # Draw input box background and border
    pygame.draw.rect(screen, bg_colour, input_rect)
    pygame.draw.rect(screen, border_colour_active if active else border_colour_passive, input_rect, 2)

    lines = wrap_text(user_text, base_font, max_width)
    y = input_rect.y + 5
    caret_x = input_rect.x + 5
    caret_y = y

    if user_text:
        for i, line in enumerate(lines):
            text_surface = base_font.render(line, True, (83, 54, 134))  # Dark purple
            screen.blit(text_surface, (input_rect.x + 5, y))
            y += base_font.get_height()
            if i == len(lines) - 1:
                caret_x = input_rect.x + 5 + base_font.size(line)[0]
                caret_y = y - base_font.get_height()
    elif not active:
        # Show placeholder only if inactive and there's no user text
        placeholder_surface = base_font.render("click here to type!", True, (180, 157, 217))
        screen.blit(placeholder_surface, (input_rect.x + 5, input_rect.y + 5))


    # Draw blinking caret even if no text yet
    if active and caret_visible:
        pygame.draw.line(screen, (83, 54, 134), (caret_x, caret_y), (caret_x, caret_y + base_font.get_height()), 2)

    # Draw blinking caret even if no text yet
    if active and caret_visible:
        pygame.draw.line(screen, (83, 54, 134), (caret_x, caret_y), (caret_x, caret_y + base_font.get_height()), 2)


    pygame.display.flip()

