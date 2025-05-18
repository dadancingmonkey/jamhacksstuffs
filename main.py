import pygame
import sys
import gamesprites
import config
import time
import menus
from pomodoro import PomodoroScreen 
from mainmenu import TitleScreen, HelpScreen
from breathing import BreathingScreen
import map




class Game:
    
    STATE_MENU = 0
    STATE_HELP = 1
    STATE_PLAY = 2
    STATE_POMODORO = 3
    STATE_BREATHING = 4
    STATE_JOURNALING = 5

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600)) 
        pygame.display.set_caption("Mindful")
        self.clock = pygame.time.Clock()
        self.running = True
        self.pomodoro_screen = None
        self.breathing_screen = None

        self.land_menu = map.LandPurchaseMenu(self.screen.get_size())

        self.title_screen = TitleScreen("images/main_title_bg.png", (800, 600))
        self.help_screen = HelpScreen((800, 600))
        self.state = self.STATE_MENU
        self.map_icon = map.MapIcon(self.screen.get_size(), "map icon.png")

        self.init_buttons()
        self.entities()  # <-- Must come before reload_tilemap()

        config.tilemap = map.update_tilemap_with_owned_land(self.land_menu.owned_tiles, config.tilemap)
        self.reload_tilemap()  # <-- Now safe to call here!

    def give_journaling_reward(self, coins):
        self.money += coins
        print("Journaling complete!",coins, "coins.")

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
        self.tree_green_seed_sprite = gamesprites.Green((0, 30))
        self.tree_pink_seed_sprite = gamesprites.Pink((0, 60))
        self.tulip_sprite = gamesprites.Tulip((0, 90))
        self.lavender_sprite = gamesprites.Lavender((0, 120))
        self.money = 10
        self.green_seeds = 0
        self.pink_seeds = 0
        self.tulip_seeds = 0
        self.lavender_seeds = 0
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

        self.quest_menu_state = "main" 

        center_y = 240
        spacing = 220 
        button_radius = 36
        screen_w = self.screen.get_width()
        self.quest_buttons = [
            gamesprites.QuestButton(
                (screen_w//2 - spacing, center_y), button_radius, (255, 80, 80),
                "Pomodoro", image_path="images/tomato.png", reward_text="+10 Coins"
            ),
            gamesprites.QuestButton(
                (screen_w//2, center_y), button_radius, (80, 200, 255), "Breathing Exercise",
                image_path="images/breathing_icon.png",reward_text="+2 Coins"
            ),
            gamesprites.QuestButton(
                (screen_w//2 + spacing, center_y), button_radius, (120, 220, 120), "Journaling",
                image_path="images/journal_icon.png", reward_text="+3 Coins"
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
        self.screen.blit(self.menu_bg_sprite.image, self.menu_bg_sprite.rect)

        font = pygame.font.SysFont("Arial", 48, bold=True)
        text = font.render("Quests", True, (64, 0, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 40))
        self.screen.blit(self.menu_close_icon.image, self.menu_close_icon.rect)

        if self.quest_menu_state == "main":
            main_font = pygame.font.SysFont("Arial", 28, bold=True)
            reward_font = pygame.font.SysFont("Arial", 20, bold=True)
            for idx, btn in enumerate(self.quest_buttons):
                self.screen.blit(btn.image, btn.rect)

                main_gap = 24  
                reward_gap = 10  

                txt = main_font.render(btn.text, True, (32, 32, 32))
                tx = btn.rect.centerx - txt.get_width() // 2
                ty = btn.rect.bottom + main_gap
                self.screen.blit(txt, (tx, ty))

                if btn.reward_text:
                    reward_txt = reward_font.render(btn.reward_text, True, (255, 180, 60))
                    rx = btn.rect.centerx - reward_txt.get_width() // 2
                    ry = ty + txt.get_height() + reward_gap
                    self.screen.blit(reward_txt, (rx, ry))
        else:
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
                    block = gamesprites.Block((world_x, world_y),'light1')
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)
                elif tile == 'D':
                    block = gamesprites.Block((world_x, world_y),'dark1')
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)
                elif tile == 'U':
                    block = gamesprites.Block((world_x, world_y),'dark2')
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)
                elif tile == 'O':
                    block = gamesprites.Block((world_x, world_y),'light2')
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER) 
                elif tile == 'W':
                    water = gamesprites.Water((world_x, world_y), 'dark3')
                    self.ground.add(water)
                    self.all_sprites.add(water, layer=config.BLOCKS_LAYER)
                    self.walls.add(water)
                elif tile == 'X':
                    water = gamesprites.Water((world_x, world_y), 'dark4')
                    self.ground.add(water)
                    self.all_sprites.add(water, layer=config.BLOCKS_LAYER)
                    self.walls.add(water)
                elif tile == '#':
                    tree = gamesprites.Tree((world_x, world_y))
                    self.trees.add(tree)
                    self.all_sprites.add(tree, layer=config.TREES_LAYER)
                elif tile == 'P':
                    self.player = gamesprites.Player((world_x, world_y))
                    block = gamesprites.Block((world_x, world_y),'light1')
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
        if self.green_seeds > 0:
            self.green_seeds -= 1
            tile_pos = self.get_forward_pos(self.player)
            new_tree_temp = gamesprites.PlantedTree(
                (tile_pos.x, tile_pos.y),
                growing_time=10,
                growth_img_path="images/growth_tree_green.png",
                grown_img_path="images/tree_green.png"
            )
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

    def plant_lavender(self):
        if self.lavender_seeds > 0:
            self.lavender_seeds -= 1
            tile_pos = self.get_forward_pos(self.player)
            new_flower = gamesprites.PlantedTree(
                (tile_pos.x, tile_pos.y),
                growing_time=5,
                growth_img_path="images/lavender_growth.png",
                grown_img_path="images/lavender.png",
                type = "flower"
            )
            for flower in self.trees:
                if new_flower.rect.colliderect(flower.rect):
                    return
            for wall in self.walls:
                wall_rect = getattr(wall, 'collision_rect', wall.image.get_rect(topleft=wall.world_pos))
                if new_flower.collision_rect.colliderect(wall_rect):
                    return
            self.trees.add(new_flower) 
            self.walls.add(new_flower)
            self.all_sprites.add(new_flower, layer=config.TREES_LAYER)


    def plant_tulip(self):
        if self.tulip_seeds > 0:
            self.tulip_seeds -= 1
            tile_pos = self.get_forward_pos(self.player)
            new_flower = gamesprites.PlantedTree(
                (tile_pos.x, tile_pos.y),
                growing_time=5,
                growth_img_path="images/tulip_growth.png",
                grown_img_path="images/tulip.png",
                type = "flower"
            )
            for flower in self.trees: 
                if new_flower.rect.colliderect(flower.rect):
                    return
            for wall in self.walls:
                wall_rect = getattr(wall, 'collision_rect', wall.image.get_rect(topleft=wall.world_pos))
                if new_flower.collision_rect.colliderect(wall_rect):
                    return
            self.trees.add(new_flower)   
            self.walls.add(new_flower)
            self.all_sprites.add(new_flower, layer=config.TREES_LAYER)


    def plant_pink_tree(self):
        if self.pink_seeds > 0:
            self.pink_seeds -= 1
            tile_pos = self.get_forward_pos(self.player)
            new_tree = gamesprites.PlantedTree(
                (tile_pos.x, tile_pos.y),
                growing_time=5,
                growth_img_path="images/growth_tree_pink.png",
                grown_img_path="images/tree_pink.png",
            )
            for tree in self.trees:
                if new_tree.rect.colliderect(tree.rect):
                    return
            for wall in self.walls:
                wall_rect = getattr(wall, 'collision_rect', wall.image.get_rect(topleft=wall.world_pos))
                if new_tree.collision_rect.colliderect(wall_rect):
                    return
            self.trees.add(new_tree)
            self.walls.add(new_tree)
            self.all_sprites.add(new_tree, layer=config.TREES_LAYER)


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

    def give_breathing_reward(self):
        self.money += 1
        print("Completed a breathing cycle! +1 coin.")


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

        # Draw green seeds below money
        green_icon_y = 16 + self.money_sprite.image.get_height() + 6
        self.screen.blit(self.tree_green_seed_sprite.image, (16, green_icon_y))
        green_font = pygame.font.SysFont("Arial", 24)
        green_text = green_font.render(str(self.green_seeds), True, (80, 180, 120))
        self.screen.blit(green_text, (16 + self.tree_green_seed_sprite.image.get_width() + 8, green_icon_y))

        # Draw pink seeds below green seeds
        pink_icon_y = green_icon_y + self.tree_green_seed_sprite.image.get_height() + 6
        self.screen.blit(self.tree_pink_seed_sprite.image, (16, pink_icon_y))
        pink_font = pygame.font.SysFont("Arial", 24)
        pink_text = pink_font.render(str(self.pink_seeds), True, (220, 100, 180))
        self.screen.blit(pink_text, (16 + self.tree_pink_seed_sprite.image.get_width() + 8, pink_icon_y))


        # Draw tulip seeds below pink seeds
        tulip_icon_y = pink_icon_y + self.tree_pink_seed_sprite.image.get_height() + 6
        self.screen.blit(self.tulip_sprite.image, (16, tulip_icon_y))
        tulip_font = pygame.font.SysFont("Arial", 24)
        tulip_text = tulip_font.render(str(self.tulip_seeds), True, (220, 170, 60))
        self.screen.blit(tulip_text, (16 + self.tulip_sprite.image.get_width() + 8, tulip_icon_y))

        # Draw lavender seeds below tulip seeds
        lavender_icon_y = tulip_icon_y + self.tulip_sprite.image.get_height() + 6
        self.screen.blit(self.lavender_sprite.image, (16, lavender_icon_y))
        lavender_font = pygame.font.SysFont("Arial", 24)
        lavender_text = lavender_font.render(str(self.lavender_seeds), True, (160, 120, 220))
        self.screen.blit(lavender_text, (16 + self.lavender_sprite.image.get_width() + 8, lavender_icon_y))
    
        if self.menu_open:
            self.quests()
        self.button.draw(self.screen)

        if self.shop_open:
            self.shop_menu.draw(self.screen)
    
    def reload_tilemap(self):
        # Remove all current ground, trees, walls
        self.ground.empty()
        self.trees.empty()
        self.walls.empty()
        self.all_sprites.empty()
        self.player = None
        self.create_tilemap()
        # Re-add player if needed
        if self.player:
            self.all_sprites.add(self.player, layer=config.PLAYER_LAYER)
        else:
            self.player = gamesprites.Player((0, 0))
            self.all_sprites.add(self.player, layer=config.PLAYER_LAYER)

    def gameloop(self):
        self.selected_seed_type = "green"
        self.journaling_screen = None
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if self.state == self.STATE_MENU:
                    btn = self.title_screen.handle_event(event)
                    if btn == 0:
                        self.state = self.STATE_HELP
                    elif btn == 1:
                        self.state = self.STATE_PLAY
                    elif btn == 2:
                        self.running = False

                elif self.state == self.STATE_HELP:
                    if self.help_screen.handle_event(event):
                        self.state = self.STATE_MENU

                elif self.state == self.STATE_POMODORO:
                    if self.pomodoro_screen:
                        result = self.pomodoro_screen.handle_event(event)
                        if result == "exit":
                            self.state = self.STATE_PLAY
                            self.give_pomodoro_reward()
                            self.pomodoro_screen = None

                elif self.state == self.STATE_BREATHING:
                    if self.breathing_screen:
                        result = self.breathing_screen.handle_event(event)
                        if result == "exit":
                            self.state = self.STATE_PLAY
                            self.breathing_screen = None

                elif self.state == self.STATE_JOURNALING:
                    pass

                elif self.state == self.STATE_PLAY:
                    if self.menu_open:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.menu_open = False
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self.menu_close_icon.is_clicked(event.pos):
                                self.menu_open = False
                            else:
                                for idx, btn in enumerate(self.quest_buttons):
                                    if btn.rect.collidepoint(event.pos):
                                        if idx == 0:
                                            self.pomodoro_screen = PomodoroScreen(self.screen, self.give_pomodoro_reward)
                                            self.state = self.STATE_POMODORO
                                        elif idx == 1:
                                            self.breathing_screen = BreathingScreen(self.screen, self.give_breathing_reward)
                                            self.state = self.STATE_BREATHING
                                        elif idx == 2:
                                            from journaling import JournalingScreen
                                            self.journaling_screen = JournalingScreen(self.screen, self.give_journaling_reward)
                                            self.state = self.STATE_JOURNALING
                                        break
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                self.selected_seed_type = "green"
                            elif event.key == pygame.K_2:
                                self.selected_seed_type = "pink"
                            elif event.key == pygame.K_3:
                                self.selected_seed_type = "tulip"
                            elif event.key == pygame.K_4:
                                self.selected_seed_type = "lavender"
                            elif event.key == pygame.K_SPACE:
                                if self.selected_seed_type == "green":
                                    self.plant_tree()
                                elif self.selected_seed_type == "pink":
                                    self.plant_pink_tree()
                                elif self.selected_seed_type == "tulip":
                                    self.plant_tulip()
                                elif self.selected_seed_type == "lavender":
                                    self.plant_lavender()
                            elif event.key == pygame.K_q:
                                self.menu_open = True

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if self.button.is_clicked(event.pos):
                                    if not self.shop_open:
                                        self.shop_open = True
                                elif self.menu_icon.is_clicked(event.pos):
                                    self.menu_open = True

                        if self.shop_open:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.shop_open = False

                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                idx = self.shop_menu.item_at_pos(event.pos)
                                if idx is not None:
                                    if self.money > 0:
                                        if idx == 0:
                                            if self.money >= 5:
                                                self.money -= 5
                                                self.tulip_seeds += 1
                                        elif idx == 1:
                                            if self.money >= 5:
                                                self.money -= 5
                                                self.lavender_seeds += 1
                                        elif idx == 2:
                                            if self.money >= 10:
                                                self.money -= 10
                                                self.green_seeds += 1
                                        elif idx == 3:
                                            if self.money >= 10:
                                                self.money -= 10
                                                self.pink_seeds += 1
                                    self.shop_menu.clicked_index = idx

                            if event.type == pygame.MOUSEMOTION:
                                self.shop_menu.update_hover(event.pos)
                            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                self.shop_menu.clicked_index = None

                if self.state == self.STATE_PLAY:
                    self.map_icon.handle_event(event)
                    
                    result = self.land_menu.handle_event(event)
                    if result:
                        if result and result[0] == "done":
                            config.tilemap = map.update_tilemap_with_owned_land(self.land_menu.owned_tiles, config.tilemap)
                            self.reload_tilemap()



                
            
            # -------- DRAW LOGIC ---------
            if self.state == self.STATE_MENU:
                self.title_screen.draw(self.screen)
            elif self.state == self.STATE_HELP:
                self.help_screen.draw(self.screen)
            elif self.state == self.STATE_POMODORO and self.pomodoro_screen:
                self.pomodoro_screen.update()
                self.pomodoro_screen.draw()
            elif self.state == self.STATE_BREATHING and self.breathing_screen:
                self.breathing_screen.update()
                self.breathing_screen.draw()
            elif self.state == self.STATE_JOURNALING and self.journaling_screen:
                self.journaling_screen.run()
                self.journaling_screen = None
                self.state = self.STATE_PLAY
            elif self.state == self.STATE_PLAY:
                keys = pygame.key.get_pressed()
                self.player.update(dt, keys, self.walls)
                self.refresh()
                self.map_icon.draw(self.screen)
                self.land_menu.draw(self.screen)  # Only once, outside refresh()
                for tree in self.trees:
                    tree.update(dt)
                self.refresh()

            # Only check was_clicked ONCE
            if self.state == self.STATE_PLAY and self.map_icon.was_clicked():
                self.land_menu.open()


            pygame.display.flip()
        pygame.quit()
        sys.exit()






game = Game()
game.gameloop()

