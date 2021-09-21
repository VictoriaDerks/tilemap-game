# this file handles all NPC dialogs and player choices
# all code here is written by me, unless otherwise indicated

import tmx  # handles tilemap
import pygame
import xml.etree.ElementTree as ET  # handles XML files (dialog files)
import os  # gets folder contents
import datetime  # gets current date info

screen = pygame.display.set_mode((900, 506))  # same dimensions as Game.py file
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
pygame.font.init()
myfont = pygame.font.Font("fonts/OpenSans-Regular.ttf", 25)  # set font for dialog text


# this class creates the screen that the dialog will take place in
# takes number as an argument from Game.py. number is the number of the cell that is triggered by the player
class DialogScreen:
    def __init__(self, number):
        # this code gets the get variables belonging to the custom 'entry' property triggered cell (location & NPC name)
        triggers = tmx.load('test4.tmx', (900, 506)).layers['triggers']  # get the triggers tilemap layer
        self.input = triggers.find('entry')[number]['entry']
        self.values = self.input.split(",")  # split the variables at the ","
        self.bg = "img/" + self.values[0] + ".png"  # values[0] = string containing location. Matches a bg image in img

    def drawbg(self):
        loadbg = pygame.image.load(self.bg)  # create surface from image
        screen.blit(loadbg, (0, 0))  # blits bg surface to screen surface

    def drawNPC(self, npc):
        imgNPC = "img/" + npc + ".png"  # gets image of NPC
        loadnpc = pygame.image.load(imgNPC)
        screen.blit(loadnpc, (425, 20))  # NPC is draw on right of screen

    def drawDialog(self, tag):
        imgdialog = "img/" + tag + "-dialog.png"  # tag is either an NPC name, or "options"
        loaddialog = pygame.image.load(imgdialog)
        screen.blit(loaddialog, (0, -55))  # dialog box is drawn on bottom of screen


