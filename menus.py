import pygame

import config
import gamesprites


class ImageButton:
    def __init__(self, image_path, topright, margin=(0, 0), size = None):
        image = pygame.image.load(image_path).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topright = (topright[0] - margin[0], topright[1] + margin[1])

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    

class Shop:
    def __init__(self, width=400, height=400):
        self.width = width
        self.height = height

        # Load your item images
        self.item_images = [
            pygame.image.load("images/tulip (1).png").convert_alpha(),
            pygame.image.load("images/lavender (1).png").convert_alpha(),
            pygame.image.load("images/tree_green.png").convert_alpha(),
            pygame.image.load("images/tree_pink.png").convert_alpha(),
        ]

        self.item_size = 96  # Each item will be 96x96 pixels
        self.item_images = [
            pygame.transform.scale(img, (self.item_size, self.item_size))
            for img in self.item_images
        ]
        self.item_rects = [None] * 4  # To store rects for click detection
        self.menu_screen_pos = (0, 0)  # To store menu top-left on screen

        self.hovered_index = None
        self.clicked_index = None

    def draw(self, surface):
        screen_rect = surface.get_rect()
        menu_x = screen_rect.centerx - self.width // 2
        menu_y = screen_rect.centery - self.height // 2
        self.menu_screen_pos = (menu_x, menu_y)

        menu_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        menu_surf.fill((216, 205, 235, 240))
        pygame.draw.rect(menu_surf, (97, 63, 157), menu_surf.get_rect(), 4)

        font = pygame.font.SysFont("Arial", 48, bold=True)
        text_surf = font.render("SHOP", True, (97, 63, 157))
        text_rect = text_surf.get_rect(center=(self.width // 2, 50))
        menu_surf.blit(text_surf, text_rect)

        grid_margin = 80
        spacing = 60
        start_x = grid_margin
        start_y = 100

        for i, img in enumerate(self.item_images):
            row = i // 2
            col = i % 2
            x = start_x + col * (self.item_size + spacing)
            y = start_y + row * (self.item_size + spacing)
            menu_surf.blit(img, (x, y))
            self.item_rects[i] = pygame.Rect(x, y, self.item_size, self.item_size)

            # HOVER highlight
            if i == self.hovered_index:
                highlight_surf = pygame.Surface((self.item_size, self.item_size), pygame.SRCALPHA)
                highlight_surf.fill((150, 150,150, 80))  # Light gray, alpha=80
                menu_surf.blit(highlight_surf, (x, y))

            # CLICK highlight
            if i == self.clicked_index:
                click_surf = pygame.Surface((self.item_size, self.item_size), pygame.SRCALPHA)
                click_surf.fill((120, 120, 120, 120))    # Dark gray, alpha=120
                menu_surf.blit(click_surf, (x, y))


        surface.blit(menu_surf, (menu_x, menu_y))

    def item_at_pos(self, mouse_pos):
        """
        mouse_pos: (x, y) tuple in screen coordinates.
        Returns: the index of the clicked item (0-3), or None.
        """
        menu_x, menu_y = self.menu_screen_pos
        rel_x = mouse_pos[0] - menu_x
        rel_y = mouse_pos[1] - menu_y
        for i, rect in enumerate(self.item_rects):
            if rect and rect.collidepoint(rel_x, rel_y):
                return i
        return None
    
    def update_hover(self, mouse_pos):
        idx = self.item_at_pos(mouse_pos)
        self.hovered_index = idx