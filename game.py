# this file handles the overworld map and calls Dialog.py when appropriate
# this file is based on "Pyllet Town" (see Manual.docx and/or Credits.txt) and resembles much of the code written there
# however, the code here is more complicated and allows for more functionality
# for a direct comparision between the files, use the Pycharm compare function
import pygame  # make sure pygame module is installed
import tmx
import dialog
import start


# handles the player object in the game
class Player(pygame.sprite.Sprite):  # inherits from Sprite class in pygame
    def __init__(self, location, collStart, orientation, *groups):
        super(Player, self).__init__(*groups)  # not entirely sure what this does...
        self.image = pygame.image.load('sprites/player.png')  # loads player image from folder
        self.imageDefault = self.image.copy()
        self.rect = pygame.Rect(location, (56, 56))  # creates rectangle around first sprite image
        self.collider = pygame.Rect(collStart, (28, 28))  # creates player collision box on bottom half of player sprite
        self.orient = orientation  # direction player is facing
        self.holdTime = 0
        self.walking = False
        self.dx = 0
        self.step = 'rightFoot'
        # Set default orientation
        self.setSprite()
        self.speed = pygame.time.get_ticks() + 50  # slows down walking speed by .5 sec (current time + 50 ms)

    def setSprite(self):
        # Resets the player sprite sheet to its default position 
        # and scrolls it to the necessary position for the current orientation.
        # Moves rectangle to appropriate place in Player sprite sheet
        self.image = self.imageDefault.copy()
        if self.orient == 'up':
            self.image.scroll(0, -56)
        elif self.orient == 'down':
            self.image.scroll(0, 0)  # top first column in player.png
        elif self.orient == 'left':
            self.image.scroll(0, -112)
        elif self.orient == 'right':
            self.image.scroll(0, -168)  # bottom first column

    # checks if key is pressed and updates player position/orientation
    def update(self, dt, game):
        key = pygame.key.get_pressed()
        if pygame.time.get_ticks() >= self.speed:
            self.speed = pygame.time.get_ticks() + 50
            # Setting orientation and sprite based on key input:
            if key[pygame.K_w]:  # WASD to move, W moves position/orientation up
                if not self.walking:  # direction player is faces changes, player doesn't move
                    if self.orient != 'up':
                        self.orient = 'up'
                        self.setSprite()
                    self.holdTime += dt  # increments holdTime by dt to give time button is pressed
            elif key[pygame.K_s]:
                if not self.walking:
                    if self.orient != 'down':
                        self.orient = 'down'
                        self.setSprite()
                    self.holdTime += dt
            elif key[pygame.K_a]:
                if not self.walking:
                    if self.orient != 'left':
                        self.orient = 'left'
                        self.setSprite()
                    self.holdTime += dt
            elif key[pygame.K_d]:
                if not self.walking:
                    if self.orient != 'right':
                        self.orient = 'right'
                        self.setSprite()
                    self.holdTime += dt
            else:  # no relevant key is pressed
                self.holdTime = 0
                self.step = 'rightFoot'
            # Walking mode enabled if a button is held for 0.1 seconds
            if self.holdTime >= 100:
                self.walking = True
            lastRect = self.rect.copy()
            lastColl = self.collider.copy()
            # Walking at 2 pixels per frame in the direction the player is facing
            # rect and collider move with player
            if self.walking and self.dx < 64:  # haven't walked 64 px yet
                if self.orient == 'up':
                    self.rect.y -= 8  # walk 8 px up
                    self.collider.y -= 8
                elif self.orient == 'down':
                    self.rect.y += 8
                    self.collider.y += 8
                elif self.orient == 'left':
                    self.rect.x -= 8
                    self.collider.x -= 8
                elif self.orient == 'right':
                    self.rect.x += 8
                    self.collider.x += 8
                self.dx += 16
            # Collision detection:
            # Reset to the previous rectangle if player collides with anything in the foreground layer
            # player will be prevented from walking through object
            # uses custom 'solid' property of tile, set when creating tilemap
            if len(game.tilemap.layers['triggers'].collide(self.collider, 'solid')) > 0:
                self.rect = lastRect
                self.collider = lastColl
            # Area entry detection, loads dialog screen
            # uses custom 'entry' property, set when creating tilemap
            elif len(game.tilemap.layers['triggers'].collide(self.collider, 'entry')) > 0:
                # get current position of player
                xpos = self.rect.x
                ypos = self.rect.y
                index = 0
                for cell in game.tilemap.layers['triggers'].find('entry'):  # list of all cells with 'entry' property
                    if cell.px == xpos and cell.py == ypos:
                        self.number = index  # number is the index of the cell that player collides with
                    else:
                        index += 1
                game.fadeOut()
                dialog.loop(self.number, name)  # call main dialog loop
                # when dialog loop ends, player is moved one tile below the entry tile facing down
                self.collider.y += 16
                self.rect.y += 16
                self.orient = "down"
                self.setSprite()
            # Switch to the walking sprite after 8 pixels
            if self.dx == 32:
                # Self.step keeps track of when to flip the sprite so that
                # the character appears to be taking steps with different feet.
                if self.step == 'leftFoot' and self.orient == 'up':
                    self.image.scroll(-56, 0)  # move rectangle to third column of player.png
                    self.step = 'rightFoot'
                elif self.step == 'leftFoot' and self.orient == 'down':
                    self.image.scroll(-56, 0)
                    self.step = 'rightFoot'
                elif self.step == 'leftFoot' and self.orient == 'left':
                    self.image.scroll(-56, 0)
                    self.step = 'rightFoot'
                elif self.step == 'leftFoot' and self.orient == 'right':
                    self.image.scroll(-56, 0)
                    self.step = 'rightFoot'
                else:
                    self.image.scroll(-110, 0)  # move rectangle to second column of player.png
                    self.step = 'leftFoot'
            # After traversing 64 pixels, the walking animation is done and can start anew
            if self.dx == 64:
                self.walking = False
                self.setSprite()
                self.dx = 0

            game.tilemap.set_focus(self.rect.x, self.rect.y)  # moves tilemap with player


