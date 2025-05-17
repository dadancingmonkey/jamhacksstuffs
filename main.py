import pygame
import sys
import gamesprites
import random
import config



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Game Title")
        self.clock = pygame.time.Clock()
        self.running = True

        self.entities()
        self.gameloop()
        self.refresh()

    def entities(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
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
                    # Optionally, also treat P as ground:
                    block = gamesprites.Block((world_x, world_y))
                    self.ground.add(block)
                    self.all_sprites.add(block, layer=config.BLOCKS_LAYER)



    def refresh(self):
        self.screen.fill((135, 206, 235)) 
        screen_rect = self.screen.get_rect()

        # Draw all ground blocks (red tiles)
        for block in self.ground:
            block_rect = block.image.get_rect(
                topleft=(
                    block.world_pos.x - self.player.world_pos.x + screen_rect.centerx,
                    block.world_pos.y - self.player.world_pos.y + screen_rect.centery,
                )
            )
            self.screen.blit(block.image, block_rect)

        # Draw all trees
        for tree in self.trees:
            screen_x = tree.world_pos.x - self.player.world_pos.x + screen_rect.centerx
            screen_y = tree.world_pos.y - self.player.world_pos.y + screen_rect.centery
            tree_rect = tree.image.get_rect(midbottom=(screen_x, screen_y))
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
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player.update(dt, keys)
            for tree in self.trees:
                tree.update(dt)  # Trees don't need keys

            self.refresh()

        pygame.quit()
        sys.exit()


game = Game()
