import pygame
import config

class Player(pygame.sprite.Sprite):
    def __init__(self, world_pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((50, 150, 50))
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)
        self.speed = 200 

    def update(self, dt, keys, walls_group):
        dx, dy = self.get_direction(keys)
        self.move(dx, dy, dt, walls_group)

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

    def move(self, dx, dy, dt, walls_group):
        # Store original position
        original_pos = self.world_pos.copy()

        # Try move in x
        self.world_pos.x += dx * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.x = original_pos.x  

        # Try move in y
        self.world_pos.y += dy * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.y = original_pos.y  

    def collides_with_walls(self, walls_group):
        player_rect = self.image.get_rect(center=self.world_pos)
        for wall in walls_group:
            wall_rect = wall.image.get_rect(topleft=wall.world_pos)
            if player_rect.colliderect(wall_rect):
                return True
        return False



class Tree(pygame.sprite.Sprite):
    def __init__(self, world_pos):
        super().__init__()
        self.image = pygame.Surface((32, 64))
        self.image.fill((34, 139, 34))
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass



class Block(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Block.image_surface:
            Block.image_surface = pygame.image.load("images\grass_light_1.png").convert_alpha()
            Block.image_surface = pygame.transform.scale(
                Block.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Block.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))


class Wall(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Wall.image_surface:
            Wall.image_surface = pygame.image.load("images/grass_dark_1.png").convert_alpha()
            Wall.image_surface = pygame.transform.scale(
                Wall.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Wall.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))