# this class handles the actual dialog text
# the dialog text is drawn over the background created by the DialogScreen class
class DialogText:
    def __init__(self):
        self.rect = pygame.Rect((35, 380), (840, 102))  # size of the dialog box
        self.lineNum = -1  # number of the line in the scene
        self.textInBlock = []  # list of all lines in the scene
        self.options = []  # list of options in the scene
        self.npcList = []  # list of NPCs in the scene
        self.toneList = []  # list of tones in the scene
        self.choicesList = []  # list of choices made by the player
        # dictionary translating choicebar positions to tones. Had to hardcode this, wouldn't work programmatically :(
        self.choicesKey = {382: "friendly", 415: "neutral", 448: "rude"}
        self.tone = None  # initial tone (e.g. friendly, neutral, rude)
        self.fontHeight = myfont.size("Test")[1]  # get height of font in px
        lineSpacing = -2  # distance between lines in px
        self.step = self.fontHeight + lineSpacing  # total height of line
        line1 = self.rect.top  # start of line 1, y coordinate of the dialog box rectangle
        self.currentPosition = line1 - lineSpacing  # start position
        # below are lists for all possible game locations.
        # If  new location is added to the game, new empty list needs to be created here
        self.dojo = []
        self.outdoors = []
        self.start = []
        self.cabin = []
        self.house = []
        self.Norros = False  # default: not visted Norros in the dojo yet
        self.Arasne = False  # default: haven't visted Arasne yet after going to the dojo

    # this function determines which dialog file should be used
    # depends on current location, which locations have been visited before, and amount of times visiting location
    def parseDialog(self):
        # awful hardcoding solutions. Needs fixing. Someday.
        # see Manual.docx for explanaion
        if self.location == "dojo":
            self.Norros = True  # advances text for "house" dialog when dojo is visted
            if False in self.dojo:
                self.currentNum = self.dojo.index(False)  # currentNum is index of first False in list
                if self.currentNum == 2 and self.Arasne is False:  # haven't visited Arasne yet after going to dojo
                    self.currentNum = 1
                elif self.currentNum == 1 and self.Arasne:  # visited Arasne. Dojo dialog advances
                    self.dojo[1] = True
                    self.currentNum = 2  # dialog dojo3.xml and dojo4.xml become available
                else:
                    pass  # currentNum remains the same as set earlier
            else:
                self.currentNum = len(self.dojo) - 1  # if no more False in list, run last available dialog
            self.currentlist = self.dojo
        if self.location == "house":
            if False in self.house:
                self.currentNum = self.house.index(False)
                if self.currentNum == 2 and self.Norros is False:  # don't continue dialog if haven't visited dojo yet
                    self.currentNum = 1
                elif (self.currentNum == 0 or self.currentNum == 1) and self.Norros:  # continue dialog if visited dojo
                    self.house[1] = True
                    self.currentNum = 2  # house3.xml and house4.xml are available
                else:
                    pass
                if (self.currentNum == 2 or self.currentNum == 3) and self.Norros:
                    self.Arasne = True  # visted Arasne after going to dojo. Advances dojo dialog
                else:
                    self.Arasne = False  # could also be pass. False is default.
            else:
                self.currentNum = len(self.house) - 1
            self.currentlist = self.house
        if self.location == "outdoors":
            if False in self.outdoors:
                self.currentNum = self.outdoors.index(False)  # currentNum is index first False in list
            else:
                self.currentNum = len(self.outdoors) - 1  # if no more False, replay last available dialog
            self.currentlist = self.outdoors
        if self.location == "cabin":
            if False in self.cabin:
                self.currentNum = self.cabin.index(False)
            else:
                self.currentNum = len(self.cabin) - 1
            self.currentlist = self.cabin

    # this function parses all the content of the .xml file and makes it useable
    def getText(self, number, name):
        # these variables change depending on the text file. Can't put in init.
        self.location = DialogScreen(number).values[0]  # string containing location name
        self.name = name  # name entered by player in start dialog

        self.parseDialog()  # gets current dialog file based on location and previous dialog

        self.scene = "dialog/" + self.location + str(self.currentNum + 1) + ".xml"  # load appropriate text file
        tree = ET.parse(self.scene)  # read the text file
        self.root = tree.getroot()
        self.lengthScene = len(self.root)  # how many lines are there?

        # this block turns the .xml file into 4 more manageable lists (tone list, npc list & text list and options list)
        for line in self.root:
            if line.tag == "text":
                npcName = line.get("name").title()  # get the npcName from the name attribute
                tone = line.get("tone")  # get the line's tone from the tone attribute (if it exists)
                text = line.text
                # all lists created in init
                self.npcList.append(npcName)  # list of all NPCs in dialog scene
                self.textInBlock.append(text)  # list of all lines in dialog scene
                self.toneList.append(tone)  # list of all tones in dialog scene
            else:  # line.tag == "options":
                # nested ifs to avoid code repetition
                if len(self.options) < 3:  # maximum options in a list is 3
                    pass  # execute the code below
                else:  # if  already 3 items in the options list, create a new list
                    self.options = []  # and then execute the code below
                for choice in line:
                    self.options.append(choice.text)  # add the choice to the choices list
                self.npcList.append("player")  # choices are made by the player, not an NPC
                self.textInBlock.append(self.options)  # add the options list to the list of all text (list in a list)
                self.toneList.append(None)  # choices made by the player have no inherent tone

    # blits the text to the screen
    # writes text on a new line when maximum line length is reached
    # adapted from https://www.pygame.org/wiki/TextWrap
    # comments by me, code mostly not mine
    def drawText(self, text):
        y = self.rect.top  # returns y location of dialog rect in px. Rect set in init
        while text:  # while we still have text left to write
            i = 1
            if y + self.fontHeight > self.rect.bottom:  # if text touches bottom of rect: we don't fit anymore, chief
                break
            while myfont.size(text[:i])[0] < self.rect.width and i < len(text):  # while letter fits in width of rect
                i += 1  # increase 1 letter
            if i < len(text):  # we don't fit in width, but there's still letters left
                i = text.rfind(" ", 0, i) + 1  # find last space beginning at 0 and ending at last letter that fits
            newText = myfont.render(text[:i], True, (250, 255, 255))  # render first line in white w/ anti-aliasing
            screen.blit(newText, (self.rect.left, y))  # output text to screen at height y
            y += self.step  # create new line
            text = text[i:]  # remove first blitted line from the total text line
        return text  # return the text that didn't fit in the box

    # blits the player options to the screen
    # every option is written on a new line
    # code is based on drawText(), but written entirely by me
    def drawChoices(self, choiceDict, key):
        y = self.rect.top  # see drawText() comment
        choicebox = pygame.image.load("img/choices-dialog.png")  # get the choicebox (a blueish rectangle shape)
        # when the bottom of the dialog rect isn't yet reached, move the choicebox down one line
        if key == "s" and self.currentPosition < self.rect.bottom - self.step - 2:
            self.currentPosition = self.currentPosition + self.step
        # when the top of the dialog rect isn't yet reached, move the choicebox up one line
        elif key == "w" and self.currentPosition > self.rect.top + self.step:
            self.currentPosition = self.currentPosition - self.step
        else:  # if the player hits any other button than up or down
            pass

        screen.blit(choicebox, (self.rect.left - 10, self.currentPosition))  # blit the choicebox to the top choice
        self.tone = self.choicesKey[self.currentPosition]  # position of choicebox determines tone of line
        # blit each choice to the screen, on a separate line, in front of the choicebox
        for item in choiceDict:
            newChoice = myfont.render(item, True, (250, 255, 255))  # colour = white
            screen.blit(newChoice, (self.rect.left, y))  # blits options to screen
            y += self.step

    # your main text function
    # updates text and draws it to the screen
    # also, an occasional mess
    def textUpdate(self, screen, key="e"):
        # self.key = pygame.key.get_pressed()  # get keyboard key
        if self.lineNum < self.lengthScene - 1 and key == "e":  # E = next/confirm
            # increment line if we haven't yet seen all lines in the scene
            self.lineNum += 1
        elif self.lineNum == self.lengthScene - 1 and key == "e":  # no more text left to show
            removeDuplicates(self.name, self.location, self.currentNum)  # write choices to output file
            # resetting everything back to initial values.
            self.lineNum = -1
            self.textInBlock = []
            self.options = []
            self.npcList = []
            self.toneList = []
            self.choicesList = []
            self.tone = None
            if self.currentNum < len(self.currentlist) - 1:  # if end of location list (e.g. house, dojo) not reached
                self.currentlist[self.currentNum] = True  # set current dialog scene to True
            else:
                pass
            if self.location == "dojo" and self.currentNum == 2:  # story of game is done, game quits
                pygame.quit()
                quit()
            self.dialog = False  # ending the main loop if dialog is done
            return self.dialog
        else:  # if any other buttons are pressed
            pass

        # this part actually draws stuff
        currentLine = self.textInBlock[self.lineNum]
        prevLine = self.textInBlock[self.lineNum - 1]
        currentNPC = self.npcList[self.lineNum]  # NPC image is retrieved based on line properties
        screen.drawbg()  # draw the background always

        # write the player's choice to a list, after they have made it
        # this list gets trimmed down when all text is done by removeDuplicates()
        if type(prevLine) == list:  # the previous line was a player choice one
            self.write(self.tone)  # write the selected tone to a list
        else:  # previous line was a text line
            self.write(None)  # write "None" to the list

        if type(currentLine) != list:  # if line is a regular text line, not a dialog option
            # it gets weird here. We want to have the player's choice in a dialog affect the reaction of the NPCs
            # this is bloody difficult to do
            # currently, the game allows for 1 line of reaction by an NPC, dependent on a specific choice
            # i.e. the reaction for two of the three choices will always be the same, for 1 it may be different
            # there is definitely a more flexible, more elegant way to implement this, but I haven't found it yet
            # suggestions welcome
            # also see Manual.docx

            # this block is necessary to load the right response depending on the tone picked.
            if self.tone != self.toneList[self.lineNum] and self.toneList[self.lineNum] is not None:
                currentLine = self.textInBlock[self.lineNum + 1]  # skip the current line and draw the next one
                currentNPC = self.npcList[self.lineNum + 1]  # skip the npc of the current line and draw next one
                self.tone = None  # reset the tone to None
                self.lineNum += 1
            else:  # selected tone and tone of NPC line match
                pass  # draw the current line corresponding to the picked tone

            # replace the [name] tag w/ player name before drawing the line
            if "[name]" in currentLine:
                currentLine = currentLine.replace("[name]", self.name)
            else:  # if no [name] tag in line
                pass

            screen.drawNPC(currentNPC)  # draw the NPC belonging to the line. Gets drawn on top of background
            screen.drawDialog(currentNPC)  # draw the dialog box belonging to the NPC. Gets drawn on top of NPC
            self.drawText(currentLine)  # draw the actual line. Gets drawn on top of dialog box.
        else:  # if line is not a regular text line, but an player choice one
            screen.drawDialog("options")
            self.drawChoices(currentLine, key)

    def write(self, tone):
        self.choicesList.append(tone)


