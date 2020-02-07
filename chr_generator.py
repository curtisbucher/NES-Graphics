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
pallette = Graphics.Pallette(0,1,2,3)
CHR.pallette = pallette

active = 0 #0 = chr, 1-4 = pallette colors. Defines which portion is being edited


def update_screen():
    """ Updates the screen. Called every screen refresh"""
    pygame.display.set_caption("CHR Index: " + str(chr_index) + "\tPallette Index: " + str(pallette_index))
    CHR = background.chr[chr_index]
    screen.fill((255,255,255))
    
    screen.blit(CHR.to_surf((512,512), background.pallettes[pallette_index]), (512,0))
    screen.blit(background.pallettes[pallette_index].to_surf((64,256)), (1024,0))
    screen.blit(background.to_surf((512,512)),(0,0))
        
    pygame.draw.line(screen, (0,0,0),(1024,0),(1024,512),3)
    pygame.draw.line(screen, (0,0,0),(1024,256), (1088, 256),3)
    for y in range(0,256,64):
        pygame.draw.line(screen, (0,0,0),(1024,y), (1088, y),1)
        
    if not active:
        pygame.draw.rect(screen, (255,0,0), (512,0,512,512), 2)
    elif active == 1:
        pygame.draw.rect(screen, (255,0,0), (1024,0,64,64), 2)
    elif active == 2:
        pygame.draw.rect(screen, (255,0,0), (1024,64,64,64), 2)
    elif active == 3:
        pygame.draw.rect(screen, (255,0,0), (1024,128,64,64), 2)
    elif active == 4:
        pygame.draw.rect(screen, (255,0,0), (1024,192,64,64), 2)
    
        
    pygame.display.flip()
    

def click(x,y):
    """ Handles mouse click detection"""
    global active
    ## If the mouse is modifying the CHR portion
    CHR = background.chr[chr_index]
    if x < 512:
        if not active:
            background.nametable[x//(512//30) + (y//(512//32) *30)] = chr_index
        else:
            background.attributes[x//(512//15) + (y//(512//16) *15)] = pallette_index
    ## If the mouse is modifying the CHR portion
    if x > 512 and x < 1024:
        active = 0
        index = (x//64 - 8) + (y//64 * 8)
        if CHR.CHR[index] < 3:
            CHR.CHR[index] += 1
        else:
            CHR.CHR[index] = 0
            
    ## If the mouse is modifying the pallette portion
    elif x > 1024 and y > 0 and y < 64:
        active = 1
    elif x > 1024 and y > 64 and y < 128:
        active = 2
    elif x > 1024 and y > 128 and y < 192:
        active = 3
    elif x > 1024 and y > 192 and y < 256:
        active = 4
    
    
done = False
while not done:
    update_screen()
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            click(*pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if key[pygame.K_RIGHT]:
                if not active:
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
                if not active:
                    if chr_index > 0:
                        chr_index -= 1
                    else:
                        chr_index = 255
                else:
                    if pallette_index > 0:
                        pallette_index -= 1
                    else:
                        pallette_index = 3
            elif key[pygame.K_UP]:
                if background.pallettes[pallette_index][active - 1] < 63:
                    background.pallettes[pallette_index][active - 1] += 1
                else:
                    background.pallettes[pallette_index][active - 1] = 0
                    
            elif key[pygame.K_DOWN]:
                if background.pallettes[pallette_index][active - 1] > 0:
                    background.pallettes[pallette_index][active - 1] -= 1
                else:
                    background.pallettes[pallette_index][active - 1] = 63
            elif key[pygame.K_LCTRL] and key[pygame.K_s]:
                background.save(input("Filename: "))
            elif key[pygame.K_LCTRL] and key[pygame.K_o]:
                background.load(input("Filename: "))
                
        clock.tick(30)
    
pygame.quit()
os._exit(0)