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

## Defining the section sizes and positions for editor gui. RECT((x,y),size)
border = 3

SIDE_MENU_RECT = pygame.Rect((border, border), (32 - 2 * border, 512))
CORNER_MENU_RECT = pygame.Rect((1024 + 2 * border, 512 + 2 * border), (192, 256))

BACKGROUND_RECT = pygame.Rect((32, border), (480, 512))
CHR_RECT = pygame.Rect((512 + border, border), (512, 512))
PATTERN_TABLE_RECT = pygame.Rect((border, 512 + 2 * border), (1024, 256))
ACTIVE_PALLETTE_RECT = pygame.Rect((1024 + 2 * border, border), (64, 256))
PALLETTES_RECT = pygame.Rect((1024 + 2 * border, 256 + border), (64, 256))
COLORS_RECT = pygame.Rect((1088 + 3 * border, border), (128, 512))


infoObject = pygame.display.Info()
WIDTH = 1088 + 128 + 9  # infoObject.current_w
HEIGHT = 512 + 256 + 9  # infoObject.current_h

clock = pygame.time.Clock()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)  # FULLSCREEN)

background = graphics.Background()
chr_index = 0

CHR = background.chr[chr_index]
pallette_index = 0

pallette = background.pallettes[0]
color_index = 0
CHR.pallette = pallette

ACTIVE = 0  # 0 = chr, 1 = Pallette

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

    ## Refreshing the background
    screen.fill((0, 0, 0))

    ## Blitting the chr that is being edited
    screen.blit(
        CHR.to_surf(CHR_RECT.size, background.pallettes[pallette_index]),
        CHR_RECT.topleft,
    )

    ## Blitting the active pallette
    screen.blit(
        background.pallettes[pallette_index].to_surf(
            ACTIVE_PALLETTE_RECT.size, color_index
        ),
        ACTIVE_PALLETTE_RECT.topleft,
    )

    ## Blitting all the pallettes
    screen.blit(
        background.pallettes_to_surf(PALLETTES_RECT.size, pallette_index),
        PALLETTES_RECT.topleft,
    )

    ## Blitting all the colors
    screen.blit(background.colors_to_surf(COLORS_RECT.size), COLORS_RECT.topleft)

    ## Blitting the background
    screen.blit(background.to_surf(BACKGROUND_RECT.size), BACKGROUND_RECT.topleft)

    ## Blitting the chr tiles
    screen.blit(
        background.tiles_to_surf(PATTERN_TABLE_RECT.size, pallette_index),
        PATTERN_TABLE_RECT.topleft,
    )

    ## Blitting the side menu TEMP BLANK
    pygame.draw.rect(screen, (200, 200, 200), SIDE_MENU_RECT)

    ## Blitting the corner menu
    pygame.draw.rect(screen, (200, 200, 200), CORNER_MENU_RECT)

    ## Blitting the active color in the active pallette
    """
    ax, ay = ACTIVE_PALLETTE_RECT.topleft
    pygame.draw.rect(screen, (255, 0, 0), (ax, ay + 64 * color_index, 64, 64), 2)
    """

    ## Drawing a red rect around active chr tile
    ax, ay = PATTERN_TABLE_RECT.topleft
    bx, by = chr_index % 32, chr_index // 32

    cx, cy = bx * 32, by * 32
    x, y = ax + cx, ay + cy

    pygame.draw.rect(screen, (255, 0, 0), (x, y, 32, 32), 2)

    ## Drawing a red rect around active pallette
    """
    pygame.draw.rect(
        screen,
        (255, 0, 0),
        (PALLETTES_RECT.x, PALLETTES_RECT.y + pallette_index * 64, 64, 64),
        2,
    )
    """

    pygame.display.flip()


def click(x, y):
    """ Handles mouse click action"""
    global ACTIVE
    global chr_index
    global pallette_index
    global color_index

    if BACKGROUND_RECT.collidepoint(x, y):
        ax, ay = x - BACKGROUND_RECT.x, y - BACKGROUND_RECT.y
        if not ACTIVE:
            background.nametable[
                ax // (BACKGROUND_RECT.size[0] // 30)
                + (ay // (BACKGROUND_RECT.size[1] // 32) * 30)
            ] = chr_index
        else:
            background.attributes[
                ax // (BACKGROUND_RECT.size[0] // 15)
                + (ay // (BACKGROUND_RECT.size[1] // 16) * 15)
            ] = pallette_index

    elif CHR_RECT.collidepoint(x, y):
        ACTIVE = 0

        CHR = background.chr[chr_index]
        index = (x // 64 - 8) + (y // 64 * 8)
        if CHR.CHR[index] != color_index:
            CHR.CHR[index] = color_index
        ## erase by doubletapping
        else:
            CHR.CHR[index] = 0

    elif PATTERN_TABLE_RECT.collidepoint(x, y):
        ## coords within rect.
        ax, ay = x - PATTERN_TABLE_RECT.x, y - PATTERN_TABLE_RECT.y
        ## Percent locations within rect
        ax, ay = ax / PATTERN_TABLE_RECT.size[0], ay / PATTERN_TABLE_RECT.size[1]
        ## tile coords within rect
        ax, ay = int(ax * 32), int(ay * 8)
        ## Getting single tile index from coords tuple
        chr_index = ay * 32 + ax

    elif PALLETTES_RECT.collidepoint(x, y):
        ACTIVE = 1
        pallette_index = (y - 256) // 64

    elif ACTIVE_PALLETTE_RECT.collidepoint(x, y):
        color_index = y // 64

    elif COLORS_RECT.collidepoint(x, y):
        ## coords within rect.
        ax, ay = x - COLORS_RECT.x, y - COLORS_RECT.y
        ## Percent locations within rect
        ax, ay = ax / COLORS_RECT.size[0], ay / COLORS_RECT.size[1]
        ## Color coords within rect
        ax, ay = int(ax * 4), int(ay * 16)
        ## Getting single color index from coords tuple
        new_color_index = ay * 4 + ax

        background.pallettes[pallette_index][color_index] = new_color_index


done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            click(*pygame.mouse.get_pos())

        elif event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.VIDEORESIZE:
            ## Keeping the aspect ratio when resizing
            new_size = event.w, event.w * HEIGHT // WIDTH
            screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()

            ## Save-as the background, CHR, and pallette Data (Control-Shift S)
            if (event.mod & pygame.KMOD_SHIFT & HOTKEY) and key[pygame.K_s]:
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

        update_screen()
pygame.quit()
