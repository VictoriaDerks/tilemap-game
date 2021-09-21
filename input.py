import pygame
from pygame.locals import *

def name(screen, font, bg, dialog, nameprompt):
    screen = screen  # get screen set in Start file
    name = ""  # var name is empty string
    pygame.font.init()
    myfont = font  # already set in Start file
    while True:  # text loop
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.unicode.isalpha():  # key pressed has to be unicode letter
                    name += event.unicode  # update name string with letter
                elif event.key == K_BACKSPACE:  # backspace removes letter
                    name = name[:-1]
                elif event.key == K_RETURN:  # enter clears everything
                    return name  # if enter is pressed, return entered name and get back to Start.py
            elif event.type == QUIT:  # if X is pressed, quit
                return
        screen = pygame.display.set_mode((900, 506))
        screen.fill((0, 0, 0))  # black
        screen.blit(bg, (0, 0))  # bg surface is created in Start.py
        screen.blit(dialog, (0, - 55))  # dialog box surface is created in Start.py
        prompt = myfont.render(nameprompt, True, (250, 255, 255))  # white text
        screen.blit(prompt, (35, 380))  # print prompt at top of dialog box
        # blit instructions to bottom right of dialog box
        screen.blit(myfont.render("Please type your name and hit enter", True, (250, 255, 255)), (430, 450))
        block = myfont.render(name, True, (250, 255, 255))  # create surface containing name
        rect = block.get_rect().move(350, 410)  # move surface to middle of dialog box
        screen.blit(block, rect)  # blit name surface to screen
        pygame.display.flip()  # keep display active

