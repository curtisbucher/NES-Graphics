## Renders the background using pallette anc chr and tiles
## http://www.dustmop.io/blog/2015/04/28/nes-graphics-part-1/
import pygame
COLORS = [(124, 124, 124),
 (0, 0, 252),
 (0, 0, 188),
 (68, 40, 188),
 (148, 0, 132),
 (168, 0, 32),
 (168, 16, 0),
 (136, 20, 0),
 (80, 48, 0),
 (0, 120, 0),
 (0, 104, 0),
 (0, 88, 0),
 (0, 64, 88),
 (0, 0, 0),
 (0, 0, 0),
 (0, 0, 0),
 (188, 188, 188),
 (0, 120, 248),
 (0, 88, 248),
 (104, 68, 252),
 (216, 0, 204),
 (228, 0, 88),
 (248, 56, 0),
 (228, 92, 16),
 (172, 124, 0),
 (0, 184, 0),
 (0, 168, 0),
 (0, 168, 68),
 (0, 136, 136),
 (0, 0, 0),
 (0, 0, 0),
 (0, 0, 0),
 (248, 248, 248),
 (60, 188, 252),
 (104, 136, 252),
 (152, 120, 248),
 (248, 120, 248),
 (248, 88, 152),
 (248, 120, 88),
 (252, 160, 68),
 (248, 184, 0),
 (184, 248, 24),
 (88, 216, 84),
 (88, 248, 152),
 (0, 232, 216),
 (120, 120, 120),
 (0, 0, 0),
 (0, 0, 0),
 (252, 252, 252),
 (164, 228, 252),
 (184, 184, 248),
 (216, 184, 248),
 (248, 184, 248),
 (248, 164, 192),
 (240, 208, 176),
 (252, 224, 168),
 (248, 216, 120),
 (216, 248, 120),
 (184, 248, 184),
 (184, 248, 216),
 (0, 252, 252),
 (248, 216, 248),
 (0, 0, 0),
 (0, 0, 0)]

CHR_COLORS = ((0,0,0),(128,128,128),(255,255,255))


class Background:
    def __init__(self):
        ## Four pallette objects each with four colors, one of which is shared between the four
        self.pallettes = [Pallette(0,1,2,3,x) for x in range(4)]
        ## Atributes. Essentially a nametable for pallettes. 15 x 16 (240)
        self.attributes = [0b00]*240
        ## 256 CHR objects
        self.chr = [CHR(x) for x in range(256)]
        ## 30 x 32 (960) 8 bit numbers assigning chr files to position on the screen
        self.nametable = [0]*960
        
    def to_surf(self, size):
        width, height = size
        surf = pygame.Surface((width, height))
        chr_size = width//30, height//32
        for y in range(32):
            for x in range(30):
                CHR = self.chr[self.nametable[y*30+x]]
                try:
                    surf.blit(CHR.to_surf(chr_size, self.pallettes[self.attributes[x//2 + y//2* 15]]), (x*chr_size[0],y*chr_size[1]))
                except Exception:
                    print(self.attributes)
                    raise Exception
        return surf
    
    def save(self, filename):
        ## Compressing pallettes into list of 13 colors (shared background color)
        pallette_bytes = [Pallette.shared_background]
        for x in range(4):
            pallette_bytes += self.pallettes[x].to_bytes()
            
        ## Compressing 2 bit attributes into list of bytes
        attribute_bytes = []
        for x in range(0,240,4):
            attribute_bytes += [self.attributes[x] 
                                + self.attributes[x + 1] 
                                + self.attributes[x + 2] 
                                + self.attributes[x + 3]]
        ## Nametable is already 960 x bytes
        nametable_bytes = self.nametable
        
        ## Compressing 2 * 64 * 256 byte chr tiles
        chr_bytes = []
        for x in range(256):
            chr_bytes += self.chr[x].to_bytes()
            
        ## Ordered by size of data
        total_data = bytes(pallette_bytes + attribute_bytes + nametable_bytes + chr_bytes)
        with open(filename, "wb") as file:
            file.write(total_data)
            
    def load(self, filename):
        with open(filename, "rb") as file:
            data = file.read()
            
        ## Loading Pallette data
        self.pallettes = []
        pallette_bytes = data[0:13]

        background = int(pallette_bytes[0])
        for x in range(1,13,3):
            self.pallettes += [Pallette(background, 
                          int(pallette_bytes[x]), 
                          int(pallette_bytes[x+1]), 
                          int(pallette_bytes[x+2]))]
            
        ## Loading attribute data
        self.attributes = []
        attribute_bytes = data[13:73]
        for x in range(60):
            self.attributes += [attribute_bytes[x] & 0b11000000]
            self.attributes += [attribute_bytes[x] & 0b00110000]
            self.attributes += [attribute_bytes[x] & 0b00001100]
            self.attributes += [attribute_bytes[x] & 0b00001111]
            
        ## Loading nametable data
        nametable_bytes = data[73:1033]
        self.nametable = [int(x) for x in nametable_bytes]
        
        ## Loading chr data
        chr_bytes = data[1033:5129]
        self.chr = []
        for x in range(256):
            self.chr += [CHR(x)]
            self.chr[x].CHR = []
            for a in range(0,16):
                self.chr[x].CHR += [chr_bytes[x*16 - 16 + a] & 0b11000000]
                self.chr[x].CHR += [chr_bytes[x*16 - 16 + a] & 0b00110000]
                self.chr[x].CHR += [chr_bytes[x*16 - 16 + a] & 0b00001100]
                self.chr[x].CHR += [chr_bytes[x*16 - 16 + a] & 0b00000011]


class Pallette:
    shared_background = None

    def __init__(self, background_color, color1, color2, color3, index=0):
        if not Pallette.shared_background:
            Pallette.shared_background = background_color
        elif Pallette.shared_background != background_color:
            raise TypeError("Pallettes don't maintain shared background color!")

        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.index = index
        
    def __getitem__(self, index):
        if index == 0:
            return self.shared_background
        if index == 1:
            return self.color1
        if index == 2:
            return self.color2
        if index == 3:
            return self.color3
        raise IndexError(" Pallette index out of range")
        
    def __setitem__(self, index, value):
        if index == 0:
            self.shared_background = value
        elif index == 1:
            self.color1 = value
        elif index == 2:
            self.color2 = value
        elif index == 3:
            self.color3 = value
        else:
            raise IndexError(" Pallette index out of range")
        
    def to_surf(self, size):
        surf = pygame.Surface((1,4))
        for y in range(4):
            surf.set_at((0,y), COLORS[self[y]])
        return pygame.transform.scale(surf,size)

    def to_bytes(self):
        """ Creates list object from pallette for saving"""
        pallette_bytes = []
        for x in range(1,4):
            pallette_bytes += [self[x]]
        return pallette_bytes


## Setting up tile data
class CHR:
    def __init__(self, index = 0):
        # 8 x 8 pixels of two bit depth
        self.CHR = [0b00]*64
        self.index = index
        
    def to_surf(self,size, pallette):
        surf = pygame.Surface((8,8))
        for y in range(8):
            for x in range(8):
                surf.set_at((x,y), COLORS[pallette[self.CHR[y*8+x]]])
        return pygame.transform.scale(surf,size)
    
    def to_bytes(self):
        """ Compresses chr to list of bytes for saving """
        chr_bytes = []
        for x in range(0,64,4):
            chr_bytes += [self.CHR[x] 
                        + self.CHR[x + 1] 
                        + self.CHR[x + 2] 
                        + self.CHR[x + 3]]
        return chr_bytes