import pygame
import Graphics
import os

## Setting up pygame surface
## Initiating pygame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont("timesnewroman", 18)

infoObject = pygame.display.Info()
WIDTH = 1088  # infoObject.current_w
HEIGHT = 512  # infoObject.current_h

clock = pygame.time.Clock()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)  # FULLSCREEN)

background = Graphics.Background()
chr_index = 0
CHR = background.chr[chr_index]
pallette_index = 0
pallette = background.pallettes[0]

CHR.pallette = pallette

ACTIVE = 0  # 0 = chr, 1-4 = pallette colors. Defines which portion is being edited


def update_screen():
    """ Updates the screen. Called every screen refresh"""
    ## Setting the Caption
    pygame.display.set_caption(
        "CHR Index: " + str(chr_index) + "\tPallette Index: " + str(pallette_index)
    )

    CHR = background.chr[chr_index]

    ## Blitting the background
    screen.fill((255, 255, 255))

    ## Blitting the chr that is being edited
    screen.blit(CHR.to_surf((512, 512), background.pallettes[pallette_index]), (512, 0))

    ## Blitting the active pallette
    screen.blit(background.pallettes[pallette_index].to_surf((64, 256)), (1024, 0))

    ## Blitting all the pallettes
    screen.blit(background.pallettes_to_surf((64, 256)), (1024, 256))

    ## Blitting the background
    screen.blit(background.to_surf((512, 512)), (0, 0))

    ## Drawing lines to seperate segments
    pygame.draw.line(screen, (0, 0, 0), (1024, 0), (1024, 512), 3)
    pygame.draw.line(screen, (0, 0, 0), (1024, 256), (1088, 256), 3)

    ## Drawing lines to seperate active pallette colors and inactive pallettes
    for y in range(0, 512, 64):
        pygame.draw.line(screen, (0, 0, 0), (1024, y), (1088, y), 1)

    if not ACTIVE:
        pygame.draw.rect(screen, (255, 0, 0), (512, 0, 512, 512), 2)
    elif ACTIVE == 1:
        pygame.draw.rect(screen, (255, 0, 0), (1024, 0, 64, 64), 2)
    elif ACTIVE == 2:
        pygame.draw.rect(screen, (255, 0, 0), (1024, 64, 64, 64), 2)
    elif ACTIVE == 3:
        pygame.draw.rect(screen, (255, 0, 0), (1024, 128, 64, 64), 2)
    elif ACTIVE == 4:
        pygame.draw.rect(screen, (255, 0, 0), (1024, 192, 64, 64), 2)

    pygame.display.flip()


def click(x, y):
    """ Handles mouse click action"""
    global ACTIVE

    ## If the mouse is modifying the background portion
    if x < 512:
        if not ACTIVE:
            background.nametable[x // (512 // 30) + (y // (512 // 32) * 30)] = chr_index
        else:
            background.attributes[
                x // (512 // 15) + (y // (512 // 16) * 15)
            ] = pallette_index

    ## If the mouse is modifying the CHR portion
    CHR = background.chr[chr_index]
    if x > 512 and x < 1024:
        ACTIVE = 0
        index = (x // 64 - 8) + (y // 64 * 8)
        if CHR.CHR[index] < 3:
            CHR.CHR[index] += 1
        else:
            CHR.CHR[index] = 0

    ## If the mouse is modifying the pallette portion
    elif x > 1024 and y > 0 and y < 64:
        ACTIVE = 1
    elif x > 1024 and y > 64 and y < 128:
        ACTIVE = 2
    elif x > 1024 and y > 128 and y < 192:
        ACTIVE = 3
    elif x > 1024 and y > 192 and y < 256:
        ACTIVE = 4


done = False
while not done:
    for event in pygame.event.get():
        update_screen()
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            click(*pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if key[pygame.K_RIGHT]:
                if not ACTIVE:
                    if chr_index < 255:
                        chr_index += 1
                    else:
                        chr_index = 0
                else:
                    if pallette_index < 3:
                        pallette_index += 1
                    else:
                        pallette_index = 0
            elif key[pygame.K_LEFT]:
                if not ACTIVE:
                    if chr_index > 0:
                        chr_index -= 1
                    else:
                        chr_index = 255
                else:
                    if pallette_index > 0:
                        pallette_index -= 1
                    else:
                        pallette_index = 3
            elif key[pygame.K_UP] and ACTIVE:
                if background.pallettes[pallette_index][ACTIVE - 1] < 63:
                    background.pallettes[pallette_index][ACTIVE - 1] += 1
                else:
                    background.pallettes[pallette_index][ACTIVE - 1] = 0

            elif key[pygame.K_DOWN] and ACTIVE:
                if background.pallettes[pallette_index][ACTIVE - 1] > 0:
                    background.pallettes[pallette_index][ACTIVE - 1] -= 1
                else:
                    background.pallettes[pallette_index][ACTIVE - 1] = 63
            ## Saving the background, CHR and pallette Data
            elif key[pygame.K_LCTRL] and key[pygame.K_s]:
                background.save("test.nes")  # input("Filename: "))
            ## Opening a file
            elif key[pygame.K_LCTRL] and key[pygame.K_o]:
                background.load("test.nes")  # input("Filename: "))

        clock.tick(30)

pygame.quit()
os._exit(0)