class Game(object):
    def __init__(self, screen):
        self.screen = screen

    # not too sure how this function works
    def fadeOut(self):
        # Animate the screen fading to black for entering a new area
        clock = pygame.time.Clock()
        blackRect = pygame.Surface(self.screen.get_size())
        blackRect.set_alpha(100)  # no transparency
        blackRect.fill((0, 0, 0))  # black
        # Continuously draw a transparent black rectangle over the screen
        # to create a fadeout effect
        for i in range(0, 5):
            clock.tick(15)
            self.screen.blit(blackRect, (0, 0))
            pygame.display.flip()
        clock.tick(15)
        screen.fill((255, 255, 255, 50))  # white
        pygame.display.flip()
        
    def initArea(self, mapFile):
        # Load maps and initialize sprite layers for each new area
        self.tilemap = tmx.load(mapFile, screen.get_size())  # use tmx module to create tilemap
        self.players = tmx.SpriteLayer()  # use tmx module to create new sprite layer
        # Initializing player sprite
        # gets first cell with custom 'playerStart' property. Created when making tilemap
        startCell = self.tilemap.layers['triggers'].find('playerStart')[0]
        self.player = Player((startCell.px, startCell.py), (startCell.px, startCell.bottom-7),
                             startCell['playerStart'], self.players)
        foregroundItem = self.tilemap.layers.__getitem__("foreground")  # gets layer called foreground
        foregroundIndex = self.tilemap.layers.index(foregroundItem)  # gets index of layer in tilemap
        # moves player layer below foreground layer. This way, player gets drawn behind foreground objects
        self.tilemap.layers.insert(foregroundIndex, self.players)
        self.tilemap.set_focus(self.player.rect.x, self.player.rect.y)
            
    def main(self):
        clock = pygame.time.Clock()
        self.initArea('test4.tmx')  # loads tilemap file
        
        while 1:
            dt = clock.tick(30)  # limits frametrate

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # if X is pressed, quit game
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # if escape is held, quit game
                    return

            self.tilemap.update(dt, self)  # update tilemap layers
            screen.fill((0, 0, 0))
            self.tilemap.draw(self.screen)  # draw tilemap layers
            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((900, 506))
    pygame.display.set_caption("Game")
    name = start.loop()  # initiates the start conversation before loading the tilemap
    game = Game(screen)  # create instance from class
    game.main()  # START THE TILEMAP, JEEVES!
