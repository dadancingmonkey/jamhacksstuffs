import pygame
import sys
import gamesprites
import config
import time

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mindful")
        self.clock = pygame.time.Clock()
        self.running = True

        self.entities()
        self.gameloop()
        self.refresh()

    def entities(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.player = None
        self.create_tilemap()
        if self.player:
            self.all_sprites.add(self.player, layer=config.PLAYER_LAYER)
        else:
            self.player = gamesprites.Player((0, 0))
            self.all_sprites.add(self.player, layer=config.PLAYER_LAYER)

        self.money_sprite = gamesprites.Money((0, 0))
        self.money = 3
        self.tree_duration = 10
        self.menu_open = False

        icon_radius = 32
        icon_margin = 24
        icon_center = (
            self.screen.get_width() - icon_margin - icon_radius,
            self.screen.get_height() - icon_margin - icon_radius
        )
        self.menu_icon = gamesprites.Quests(icon_center, icon_radius)

        self.menu_bg_sprite = gamesprites.MenuBackground(self.screen.get_size())


        close_radius = 24
        close_margin = 24
        close_center = (
            self.screen.get_width() - close_margin - close_radius,
            close_margin + close_radius
        )
        self.menu_close_icon = gamesprites.Quests(close_center, close_radius)

    def quests(self):
        # Draw background image
        self.screen.blit(self.menu_bg_sprite.image, self.menu_bg_sprite.rect)
        font = pygame.font.SysFont("Arial", 48, bold=True)
        text = font.render("Quests", True, (64, 0, 0))
        self.screen.blit(
            text, (self.screen.get_width() // 2 - text.get_width() // 2, 40)
        )
        self.screen.blit(self.menu_close_icon.image, self.menu_close_icon.rect)

    def create_tilemap(self):
        for y, row in enumerate(config.tilemap):
            for x, tile in enumerate(row):
                world_x = x * config.TILESIZE
                world_y = y * config.TILESIZE
                if tile == '.':
                    block = gamesprites.Block((world_x, world_y))
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)
                elif tile == '#':
                    tree = gamesprites.Tree((world_x, world_y))
                    self.trees.add(tree)
                    self.all_sprites.add(tree, layer=config.TREES_LAYER)
                elif tile == 'P':
                    self.player = gamesprites.Player((world_x, world_y))
                    block = gamesprites.Block((world_x, world_y))
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)
                elif tile == 'B':
                    wall = gamesprites.Wall((world_x, world_y))
                    self.walls.add(wall)
                    self.all_sprites.add(wall, layer=config.WALLS_LAYER)

    def get_forward_pos(self, player):
        px = round(player.world_pos.x / config.TILESIZE)
        py = round(player.world_pos.y / config.TILESIZE)

        if player.direction == "up":
            py -= 2
        elif player.direction == "down":
            py += 3
        elif player.direction == "left":
            px -= 2
        elif player.direction == "right":
            px += 2

        snapped_x = px * config.TILESIZE
        snapped_y = py * config.TILESIZE
        return pygame.Vector2(snapped_x, snapped_y)

    def plant_tree(self):
        if self.money > 0:
            self.money -= 1
            tile_pos = self.get_forward_pos(self.player)
            new_tree_temp = gamesprites.PlantedTree((tile_pos.x, tile_pos.y), self.tree_duration)

            for tree in self.trees:
                if new_tree_temp.rect.colliderect(tree.rect):
                    return
            for wall in self.walls:
                wall_rect = getattr(wall, 'collision_rect', wall.image.get_rect(topleft=wall.world_pos))
                if new_tree_temp.collision_rect.colliderect(wall_rect):
                    return

            self.trees.add(new_tree_temp)
            self.walls.add(new_tree_temp)
            self.all_sprites.add(new_tree_temp, layer=config.TREES_LAYER)

    def draw_highlight_square(self, screen, player, config):
        forward_pos = self.get_forward_pos(player)
        screen_rect = screen.get_rect()
        screen_x = (forward_pos.x + config.TILESIZE // 2) - player.world_pos.x + screen_rect.centerx
        screen_y = (forward_pos.y + config.TILESIZE // 2) - player.world_pos.y + screen_rect.centery
        highlight_surf = pygame.Surface((config.TILESIZE, config.TILESIZE), pygame.SRCALPHA)
        highlight_surf.fill((255, 0, 0, 60))
        draw_x = screen_x - config.TILESIZE // 2
        draw_y = screen_y - config.TILESIZE // 2
        screen.blit(highlight_surf, (draw_x, draw_y))

    def refresh(self):
        self.screen.fill((135, 206, 235))
        screen_rect = self.screen.get_rect()
        font = pygame.font.SysFont("Arial", 20)

        # Draw ground blocks
        for block in self.ground:
            block_rect = block.image.get_rect(
                topleft=(
                    block.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                    block.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                )
            )
            self.screen.blit(block.image, block_rect)

        # Draw walls
        for wall in self.walls:
            if wall not in self.trees:
                wall_rect = wall.image.get_rect(
                    topleft=(
                        wall.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                        wall.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                    )
                )
                self.screen.blit(wall.image, wall_rect)

        # Draw trees (with timer below)
        for tree in self.trees:
            tree_rect = tree.image.get_rect(
                topleft=(
                    tree.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                    tree.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                )
            )
            self.screen.blit(tree.image, tree_rect)

            if hasattr(tree, "time_left"):
                seconds_left = tree.time_left()
                if seconds_left > 0:   # <--- Only draw timer if greater than 0
                    timer_text = font.render(str(seconds_left), True, (0, 120, 0))
                    text_x = tree_rect.centerx - timer_text.get_width() // 2
                    text_y = tree_rect.bottom + 2
                    self.screen.blit(timer_text, (text_x, text_y))

        self.draw_highlight_square(self.screen, self.player, config)

        # Draw player at center
        player_rect = self.player.image.get_rect(center=screen_rect.center)
        self.screen.blit(self.player.image, player_rect)

        # Draw money
        self.screen.blit(self.money_sprite.image, (16, 16))
        money_font = pygame.font.SysFont("Arial", 24)
        money_text = money_font.render(str(self.money), True, (255, 255, 0))
        self.screen.blit(money_text, (16 + self.money_sprite.image.get_width() + 8, 16))
        self.screen.blit(self.menu_icon.image, self.menu_icon.rect)

        # Draw the menu (if open)
        if self.menu_open:
            self.quests()

        pygame.display.flip()

    def gameloop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if self.menu_open:
                    # Only handle menu-close events
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.menu_open = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu_close_icon.is_clicked(event.pos):
                            self.menu_open = False
                else:
                    # Handle game events when menu is not open
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.plant_tree()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu_icon.is_clicked(event.pos):
                            self.menu_open = True

            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.walls)

            for tree in self.trees:
                tree.update(dt)

            self.refresh()

        pygame.quit()
        sys.exit()

game = Game()
