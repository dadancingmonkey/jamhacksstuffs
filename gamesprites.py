import pygame
import config
import time
import pomodoro

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
        
        self.up_sprites = [
            pygame.transform.scale(pygame.image.load("images/bunnySprite_back1.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
            pygame.transform.scale(pygame.image.load("images/bunnySprite_back2.PNG").convert_alpha(), (config.PLAYERSIZE/2, config.PLAYERSIZE)),
        ]


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

        if dx != 0 or dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx /= length
            dy /= length

        return dx, dy

    def move(self, dx, dy, dt, walls_group):
        original_pos = self.world_pos.copy()
        #X movement (horizontal or left or right or whatever else you call it)
        self.world_pos.x += dx * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.x = original_pos.x
        #Y movement (veritical ahhh)
        self.world_pos.y += dy * self.speed * dt
        if self.collides_with_walls(walls_group):
            self.world_pos.y = original_pos.y

    def collides_with_walls(self, walls_group):
        player_rect = self.image.get_rect(topleft=self.world_pos)
        for wall in walls_group:
            wall_rect = getattr(wall, 'collision_rect', wall.image.get_rect(topleft=wall.world_pos))
            if player_rect.colliderect(wall_rect):
                return True
        return False




    def animate(self, dx, dy, dt):
        moving = dx != 0 or dy != 0

        if moving:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            elif abs(dy) > 0:
                self.direction = 'down' if dy > 0 else 'up'

        if moving:
            self.frame_timer += dt
            if self.frame_timer >= 0.15:
                self.frame = (self.frame + 1) % 2
                self.frame_timer = 0
        else:
            self.frame = 0

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


class Block(pygame.sprite.Sprite):
    image_surfaces = {}

    def __init__(self, world_pos, type):
        super().__init__()
        if type not in Block.image_surfaces:
            if type == "light1":
                image = pygame.image.load("images/grass_light_1.png").convert_alpha()
            elif type == "dark1":
                image = pygame.image.load("images/grass_dark_1.png").convert_alpha()
            elif type == "dark2":
                image = pygame.image.load("images/grass_dark_2.png").convert_alpha()
            elif type == "light2":
                image = pygame.image.load("images/grass_light_2.png").convert_alpha()
            else:
                image = pygame.Surface((config.TILESIZE, config.TILESIZE))
            image = pygame.transform.scale(image, (config.TILESIZE, config.TILESIZE))
            Block.image_surfaces[type] = image

        self.image = Block.image_surfaces[type]
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))


class Water(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos, type):
        super().__init__()
        if type not in Block.image_surfaces:
            if type == "dark3":
                image = pygame.image.load("images/water.png").convert_alpha()
            elif type == "dark4":
                image = pygame.image.load("images/water1.png").convert_alpha()
            image = pygame.transform.scale(image, (config.TILESIZE, config.TILESIZE))
            Block.image_surfaces[type] = image

        self.image = Block.image_surfaces[type]
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)
        self.collision_rect = self.image.get_rect(topleft=self.world_pos)

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
            Wall.image_surface = pygame.image.load("images/stone.png").convert_alpha()
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
    

