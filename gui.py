#This will run on the laptops and show statistics for the cars

from __future__ import division

import os, pygame
from pygame.locals import *
from pygame.compat import geterror

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'gui_data')

SCREEN_SIZE = (1000,500)

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def write(words, surf, x, y, color = (0,0,0), size = 36):
        font = pygame.font.Font(None, size)
        text = font.render(words, 1, color)
        textpos = text.get_rect(center = (x,y))
        surf.blit(text, textpos)

class PowerMeter(object):
    """Indicates when you can shoot"""
    def __init__(self, surf, x, y):
        self.bg = surf#the surface to draw on
        self.width = 100
        self.height = 20
        self.health = 100#%
        self.x = x
        self.y = y
        #draw border
        pygame.draw.rect(self.bg, (128,128,128), pygame.Rect(self.x,self.y,self.width,self.height), 10)
        #clear space for power
        pygame.draw.rect(self.bg, (255,255,255), pygame.Rect(self.x,self.y,self.width,self.height))
    def update(self):
        #this is the health level
        color = (0, 0, 0)
        if self.health < 25:
            color = (255, 0, 0)
        elif self.health < 50:
            color = (255, 128, 0) #orange
        else:
            color = (0, 255, 0)
        pygame.draw.rect(self.bg, color, pygame.Rect(self.x,self.y,self.health,self.height))

class GameTimer(object):
    """Bar that indicates time left in the game"""
    def __init__(self, surf, clock, time = 180):
        self.start_time = time
        self.time = time
        self.bg = surf
        self.color = (0,255,0)
        self.x = 0
        self.y = 490
        self.width = SCREEN_SIZE[0]
        self.height = 20
        self.clock = clock
        
        pygame.draw.rect(self.bg, self.color, pygame.Rect(self.x,self.y,self.width,self.height))
    def update(self):
        self.time -= (self.clock.get_time())/1000
    #def count(self):
        pygame.draw.rect(self.bg, (255,255,255), pygame.Rect(self.x,self.y,self.width,self.height))
        pygame.draw.rect(self.bg, self.color, pygame.Rect(self.x,self.y,self.time/self.start_time*self.width,self.height))

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('FRC Team 830')
    pygame.mouse.set_visible(1)
    #create background    
    background_img = pygame.image.load(os.path.join(data_dir, "bg.png")).convert()
    background = pygame.Surface(SCREEN_SIZE)
    background.blit(background_img, (0, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    meter1 = PowerMeter(background, 10, 100)
    meter2 = PowerMeter(background, 510, 100)
    game_time = GameTimer(background, clock)

    updateables = (meter1, meter2, game_time)#list of things to update in the loop
    #allsprites = pygame.sprite.RenderPlain(())

    write("LaserBots!", background, 500, 25, (46,45,123), 50)
    write("Player 1", background, 250, 60, (0,255,0), 50)
    write("Player 2", background, 750, 60, (255,0,0), 50)
#Main Loop
    going = True
    while going:
        clock.tick(60)

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
        for obj in updateables:
            obj.update()
        #allsprites.update()     
        #Draw Everything
        screen.blit(background, (0, 0))
        #allsprites.draw(screen)
        pygame.display.flip()


    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
