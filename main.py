import pygame
import sys
import gamesprites
import random
import config
import menus



class Game:
    def __init__(self):


        
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mindful")
        self.clock = pygame.time.Clock()
        self.running = True

        self.init_buttons()

        
    
        self.entities()
        self.gameloop()
        self.refresh()
        

    def init_buttons(self):
        screen_width = self.screen.get_width()
        self.button = menus.ImageButton("images/shop_icon.png", (screen_width, 0), margin=(20, 20), size=(80, 80))
        self.shop_menu = menus.Shop()
        self.shop_open = False



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
        offset = config.TILESIZE
        px = int(player.world_pos.x // config.TILESIZE)
        py = int(player.world_pos.y // config.TILESIZE)

        if player.direction == "up":
            py -= 1
        elif player.direction == "down":
            py += 3
        elif player.direction == "left":
            px -= 2
        elif player.direction == "right":
            px += 2

        snapped_x = px * config.TILESIZE
        snapped_y = py * config.TILESIZE

        return pygame.Vector2(snapped_x, snapped_y)

    

    def draw_highlight_square(self, screen, player, config):
        forward_pos = self.get_forward_pos(player)
        screen_rect = screen.get_rect()
        # Add half tile to world positions for center alignment
        screen_x = (forward_pos.x + config.TILESIZE // 2) - player.world_pos.x + screen_rect.centerx
        screen_y = (forward_pos.y + config.TILESIZE // 2) - player.world_pos.y + screen_rect.centery

        # Now, to draw the highlight centered on the tile, subtract half tile from the draw position:
        highlight_surf = pygame.Surface((config.TILESIZE, config.TILESIZE), pygame.SRCALPHA)
        highlight_surf.fill((255, 0, 0, 255))
        draw_x = screen_x - config.TILESIZE // 2
        draw_y = screen_y - config.TILESIZE // 2
        screen.blit(highlight_surf, (draw_x, draw_y))

    def plant_tree(self):
        tile_pos = self.get_forward_pos(self.player)
        new_tree_temp = gamesprites.PlantedTree((tile_pos.x, tile_pos.y))

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




    def refresh(self):
        self.screen.fill((135, 206, 235))
        screen_rect = self.screen.get_rect()

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


        for tree in self.trees:
            tree_rect = tree.image.get_rect(
                topleft=(
                    tree.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                    tree.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                )
            )
            self.screen.blit(tree.image, tree_rect)

            debug_rect = pygame.Rect(
                tree.collision_rect.x - self.player.world_pos.x + screen_rect.centerx,
                tree.collision_rect.y - self.player.world_pos.y + screen_rect.centery,
                tree.collision_rect.width,
                tree.collision_rect.height
            )
            pygame.draw.rect(self.screen, (255, 0, 0), debug_rect, 2)




        self.draw_highlight_square(self.screen, self.player, config)


        # Draw player at center
        player_rect = self.player.image.get_rect(center=screen_rect.center)
        self.screen.blit(self.player.image, player_rect)

        self.button.draw(self.screen)

        if self.shop_open:
            self.shop_menu.draw(self.screen)


        pygame.display.flip()




    


    def gameloop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.plant_tree()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.button.is_clicked(event.pos):
                        if not self.shop_open:
                            self.shop_open = True
                if self.shop_open and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.shop_open = False



                if self.shop_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = self.shop_menu.item_at_pos(event.pos)
                    if idx is not None:
                        print(f"Clicked item {idx}!")

                if self.shop_open:
                    if event.type == pygame.MOUSEMOTION:
                        self.shop_menu.update_hover(event.pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        idx = self.shop_menu.item_at_pos(event.pos)
                        if idx is not None:
                            self.shop_menu.clicked_index = idx
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.shop_menu.clicked_index = None


            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.walls)





                

            for tree in self.trees:
                tree.update(dt)

            self.refresh()





        pygame.quit()
        sys.exit()


game = Game()

