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
    
    def get_tile_in_front(self, player, distance=2):
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
        return px, py



    def plant_tree(self):
        px, py = self.get_tile_in_front(self.player)
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
