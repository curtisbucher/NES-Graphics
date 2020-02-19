import pygame
import graphics
import fileexplorer

import tkinter
from platform import system
from os import path


## Setting up pygame surface
## Initiating pygame

root = tkinter.Tk()
pygame.init()


pygame.font.init()
font = pygame.font.SysFont("timesnewroman", 18)

infoObject = pygame.display.Info()
WIDTH = 1088  # infoObject.current_w
HEIGHT = 512  # infoObject.current_h

clock = pygame.time.Clock()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)  # FULLSCREEN)

background = graphics.Background()
chr_index = 0
CHR = background.chr[chr_index]
pallette_index = 0
pallette = background.pallettes[0]

CHR.pallette = pallette

ACTIVE = 0  # 0 = chr, 1-4 = pallette colors. Defines which portion is being edited
FILENAME = ""  # Filename for autosaving
PATH = "/"  # Default path for saving
FILE = "newdoc.chr"

## Getting system dependent hotkey
if system() == "Darwin":
    HOTKEY = pygame.KMOD_META
else:
    HOTKEY = pygame.KMOD_CTRL


def update_screen():
    """ Updates the screen. Called every screen refresh"""

    ## Setting the Caption
    pygame.display.set_caption(
        FILE
        + " "
        + "CHR Index: "
        + str(chr_index)
        + "\tPallette Index: "
        + str(pallette_index)
    )
    ## Setting the Icon
    pygame.display.set_icon(pygame.image.load("icon.png"))

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

            ## Save-as the background, CHR, and pallette Data (Control-Shift S)
            elif (event.mod & pygame.KMOD_SHIFT & HOTKEY) and key[pygame.K_s]:
                ## Asking for filename then saving
                FILENAME = fileexplorer.save(root, PATH)
                if FILENAME:
                    PATH, FILE = path.split(FILENAME)
                    background.save(FILENAME)

            ## Save the background, CHR and pallette Data (Control-S)
            elif (event.mod & HOTKEY) and key[pygame.K_s]:
                ## Saving under `FILENAME` if it is available, otherwise asking for file.
                if not FILENAME:
                    FILENAME = fileexplorer.save(root, PATH)
                if FILENAME:
                    PATH, FILE = path.split(FILENAME)
                    background.save(FILENAME)

            ## Opening a file (Control-O)
            elif (event.mod & HOTKEY) and key[pygame.K_o]:
                FILENAME = fileexplorer.open(root, PATH)
                if FILENAME:
                    PATH, FILE = path.split(FILENAME)
                    background.load(FILENAME)
pygame.quit()
