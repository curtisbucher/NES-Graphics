## Renders the background using pallette anc chr and tiles
## http://www.dustmop.io/blog/2015/04/28/nes-graphics-part-1/
import pygame

COLORS = [
    (124, 124, 124),
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
    (0, 0, 0),
]


class Background:
    def __init__(self):
        ## Four pallette objects each with four colors, one of which is shared between the four
        self.pallettes = [Pallette(0, 1, 2, 3, x) for x in range(4)]
        ## Atributes. Essentially a nametable for pallettes. 15 x 16 (240)
        self.attributes = [0b00] * 240
        ## 256 CHR objects
        self.chr = [CHR(x) for x in range(256)]
        ## 30 x 32 (960) 8 bit numbers assigning chr files to position on the screen
        self.nametable = [0] * 960

    def to_surf(self, size):
        width, height = size
        surf = pygame.Surface((width, height))
        chr_size = width // 30, height // 32
        for y in range(32):
            for x in range(30):
                CHR = self.chr[self.nametable[y * 30 + x]]
                surf.blit(
                    CHR.to_surf(
                        chr_size, self.pallettes[self.attributes[x // 2 + y // 2 * 15]]
                    ),
                    (x * chr_size[0], y * chr_size[1]),
                )
        return surf

    def pallettes_to_surf(self, size):
        surf = pygame.Surface((2, 8))
        for a in range(16):
            surf.set_at((a % 2, a // 2), COLORS[self.pallettes[a // 4][a % 4]])
        return pygame.transform.scale(surf, size)

    def save(self, filename):
        ##  16 BYTES
        ## Compressing 4 x 4 byte pallettes into list of 16 colors (shared background color)
        pallette_bytes = []
        for x in range(4):
            pallette_bytes += self.pallettes[x].to_bytes()

        ## 64 BYTES
        ## Compressing 2 bit attributes into list of bytes. (Z ordering. 4 extra bytes at end)
        attribute_bytes = []
        for x in range(0, 16, 2):
            for y in range(0, 15, 2):
                first_index = x + (y * 16)
                byte = (self.attributes[first_index]) + (
                    self.attributes[first_index + 1] << 2
                )

                if y < 14:
                    byte += (self.attributes[first_index + 16] << 4) + (
                        self.attributes[first_index + 17] << 6
                    )

                attribute_bytes += [byte]

        ## 960 BYTES
        ## Nametable is already 960 x bytes
        nametable_bytes = self.nametable

        ## 4096 BYTES
        ## Compressing 2 * 64 * 256 byte chr tiles
        chr_bytes = []
        for x in range(256):
            chr_bytes += self.chr[x].to_bytes()

        ## Ordered by size of data
        total_data = bytes(
            pallette_bytes + attribute_bytes + nametable_bytes + chr_bytes
        )
        with open(filename, "wb") as file:
            file.write(total_data)

    def load(self, filename):
        with open(filename, "rb") as file:
            data = file.read()

        ## Loading Pallette data
        self.pallettes = []
        pallette_bytes = data[0:16]

        background = int(pallette_bytes[0])
        for x in range(1, 16, 4):
            self.pallettes += [
                Pallette(
                    background,
                    int(pallette_bytes[x]),
                    int(pallette_bytes[x + 1]),
                    int(pallette_bytes[x + 2]),
                    x // 3,
                )
            ]

        ## Loading attribute data
        self.attributes = [0 for x in range(240)]
        attribute_bytes = data[16:80]
        count = 0

        for x in range(0, 16, 2):
            for y in range(0, 15, 2):
                byte = attribute_bytes[count]
                first_index = x + (y * 16)

                self.attributes[first_index] = byte & 0b00000011
                self.attributes[first_index + 1] = (byte & 0b00001100) >> 2

                if y < 14:
                    self.attributes[first_index + 16] = (byte & 0b00110000) >> 4
                    self.attributes[first_index + 17] = (byte & 0b11000000) >> 6

                count += 1

        ## Loading nametable data
        nametable_bytes = data[80:1040]
        self.nametable = [int(x) for x in nametable_bytes]

        ## Loading chr data
        chr_bytes = data[1040:5136]
        self.chr = [CHR(x, chr_bytes[x * 16 : x * 16 + 16]) for x in range(256)]


class Pallette:
    shared_background = None

    def __init__(self, background_color, color1, color2, color3, index):
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
            return Pallette.shared_background
        elif index == 1:
            return self.color1
        elif index == 2:
            return self.color2
        elif index == 3:
            return self.color3
        else:
            print(index)
            raise IndexError(" Pallette index out of range")

    def __setitem__(self, index, value):
        if index == 0:
            Pallette.shared_background = value
        elif index == 1:
            self.color1 = value
        elif index == 2:
            self.color2 = value
        elif index == 3:
            self.color3 = value
        else:
            raise IndexError(" Pallette index out of range")

    def to_surf(self, size):
        surf = pygame.Surface((1, 4))
        for y in range(4):
            surf.set_at((0, y), COLORS[self[y]])
        return pygame.transform.scale(surf, size)

    def to_bytes(self):
        """ Creates list object from pallette for saving"""
        pallette_bytes = []
        for x in range(0, 4):
            pallette_bytes += [self[x]]
        return pallette_bytes


## Setting up tile data
class CHR:
    def __init__(self, index, data=[0b00 for x in range(16)]):
        # 64 pixels of two bit depth (16 bytes when compressed to bytes)
        self.CHR = self.__from_bytes__(data)
        self.index = index

    def to_surf(self, size, pallette):
        surf = pygame.Surface((8, 8))
        for y in range(8):
            for x in range(8):
                surf.set_at((x, y), COLORS[pallette[self.CHR[y * 8 + x]]])
        return pygame.transform.scale(surf, size)

    def to_bytes(self):
        """ Compresses chr to list of bytes for saving """
        chr_bytes = []
        for x in range(0, 64, 8):
            chr_bytes += [
                ((self.CHR[x] & 0b01) << 7)
                + ((self.CHR[x + 1] & 0b01) << 6)
                + ((self.CHR[x + 2] & 0b01) << 5)
                + ((self.CHR[x + 3] & 0b01) << 4)
                + ((self.CHR[x + 4] & 0b01) << 3)
                + ((self.CHR[x + 5] & 0b01) << 2)
                + ((self.CHR[x + 6] & 0b01) << 1)
                + ((self.CHR[x + 7] & 0b01))
            ]
        for x in range(0, 64, 8):
            chr_bytes += [
                ((self.CHR[x] & 0b10) << 6)
                + ((self.CHR[x + 1] & 0b10) << 5)
                + ((self.CHR[x + 2] & 0b10) << 4)
                + ((self.CHR[x + 3] & 0b10) << 3)
                + ((self.CHR[x + 4] & 0b10) << 2)
                + ((self.CHR[x + 5] & 0b10) << 1)
                + ((self.CHR[x + 6] & 0b10))
                + ((self.CHR[x + 7] & 0b10) >> 1)
            ]

        return chr_bytes

    def __from_bytes__(self, data):
        """ Decompresses chr from list of bytes for loading and displaying"""
        CHR = []
        for a in range(0, 8):
            CHR += [((data[a] & 0b10000000) >> 7) + ((data[a + 8] & 0b10000000) >> 6)]
            CHR += [((data[a] & 0b01000000) >> 6) + ((data[a + 8] & 0b01000000) >> 5)]
            CHR += [((data[a] & 0b00100000) >> 5) + ((data[a + 8] & 0b00100000) >> 4)]
            CHR += [((data[a] & 0b00010000) >> 4) + ((data[a + 8] & 0b00010000) >> 3)]
            CHR += [((data[a] & 0b00001000) >> 3) + ((data[a + 8] & 0b00001000) >> 2)]
            CHR += [((data[a] & 0b00000100) >> 2) + ((data[a + 8] & 0b00000100) >> 1)]
            CHR += [((data[a] & 0b00000010) >> 1) + ((data[a + 8] & 0b00000010) >> 0)]
            CHR += [((data[a] & 0b00000001) >> 0) + ((data[a + 8] & 0b00000001) << 1)]
        return CHR

