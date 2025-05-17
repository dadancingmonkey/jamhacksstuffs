import pygame
import config

import pygame
import config

class Player(pygame.sprite.Sprite):
    def __init__(self, world_pos):
        super().__init__()
        self.speed = 200
        self.world_pos = pygame.Vector2(world_pos)
        self.frame = 0
        self.frame_timer = 0
        self.direction = 'down'  # Start facing down

        # Load walking sprites for each direction
        # If missing back (up), use down; if missing left, flip right
        self.right_sprites = [
            pygame.transform.scale(pygame.image.load("images/bunnySprite_right1.PNG").convert_alpha(), (config.PLAYERSIZE, config.PLAYERSIZE)),
            pygame.transform.scale(pygame.image.load("images/bunnySprite_right2.PNG").convert_alpha(), (config.PLAYERSIZE, config.PLAYERSIZE)),
        ]
        self.left_sprites = [
            pygame.transform.flip(self.right_sprites[0], True, False),
            pygame.transform.flip(self.right_sprites[1], True, False),
        ]
        self.down_sprites = [
            pygame.transform.scale(pygame.image.load("images/bunnySprite_front1.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
            pygame.transform.scale(pygame.image.load("images/bunnySprite_front2.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
        ]
        # If up sprites missing, use down_sprites as fallback
        try:
            self.up_sprites = [
                pygame.transform.scale(pygame.image.load("images/bunnySprite_back1.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
                pygame.transform.scale(pygame.image.load("images/bunnySprite_back2.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
            ]
        except:
            self.up_sprites = self.down_sprites

        # Start with facing down, first frame
        self.image = self.down_sprites[0]
        self.rect = self.image.get_rect()

    def update(self, dt, keys, walls_group):
        dx, dy = self.get_direction(keys)
        self.move(dx, dy, dt, walls_group)
        self.animate(dx, dy, dt)

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
        original_pos = self.world_pos.copy()
        # Try X movement
        self.world_pos.x += dx * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.x = original_pos.x
        # Try Y movement
        self.world_pos.y += dy * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.y = original_pos.y

    def collides_with_walls(self, walls_group):
        # The player's rect is always centered on their world position
        player_rect = self.image.get_rect(center=self.world_pos)
        for wall in walls_group:
            wall_rect = wall.image.get_rect(topleft=wall.world_pos)
            if player_rect.colliderect(wall_rect):
                return True
        return False

    def animate(self, dx, dy, dt):
        moving = dx != 0 or dy != 0

        # Direction logic: vertical movement takes priority over horizontal
        if moving:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            elif abs(dy) > 0:
                self.direction = 'down' if dy > 0 else 'up'

        # Frame timing for animation
        if moving:
            self.frame_timer += dt
            if self.frame_timer >= 0.15:
                self.frame = (self.frame + 1) % 2
                self.frame_timer = 0
        else:
            self.frame = 0  # Idle on first frame

        # Set image based on direction and frame
        if self.direction == 'right':
            self.image = self.right_sprites[self.frame]
        elif self.direction == 'left':
            self.image = self.left_sprites[self.frame]
        elif self.direction == 'up':
            self.image = self.up_sprites[self.frame]
        elif self.direction == 'down':
            self.image = self.down_sprites[self.frame]

    def get_draw_pos(self, screen_rect):
        return self.image.get_rect(center=screen_rect.center)




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
