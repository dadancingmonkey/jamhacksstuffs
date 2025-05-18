import pygame
import config


def remove(map_rows):
    for x in range (97):
        for y in range(63):
            if map_rows[y][x] != 'P':
                if map_rows[y][x] == 'B':
                    map_rows[y][x] = '.'

    


def update_tilemap_with_owned_land(owned_tiles, tilemap):
    map_rows = [list(row) for row in tilemap]
    remove(map_rows)
    
    
    
    width = 0
    length = 0
    lr=1
    lc=1
    hr=1
    hc=1
    for r, c in owned_tiles:
        if r < lr:
            lr=r
        if c < lc:
            lc=c
        if c > hc:
            hc = c
        if r > hr:
            hr = r
        
        

        length = ((hr-lr)+1)*21
         
        width = ((hc-lc)+1)*32
        


    
    for y in range(width):
        map_rows[((lr*21+1))][(lc*32+1+y)] = 'B'
        map_rows[((lr*21+1)+length-1)][(lc*32+1+y)] = 'B'

    for x in range(length):
        map_rows[(lr*21+1+x)][((lc*32+1)-1)] = 'B'
        map_rows[(lr*21+1+x)][((lc*32+1)+width-1)] = 'B'

    return [''.join(row) for row in map_rows]




class MapIcon:
    ICON_SIZE = (80, 80)
    MARGIN = 10

    def __init__(self, screen_size, icon_path="images/map icon.png"):


    
        self.image_raw = pygame.image.load(icon_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image_raw, self.ICON_SIZE)
        self.rect = self.image.get_rect()
        self.screen_size = screen_size
        self.set_position(screen_size)
        self.clicked = False

    def set_position(self, screen_size):
        # Position at bottom-left corner with margin
        self.rect.topleft = (self.MARGIN, screen_size[1] - self.rect.height - self.MARGIN)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True

    def was_clicked(self):
        if self.clicked:
            self.clicked = False
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)



import random

