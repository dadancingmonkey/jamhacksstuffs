import pygame
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))


current_frame = 0

next_frame1 = current_frame

next_frame2 = current_frame

moving = True

interval = 60

speed_changer = 1

new = 0

font = pygame.font.SysFont('helvetica', 40)

text_str = 'Breath in...'



pygame.display.set_caption("Hello, world!")


clock = pygame.time.Clock()
radius = 150
radius2 = 85
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
    #screen.fill((255, 87, 51))
    screen.fill((195, 177, 225))

    if moving:
        current_frame += 1
    
    new += 1

    

    
    image = pygame.draw.circle(screen, (150,111,214), (400,300), radius)

    image2 = pygame.draw.circle(screen, (75,56,107), (400,300), radius2)

    text_surface = font.render(text_str, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(400, 300))

    screen.blit(text_surface, text_rect)







    if moving:
        speed = ((5*math.pi)/(6*speed_changer)) * math.sin((math.pi*current_frame)/(60*speed_changer))

    else:
        speed = 0

    if moving:
        speed2 = ((5*math.pi)/(4*speed_changer)) * math.sin((math.pi*current_frame)/(60*speed_changer))

    else:
        speed2 = 0


    

    radius += speed

    radius2 += speed2




    if new == 60:
        text_str = "Hold..."
        moving = False

    elif new == 120:
        text_str = "Breath out..."
        moving = True

        current_frame = 120

        speed_changer = 2

    elif new == 240:

        text_str = "Hold..."


        current_frame = 120
        moving = False
        

        

    elif new == 300:
        text_str = "Breath in..."
        new = 0
        speed_changer = 1
        current_frame = 0
        moving = True
    
        

    
    pygame.display.flip()
# Close the game window , set the X
pygame.quit()