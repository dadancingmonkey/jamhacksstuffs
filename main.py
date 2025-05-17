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
        # Sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.trees = pygame.sprite.Group()

        # Example: Add a player
        self.player = gamesprites.Player((400, 300))
        self.all_sprites.add(self.player, layer=2)

        # Example: Add a tree
        tree = gamesprites.Tree((200, 400))
        self.trees.add(tree)
        self.all_sprites.add(tree, layer=1)

    def refresh(self):
        self.screen.fill((135, 206, 235))  # Light sky blue background

        screen_rect = self.screen.get_rect()

        # Draw all trees at their world positions relative to player
        for tree in self.trees:
            # Calculate where to draw the tree on the screen
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