class PlantedTree(pygame.sprite.Sprite):
    TRUNK_SIZES = {
        "growing": (16, 20),
        "grown": (40, 56)
    }

    def __init__(self, tile_pos, growing_time, growth_img_path, grown_img_path, type="tree"):
        super().__init__()
        growth_img = pygame.image.load(growth_img_path).convert_alpha()
        grown_img = pygame.image.load(grown_img_path).convert_alpha()
        if type == "flower":
            self.growth_image = pygame.transform.scale(growth_img, (config.TREESIZE // 4, config.TREESIZE // 4))
            self.grown_image = pygame.transform.scale(grown_img, (config.TREESIZE//3, config.TREESIZE//3))
        else:
            self.growth_image = pygame.transform.scale(growth_img, (config.TREESIZE // 2, config.TREESIZE // 2))
            self.grown_image = pygame.transform.scale(grown_img, (config.TREESIZE, config.TREESIZE))

        self.image = self.growth_image

        # Positioning
        tile_center_x = tile_pos[0] + config.TILESIZE // 2
        image_midbottom_x = tile_center_x
        image_midbottom_y = tile_pos[1] + config.TILESIZE
        self.base_midbottom = (image_midbottom_x, image_midbottom_y)
        self.rect = self.image.get_rect(midbottom=self.base_midbottom)
        self.world_pos = pygame.Vector2(self.rect.topleft)

        # Start as "growing"
        self.set_trunk_collision(*self.TRUNK_SIZES["growing"])

        self.planted_time = time.time()
        self.grow_duration = growing_time
        self.grown = False

    def set_trunk_collision(self, trunk_width, trunk_height):
        trunk_x = self.rect.left + (self.rect.width - trunk_width) // 2
        trunk_y = self.rect.bottom - trunk_height
        self.collision_rect = pygame.Rect(trunk_x, trunk_y, trunk_width, trunk_height)

    def time_left(self):
        elapsed = time.time() - self.planted_time
        return max(0, int(self.grow_duration - elapsed))

    def update(self, dt):
        if not self.grown and self.time_left() == 0:
            # Switch to fully grown state
            self.image = self.grown_image
            self.rect = self.image.get_rect(midbottom=self.base_midbottom)
            self.world_pos = pygame.Vector2(self.rect.topleft)
            self.set_trunk_collision(*self.TRUNK_SIZES["grown"])
            self.grown = True



class Money(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Money.image_surface:
            Money.image_surface = pygame.image.load("images/coinCurrency.png").convert_alpha()
            Money.image_surface = pygame.transform.scale(
                Money.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Money.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))
    

class Green(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Green.image_surface:
            Green.image_surface = pygame.image.load("images/tree_green_seed.png").convert_alpha()
            Green.image_surface = pygame.transform.scale(
                Green.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Green.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))

class Pink(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Pink.image_surface:
            Pink.image_surface = pygame.image.load("images/tree_pink_seed.png").convert_alpha()
            Pink.image_surface = pygame.transform.scale(
                Pink.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Pink.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))

class Tulip(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Tulip.image_surface:
            Tulip.image_surface = pygame.image.load("images/tulip_seed.png").convert_alpha()
            Tulip.image_surface = pygame.transform.scale(
                Tulip.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Tulip.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))
    
class Lavender(pygame.sprite.Sprite):
    image_surface = None

    def __init__(self, world_pos):
        super().__init__()
        if not Lavender.image_surface:
            Lavender.image_surface = pygame.image.load("images/lavender_seed.png").convert_alpha()
            Lavender.image_surface = pygame.transform.scale(
                Lavender.image_surface, (config.TILESIZE, config.TILESIZE)
            )
        self.image = Lavender.image_surface
        self.rect = self.image.get_rect()
        self.world_pos = pygame.Vector2(world_pos)

    def update(self, dt):
        pass

    def get_draw_pos(self, player_world_pos, screen_rect):
        screen_x = self.world_pos.x - player_world_pos.x + screen_rect.centerx
        screen_y = self.world_pos.y - player_world_pos.y + screen_rect.centery
        return self.image.get_rect(topleft=(screen_x, screen_y))
 

class Quests(pygame.sprite.Sprite):
    def __init__(self, pos, radius=32):
        super().__init__()
        self.radius = radius
        self.image = pygame.image.load("images/scroll_icon.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=pos)

    def is_clicked(self, mouse_pos):
        rel_x = mouse_pos[0] - self.rect.centerx
        rel_y = mouse_pos[1] - self.rect.centery
        return rel_x ** 2 + rel_y ** 2 <= self.radius ** 2
    

class MenuBackground(pygame.sprite.Sprite):
    def __init__(self, screen_size):
        super().__init__()
        self.image = pygame.image.load("images/menu_bg.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, screen_size)
        self.rect = self.image.get_rect(topleft=(0, 0))


class QuestButton(pygame.sprite.Sprite):
    def __init__(self, center, radius, color, text, image_path=None, reward_text=None):
        super().__init__()
        self.radius = radius
        self.color = color
        self.text = text
        self.reward_text = reward_text
        self.image_path = image_path

        if image_path:
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.smoothscale(image, (radius*2, radius*2))
            self.image = image
        else:
            self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect(center=center)

    def is_clicked(self, mouse_pos):
        rel_x = mouse_pos[0] - self.rect.centerx
        rel_y = mouse_pos[1] - self.rect.centery
        return rel_x ** 2 + rel_y ** 2 <= self.radius ** 2


