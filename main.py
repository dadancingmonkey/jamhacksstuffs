import pygame
import sys
import gamesprites
import random
import config



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
        self.player = None  # Will set after scanning tilemap
        self.create_tilemap()
        # Add player sprite after locating P
        if self.player:
            self.all_sprites.add(self.player, layer=config.PLAYER_LAYER)
        else:
            # Fallback if no 'P' found
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
    # How far in front of the player? Use TILESIZE or PLAYERSIZE
        offset = config.TILESIZE
        # Find the player's current tile
        px = int(player.world_pos.x // config.TILESIZE)
        py = int(player.world_pos.y // config.TILESIZE)

        # Move one tile in facing direction
        if player.direction == "up":
            py -= 1
        elif player.direction == "down":
            py += 3
        elif player.direction == "left":
            px -= 2
        elif player.direction == "right":
            px += 2

        # Snap to tile top-left
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



    

    '''def draw_highlight_square(self, screen, player, config):
        """
        Draw a translucent highlight square in front of the player,
        based on the player's facing direction and world position.
        """
        # 1. Get forward tile's world position
        forward_pos = self.get_forward_pos(player)
        # 2. Convert world position to screen position
        screen_rect = screen.get_rect()
        screen_x = forward_pos.x - player.world_pos.x + screen_rect.centerx
        screen_y = forward_pos.y - player.world_pos.y + screen_rect.centery
        # 3. Create translucent highlight surface
        highlight_surf = pygame.Surface((config.TILESIZE, config.TILESIZE), pygame.SRCALPHA)
        highlight_surf.fill((255, 0, 0, 255))  # Bright red, fully opaque
        
        
        # 4. Draw to main screen
        screen.blit(highlight_surf, (screen_x, screen_y))'''
    
    
    '''def get_tile_in_front(self, player, distance=2):
        px = int(round(player.world_pos.x // config.TILESIZE))
        py = int(round(player.world_pos.y // config.TILESIZE))
        if player.direction == 'up':
            py -= distance
        elif player.direction == 'down':
            py += distance
        elif player.direction == 'left':
            px -= distance
        elif player.direction == 'right':
            px += distance
        return px, py'''


    def plant_tree(self):
        tile_pos = self.get_forward_pos(self.player)  # This is the top-left of the tile
        # Get tile center
        center_x = tile_pos.x + config.TILESIZE // 2
        center_y = tile_pos.y + config.TILESIZE // 2

        # To center the tree, subtract half its size
        tree_x = center_x - config.TREESIZE // 2
        tree_y = center_y - config.TREESIZE // (5/4)

        # Prevent planting on tree or wall
        px = int(tile_pos.x // config.TILESIZE)
        py = int(tile_pos.y // config.TILESIZE)
        for tree in self.trees:
            tx = int(tree.world_pos.x // config.TILESIZE)
            ty = int(tree.world_pos.y // config.TILESIZE)
            if (tx, ty) == (px, py):
                return
        for wall in self.walls:
            wx = int(wall.world_pos.x // config.TILESIZE)
            wy = int(wall.world_pos.y // config.TILESIZE)
            if (wx, wy) == (px, py):
                return

        # Place the new tree centered on the tile
        new_tree = gamesprites.PlantedTree((tree_x, tree_y))
        self.trees.add(new_tree)
        self.walls.add(new_tree)
        self.all_sprites.add(new_tree, layer=config.TREES_LAYER)

    
    
    
    '''def plant_tree(self):


        px, py = self.get_forward_pos(self.player)
        world_x, world_y = px * config.TILESIZE, py * config.TILESIZE

        # Prevent planting on tree or wall
        for tree in self.trees:
            tx, ty = int(round(tree.world_pos.x // config.TILESIZE)), int(round(tree.world_pos.y // config.TILESIZE))
            if (tx, ty) == (px, py):
                return
        for wall in self.walls:
            wx, wy = int(round(wall.world_pos.x // config.TILESIZE)), int(round(wall.world_pos.y // config.TILESIZE))
            if (wx, wy) == (px, py):
                return

        # Place the new tree
        new_tree = gamesprites.PlantedTree((world_x, world_y))
        self.trees.add(new_tree)
        self.walls.add(new_tree)  # <-- Add this line!
        self.all_sprites.add(new_tree, layer=config.TREES_LAYER)
        '''


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


        # Draw trees
        for tree in self.trees:
            tree_rect = tree.image.get_rect(
                topleft=(
                    tree.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                    tree.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                )
            )
            self.screen.blit(tree.image, tree_rect)

        # Draw highlight square before the player so it's under them, or after for over
        self.draw_highlight_square(self.screen, self.player, config)


        # Draw player at center
        player_rect = self.player.image.get_rect(center=screen_rect.center)
        self.screen.blit(self.player.image, player_rect)

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

            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.walls)

            for tree in self.trees:
                tree.update(dt)

            self.refresh()



        pygame.quit()
        sys.exit()


game = Game()