class LandPurchaseMenu:
    GRID_SIZE = 3
    RAW_TILE_SIZE = 16
    SCALE = 8
    TILE_SIZE = RAW_TILE_SIZE * SCALE
    GRID_PIX = GRID_SIZE * RAW_TILE_SIZE
    GRID_DISPLAY = GRID_PIX * SCALE

    GRID_MENU_MARGIN = 56  
    TITLE_MARGIN = 48
    BUTTONS_AREA = 120
    GRID_BUTTON_SPACING = 34

    WIDTH = GRID_DISPLAY + 2 * GRID_MENU_MARGIN
    HEIGHT = TITLE_MARGIN + GRID_DISPLAY + 2 * GRID_MENU_MARGIN + BUTTONS_AREA


    PURCHASE_ORDER = [
        ([(0,1)], 40),                        
        ([(0,2), (1,2)], 50),                  
        ([(2,2), (2,1)], 60),                  
        ([(0,0), (1,0), (2,0)], 80),            
    ]

    def __init__(self, screen_size, get_money_func=None, spend_money_func=None):
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.rect = self.surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2))
        self.active = False

        self.owned_tiles = set([(1, 1)])
        self.pending_tiles = set()
        self.grid_surface = pygame.Surface((self.GRID_PIX, self.GRID_PIX))

        self.buy_buttons = {}
        self.update_buy_buttons()

        btn_w, btn_h = 90, 40
        space = 28
        y_base = self.TITLE_MARGIN + self.GRID_MENU_MARGIN + self.GRID_DISPLAY + 44
        self.cancel_rect = pygame.Rect(self.WIDTH//2 - btn_w - space//2, y_base, btn_w, btn_h)
        self.done_rect = pygame.Rect(self.WIDTH//2 + space//2, y_base, btn_w, btn_h)

        # Cost functions
        self.get_money = get_money_func
        self.spend_money = spend_money_func
        self.last_purchase_failed = False
        self.failed_timer = 0


    def next_spiral_candidates(self):
        center = (1, 1) 
        seen = set(self.owned_tiles)
        max_ring = self.GRID_SIZE
        candidates = []
        for ring in range(1, max_ring+1):
            positions = []
            for dc in range(-ring+1, ring+1):
                positions.append((center[0]-ring, center[1]+dc))
            for dr in range(-ring+1, ring+1):
                positions.append((center[0]+dr, center[1]+ring))
            for dc in range(ring-1, -ring-1, -1):
                positions.append((center[0]+ring, center[1]+dc))
            for dr in range(ring-1, -ring-1, -1):
                positions.append((center[0]+dr, center[1]-ring))
            for pos in positions:
                if pos not in seen and self.is_adjacent_to_owned(pos):
                    candidates.append(pos)
            if candidates:
                break
        return [pos for pos in candidates if self.is_valid_plot(pos)]
    def is_adjacent_to_owned(self, pos):
        r, c = pos
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbor = (r+dr, c+dc)
            if neighbor in self.owned_tiles:
                return True
        return False

    def is_valid_plot(self, pos):
        r, c = pos
        return 0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE


    def get_group_center(self, tiles):
        """Returns pixel coords of the center of a group of (r, c) tiles."""
        if not tiles:
            return 0, 0
        avg_r = sum(r for r, c in tiles) / len(tiles)
        avg_c = sum(c for r, c in tiles) / len(tiles)
        # Pixel coords
        x = self.GRID_MENU_MARGIN + int((avg_c + 0.5) * self.TILE_SIZE)
        y = self.TITLE_MARGIN + self.GRID_MENU_MARGIN + int((avg_r + 0.5) * self.TILE_SIZE)
        return x, y

    def update_buy_buttons(self):
        self.buy_buttons = {}
        btn_w, btn_h = 90, 40

        purchased = set(self.owned_tiles) | set(self.pending_tiles)

        for i, (plots, price) in enumerate(self.PURCHASE_ORDER):
            group_pending = any(p not in purchased for p in plots)
            if group_pending:
                x, y = self.get_group_center(plots)
                btn_rect = pygame.Rect(x - btn_w//2, y - btn_h//2, btn_w, btn_h)
                self.buy_buttons[i] = {
                    "rect": btn_rect,
                    "price": price,
                    "locked": False,
                    "plots": plots,
                    "group": i,
                }
                # All remaining groups are locked
                for j in range(i+1, len(self.PURCHASE_ORDER)):
                    x2, y2 = self.get_group_center(self.PURCHASE_ORDER[j][0])
                    btn_rect2 = pygame.Rect(x2 - btn_w//2, y2 - btn_h//2, btn_w, btn_h)
                    self.buy_buttons[j] = {
                        "rect": btn_rect2,
                        "price": self.PURCHASE_ORDER[j][1],
                        "locked": True,
                        "plots": self.PURCHASE_ORDER[j][0],
                        "group": j,
                    }
                break




    def open(self):
        self.active = True
        self.pending_tiles.clear()
        self.update_buy_buttons()

    def close(self):
        self.active = False
        self.pending_tiles.clear()
        self.update_buy_buttons()

    def handle_event(self, event):
        print("LandPurchaseMenu.handle_event called, active:", self.active)
        if not self.active:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            rel_x, rel_y = mx - self.rect.left, my - self.rect.top
            for group_idx, btn in self.buy_buttons.items():
                if btn["rect"].collidepoint((rel_x, rel_y)) and not btn["locked"]:
                    for plot in btn["plots"]:
                        if plot not in self.owned_tiles:
                            self.pending_tiles.add(plot)
                    self.update_buy_buttons()
                    return ("pending", group_idx, btn["plots"])

            if self.done_rect.collidepoint((rel_x, rel_y)):
                # Calculate total cost for pending tiles
                total_cost = 0
                for group_idx, btn in self.buy_buttons.items():
                    if any(plot in self.pending_tiles for plot in btn["plots"]):
                        total_cost += btn["price"]
                # Check if player has enough money
                if self.spend_money is not None and total_cost > 0:
                    if not self.spend_money(total_cost):
                        # Not enough money, abort purchase (optionally show a message)
                        return None
                self.owned_tiles.update(self.pending_tiles)
                purchased = list(self.pending_tiles)
                self.pending_tiles.clear()
                # Update tilemap with all owned land
                config.tilemap = update_tilemap_with_owned_land(self.owned_tiles, config.tilemap)
                self.update_buy_buttons()
                self.active = False
                return ("done", purchased)
            if self.cancel_rect.collidepoint((rel_x, rel_y)):
                self.pending_tiles.clear()
                self.update_buy_buttons()
                self.active = False
                return "cancel"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pending_tiles.clear()
            self.update_buy_buttons()
            self.active = False
            return "cancel"
        return None

    def draw_pixel_grass(self, surf, tile_rect, seed):
        random.seed(seed)
        grass_colors = [
            (54, 168, 60), (38, 136, 43), (74, 189, 84),
            (60, 155, 48), (83, 208, 93), (101, 183, 86)
        ]
        for y in range(tile_rect.top, tile_rect.bottom):
            for x in range(tile_rect.left, tile_rect.right):
                color = random.choice(grass_colors)
                surf.set_at((x, y), color)
        swirl_colors = [(80,220,100), (150,255,130), (24,120,30)]
        num_swirls = 3 + random.randint(0,2)
        for _ in range(num_swirls):
            cx = random.randint(tile_rect.left+3, tile_rect.right-4)
            cy = random.randint(tile_rect.top+3, tile_rect.bottom-4)
            for l in range(6, 12):
                dx = int(l * 0.25 * random.uniform(0.7, 1.3) * random.choice([-1, 1]))
                dy = int(l * 0.18 * random.uniform(0.7, 1.3) * random.choice([-1, 1]))
                px = cx + dx
                py = cy + dy
                if tile_rect.left <= px < tile_rect.right and tile_rect.top <= py < tile_rect.bottom:
                    surf.set_at((px, py), random.choice(swirl_colors))

    def draw_pixel_grid(self):
        self.grid_surface.fill((48, 48, 48))
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                x = c * self.RAW_TILE_SIZE
                y = r * self.RAW_TILE_SIZE
                rect = pygame.Rect(x, y, self.RAW_TILE_SIZE, self.RAW_TILE_SIZE)
                if (r, c) in self.owned_tiles:
                    self.draw_pixel_grass(self.grid_surface, rect, seed=100 + r*10 + c)
                    pygame.draw.rect(self.grid_surface, (34, 140, 30), rect, 2)
                elif (r, c) in self.pending_tiles:
                    self.grid_surface.fill((200, 205, 60), rect)
                    pygame.draw.rect(self.grid_surface, (140, 140, 30), rect, 2)
                else:
                    self.grid_surface.fill((88, 88, 88), rect)
                    pygame.draw.rect(self.grid_surface, (60, 60, 60), rect, 2)
        pygame.draw.rect(self.grid_surface, (20, 20, 20), self.grid_surface.get_rect(), 2)

    def draw_lock_icon(self, surf, rect):
        # Simple lock: body + shackle
        pygame.draw.rect(surf, (180,180,180), (rect.x+4, rect.y+8, rect.width-8, rect.height-10))
        pygame.draw.rect(surf, (90,90,90), (rect.x+4, rect.y+8, rect.width-8, rect.height-10), 2)
        # Shackle
        pygame.draw.arc(surf, (90,90,90), (rect.x+5, rect.y+2, rect.width-10, rect.height-10), 3.14, 0, 2)
        # Keyhole
        cx = rect.centerx
        cy = rect.y + rect.height//2 + 2
        pygame.draw.circle(surf, (40,40,40), (cx, cy), 2)
        pygame.draw.rect(surf, (40,40,40), (cx-1, cy+2, 2, 4))


    def draw(self, surface):
        if not self.active:
            return
        self.surface.fill((38, 35, 34))
        pygame.draw.rect(self.surface, (78, 52, 36), self.surface.get_rect(), 10) 

        font = pygame.font.SysFont("Consolas", 28, bold=True)
        title = font.render("Buy Land", True, (180, 255, 180))
        self.surface.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 20))

        self.draw_pixel_grid()
        grid_x = self.GRID_MENU_MARGIN
        grid_y = self.TITLE_MARGIN + self.GRID_MENU_MARGIN
        self.surface.blit(
            pygame.transform.scale(self.grid_surface, (self.GRID_DISPLAY, self.GRID_DISPLAY)),
            (grid_x, grid_y)
        )
        btn_font = pygame.font.SysFont("Consolas", 18, bold=True)
        for group_idx, btn in self.buy_buttons.items():
            color = (66, 110, 255) if not btn["locked"] else (90, 90, 90)
            border = (24, 44, 160) if not btn["locked"] else (48, 48, 60)
            pygame.draw.rect(self.surface, color, btn["rect"])
            pygame.draw.rect(self.surface, border, btn["rect"], 4)
            # Draw price if unlocked
            if not btn["locked"]:
                text = btn_font.render(str(btn["price"]), True, (255, 255, 255))
                self.surface.blit(text, (btn["rect"].centerx - text.get_width()//2, btn["rect"].centery - text.get_height()//2))
            else:
                # Draw lock icon
                lock_rect = btn["rect"].copy()
                lock_rect.width = min(lock_rect.width, 22)
                lock_rect.height = min(lock_rect.height, 18)
                lock_rect.center = btn["rect"].center
                self.draw_lock_icon(self.surface, lock_rect)

        # DRAW DONE & CANCEL BUTTONS
        pygame.draw.rect(self.surface, (44, 160, 64), self.done_rect)
        pygame.draw.rect(self.surface, (28, 80, 32), self.done_rect, 4)
        done_text = btn_font.render("Done", True, (255, 255, 255))
        self.surface.blit(done_text, (self.done_rect.centerx - done_text.get_width()//2, self.done_rect.centery - done_text.get_height()//2))

        pygame.draw.rect(self.surface, (180, 50, 44), self.cancel_rect)
        pygame.draw.rect(self.surface, (120, 24, 24), self.cancel_rect, 4)
        cancel_text = btn_font.render("Cancel", True, (255, 255, 255))
        self.surface.blit(cancel_text, (self.cancel_rect.centerx - cancel_text.get_width()//2, self.cancel_rect.centery - cancel_text.get_height()//2))

        surface.blit(self.surface, self.rect)
