import pygame

pygame.init()

screen = pygame.display.set_mode((1000, 1000))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("RoboticsLogoPNG.png").convert_alpha()
        self.rect = self.image.get_rect(center=(400, 300))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_UP]:
            self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            self.rect.y += 5

player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)





# I - Import and Initialize - Start IDEA

# D - Display configuration

pygame.display.set_caption("Hello, world!")
# E - Entities (just background for now)
background = pygame.image.load('wowza.png')
background = background.convert()




# A - Action (broken into ALTER steps)
# A - Assign values to key variables
clock = pygame.time.Clock()
# L - Loop
keepGoing = True
while keepGoing:
# T - Timer to set frame rate
    clock.tick(30)
# E - Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keepGoing = False

    
# R - Refresh display
    screen.blit(background, (0, 0))

    


    all_sprites.update()
    all_sprites.draw(screen)



        

        

    
    pygame.display.flip()
# Close the game window , set the X
pygame.quit()