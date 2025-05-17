import pygame

import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, world_pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((50, 150, 50))
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)
        self.speed = 200  # pixels per second

    def update(self, dt, keys):
        dx, dy = self.get_direction(keys)
        self.move(dx, dy, dt)

    def get_direction(self, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Normalize diagonal movement
        if dx != 0 or dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx /= length
            dy /= length

        return dx, dy

    def move(self, dx, dy, dt):
        self.world_pos.x += dx * self.speed * dt
        self.world_pos.y += dy * self.speed * dt

    def get_draw_pos(self, screen_rect):
        # Always draw in the center of the screen
        return self.image.get_rect(center=screen_rect.center)


class Tree(pygame.sprite.Sprite):
    def __init__(self, world_pos):
        super().__init__()
        self.image = pygame.Surface((32, 64))
        self.image.fill((34, 139, 34))
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