newText = DialogText()  # create new instance from class

# atrocious solution to a complicated problem.
# but I don't have the energy to figure this one out anymore
# DEFINITELY needs fixing once game gets more complicated, but for now it works like this
# all code in this block only happens once. This is good.
# also see Manual.docx
files = os.listdir("dialog")  # get all files in dialog folder
for files in files:
    # all locations have own dialog files. If new location added in game, add here as well
    if "dojo" in files:
        newText.dojo.append(False)  # set all dialog files to False. Changes to True when specific dialog is done
    elif "house" in files:
        newText.house.append(False)
    elif "outdoors" in files:
        newText.outdoors.append(False)
    elif "cabin" in files:
        newText.cabin.append(False)


# main dialog loop
def loop(number, name):
    newDialog = DialogScreen(number)  # create instance from class
    newText.dialog = True  # dialog hasn't ended yet
    newText.getText(number, name)  # gets file info and retrieves images, also gets player name info
    screen.fill((0, 0, 0))  # black
    newText.textUpdate(newDialog, "e")
    while newText.dialog:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if player presses X, quit the game
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                print(event.key)
                if event.key == pygame.K_e:
                    newText.textUpdate(newDialog, "e")
                elif event.key == pygame.K_s:
                    newText.textUpdate(newDialog, "s")
                elif event.key == pygame.K_w:
                    newText.textUpdate(newDialog, "w")  # the main body of the program. Draws everything.
        pygame.display.flip()  # keeps the display active


def removeDuplicates(name, location, num):  # creates a list of the player's choices
    list = newText.choicesList  # altered by the write() function
    i = 0
    while i < len(list) - 1:  # remove duplicate consecutive values
        if list[i] == list[i + 1]:
            list.remove(list[i])
        else:
            i += 1
    for item in range(list.count(None)):  # remove all "None" items in list
        list.remove(None)
    # gets date info
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    # creates and writes to file
    filename = "participants/" + name + " choices, " + str(day) + "-" + str(month) + "-" + str(year) + ".csv"
    openFile = open(filename, "a")
    list.insert(0, location + str(num))  # add name of location file at beginning of choices list
    toWrite = ",".join(list) + "\n"
    openFile.write(toWrite)
    openFile.close()
