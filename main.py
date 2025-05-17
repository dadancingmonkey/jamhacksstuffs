import pygame
import sys
import gamesprites
import config
import time
import menus
from pomodoro import PomodoroScreen 


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mindful")
        self.clock = pygame.time.Clock()
        self.running = True
        self.pomodoro_screen = None

        self.init_buttons()
        self.entities()
        self.gameloop()
        self.refresh()

    def init_buttons(self):
        screen_width = self.screen.get_width()
        self.button = menus.ImageButton("images/shop_icon.png", (screen_width, 0), margin=(20, 20), size=(80, 80))
        self.shop_menu = menus.Shop()
        self.shop_open = False

    def give_pomodoro_reward(self):
        self.money += 5
        print("Pomodoro complete! +10 coins.")



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

        self.quest_menu_state = "main"  # could be "main", "quest1", "quest2", "quest3"

        # Setup quest buttons - use increased spacing!
        center_y = 240
        spacing = 220  # <<--- More space!
        button_radius = 36
        screen_w = self.screen.get_width()
        self.quest_buttons = [
            gamesprites.QuestButton(
                (screen_w//2 - spacing, center_y), button_radius, (255, 80, 80),
                "Pomodoro", image_path="images/tomato.png", reward_text="+10 Coins"
            ),
            gamesprites.QuestButton(
                (screen_w//2, center_y), button_radius, (80, 200, 255), "Breathing Exercise",
                reward_text="+2 Coins"
            ),
            gamesprites.QuestButton(
                (screen_w//2 + spacing, center_y), button_radius, (120, 220, 120), "Journaling",
                reward_text="+3 Coins"
            ),
        ]

        close_radius = 24
        close_margin = 24
        close_center = (
            self.screen.get_width() - close_margin - close_radius,
            close_margin + close_radius
        )
        self.menu_close_icon = gamesprites.Quests(close_center, close_radius)

    def quests(self):
        # Draw background image for quest menu
        self.screen.blit(self.menu_bg_sprite.image, self.menu_bg_sprite.rect)

        # Draw the big "Quests" title
        font = pygame.font.SysFont("Arial", 48, bold=True)
        text = font.render("Quests", True, (64, 0, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 40))
        self.screen.blit(self.menu_close_icon.image, self.menu_close_icon.rect)

        if self.quest_menu_state == "main":
            main_font = pygame.font.SysFont("Arial", 28, bold=True)
            reward_font = pygame.font.SysFont("Arial", 20, bold=True)
            for idx, btn in enumerate(self.quest_buttons):
                self.screen.blit(btn.image, btn.rect)

                main_gap = 24  # Gap from button image to main text
                reward_gap = 10  # Gap from main text to reward text

                # Main quest text
                txt = main_font.render(btn.text, True, (32, 32, 32))
                tx = btn.rect.centerx - txt.get_width() // 2
                ty = btn.rect.bottom + main_gap
                self.screen.blit(txt, (tx, ty))

                # Reward text below
                if btn.reward_text:
                    reward_txt = reward_font.render(btn.reward_text, True, (255, 180, 60))
                    rx = btn.rect.centerx - reward_txt.get_width() // 2
                    ry = ty + txt.get_height() + reward_gap
                    self.screen.blit(reward_txt, (rx, ry))
        else:
            # If not in main, show a placeholder for the quest screen
            self.screen.fill((245,245,255))
            self.screen.blit(self.menu_bg_sprite.image, self.menu_bg_sprite.rect)
            quest_font = pygame.font.SysFont("Arial", 40, bold=True)
            quest_text = quest_font.render(f"Quest {self.quest_menu_state[-1]} Screen", True, (120, 40, 40))
            self.screen.blit(quest_text, (self.screen.get_width()//2 - quest_text.get_width()//2, 200))
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
                if seconds_left > 0:
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
        self.button.draw(self.screen)

        if self.shop_open:
            self.shop_menu.draw(self.screen)

        pygame.display.flip()

    def gameloop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            # POMODORO SCREEN HANDLING
            if self.quest_menu_state == "pomodoro" and self.pomodoro_screen:
                pomodoro_running = True
                while pomodoro_running and self.running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.quit()
                            return
                        result = self.pomodoro_screen.handle_event(event)
                        if result == "exit":
                            # Return to quest menu on ESC
                            self.quest_menu_state = "main"
                            self.menu_open = True
                            self.pomodoro_screen = None
                            pomodoro_running = False
                            break

                    if not pomodoro_running:
                        break
                    self.pomodoro_screen.update()
                    self.pomodoro_screen.draw()
                    pygame.display.flip()
                continue  # Skip rest of loop and re-enter main event loop

            # -- Usual event handling below here --
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                # QUEST MENU
                if self.menu_open:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.menu_open = False
                        self.quest_menu_state = "main"
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu_close_icon.is_clicked(event.pos):
                            self.menu_open = False
                            self.quest_menu_state = "main"
                        elif self.quest_menu_state == "main":
                            for idx, btn in enumerate(self.quest_buttons):
                                if btn.is_clicked(event.pos):
                                    if idx == 0:  # Pomodoro button
                                        self.pomodoro_screen = PomodoroScreen(self.screen, self.give_pomodoro_reward)
                                        self.quest_menu_state = "pomodoro"
                                        self.menu_open = False
                                    else:
                                        self.quest_menu_state = f"quest{idx+1}"
                # SHOP MENU
                elif self.shop_open:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.shop_open = False
                    elif event.type == pygame.MOUSEMOTION:
                        self.shop_menu.update_hover(event.pos)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        item_idx = self.shop_menu.item_at_pos(mouse_pos)
                        if item_idx is not None:
                            self.shop_menu.clicked_index = item_idx
                            print("purchased one")
                        else:
                            menu_x, menu_y = self.shop_menu.menu_screen_pos
                            menu_rect = pygame.Rect(menu_x, menu_y, self.shop_menu.width, self.shop_menu.height)
                            if not menu_rect.collidepoint(mouse_pos):
                                self.shop_open = False
                # MAIN GAME
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.plant_tree()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu_icon.is_clicked(event.pos):
                            self.menu_open = True
                            self.quest_menu_state = "main"
                        elif self.button.is_clicked(event.pos):
                            self.shop_open = True

            if self.shop_open:
                mouse_pos = pygame.mouse.get_pos()
                self.shop_menu.update_hover(mouse_pos)

            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.walls)
            for tree in self.trees:
                tree.update(dt)
            self.refresh()
        pygame.quit()
        sys.exit()


    def quit(self):
        self.running = False

game = Game()
