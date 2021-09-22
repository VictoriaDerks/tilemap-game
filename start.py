# this file is very similar to the Dialog file. Therefore, all duplicate comments are removed
# it contains the dialog that runs at the start of the game
# because it isn't triggered by a position on the tile map (the tilemap isn't loaded yet), the Dialog file can't be used
# this file has some minor alterations that make it runs without any tilemap input
import pygame
import xml.etree.ElementTree as ET
import os
import input
import datetime

screen = pygame.display.set_mode((900, 506))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
crashed = False
pygame.font.init()
myfont = pygame.font.Font("fonts/OpenSans-Regular.ttf", 25)


class DialogScreen:
    def __init__(self):
        self.values = ["start", "rindri"]  # hardcoded list, because can't get from tilemap. Sets starting location&NPC.
        self.bg = "img/" + self.values[0] + ".png"

    def drawbg(self):
        self.loadbg = pygame.image.load(self.bg)
        screen.blit(self.loadbg, (0, 0))
        return self.loadbg

    def drawNPC(self, npc):
        imgNPC = "img/" + npc + ".png"
        loadnpc = pygame.image.load(imgNPC)
        screen.blit(loadnpc, (425, 20))

    def drawDialog(self, tag):
        imgdialog = "img/" + tag + "-dialog.png"
        self.loaddialog = pygame.image.load(imgdialog)
        screen.blit(self.loaddialog, (0, -55))
        return self.loaddialog


class DialogText:
    def __init__(self):
        self.rect = pygame.Rect((35, 380), (840, 102))
        self.lineNum = -1
        self.textInBlock = []
        self.options = []
        self.npcList = []
        self.toneList = []
        self.choicesList = []
        self.choicesKey = {382: "friendly", 415: "neutral", 448: "rude"}
        self.tone = None
        self.fontHeight = myfont.size("Test")[1]
        lineSpacing = -2
        self.step = self.fontHeight + lineSpacing
        line1 = self.rect.top
        self.currentPosition = line1 - lineSpacing
        self.start = []
        self.currentList = None
        self.name = None  # name var is not yet set
        self.currentLine = ""

    def getText(self):
        self.location = "start"
        self.currentlist = self.start
        self.scene = "dialog/" + self.location + str(1) + ".xml"
        tree = ET.parse(self.scene)
        self.root = tree.getroot()
        self.lengthScene = len(self.root)

        for line in self.root:
            self.npcList.append("rindri")  # all start text is spoken by Rindri
            if line.tag == "text":
                tone = line.get("tone")
                text = line.text
                # all empty lists created in init
                self.textInBlock.append(text)
                self.toneList.append(tone)
            elif line.tag == "options":
                if len(self.options) < 3:
                    pass
                else:
                    self.options = []
                for choice in line:
                    self.options.append(choice.text)
                self.textInBlock.append(self.options)
                self.toneList.append(None)


    def drawText(self, text):
        y = self.rect.top
        while text:
            i = 1
            if y + self.fontHeight > self.rect.bottom:
                break
            while myfont.size(text[:i])[0] < self.rect.width and i < len(text):
                i += 1
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1
            newText = myfont.render(text[:i], True, (250, 255, 255))
            screen.blit(newText, (self.rect.left, y))
            y += self.step
            text = text[i:]
        return text

    def drawChoices(self, choiceDict, key):
        y = self.rect.top
        choicebox = pygame.image.load("img/choices-dialog.png")
        if key == "s" and self.currentPosition < self.rect.bottom - self.step -2:
            self.currentPosition = self.currentPosition + self.step
        elif key == "w" and self.currentPosition > self.rect.top + self.step:
            self.currentPosition = self.currentPosition - self.step
        else:
            pass

        screen.blit(choicebox, (self.rect.left - 10, self.currentPosition))
        self.tone = self.choicesKey[self.currentPosition]
        for item in choiceDict:
            newChoice = myfont.render(item, True, (250, 255, 255))  # colour = white
            screen.blit(newChoice, (self.rect.left, y))
            y += self.step

    def textUpdate(self, screen, key="e"):
        # self.key = pygame.key.get_pressed()
        if self.lineNum < self.lengthScene-1 and key == "e":
            self.lineNum += 1
        elif self.textInBlock[self.lineNum] == self.textInBlock[self.lengthScene-1] and key == "e":
            # this would normally reset everything back to initial values.
            # but we're not calling the functions in these file ever again after the start dialog has ended
            # so we just save, quit the dialog and launch into the game
            removeDuplicates(self.name, "start", "0")
            self.dialog = False  # ending the loop
            return self.dialog
        else:
            pass

        self.currentLine = self.textInBlock[self.lineNum]
        prevLine = self.textInBlock[self.lineNum-1]
        self.currentNPC = self.npcList[self.lineNum]  # always Rindri, but w/e
        screen.drawbg()

        if type(prevLine) == list:
            self.write(self.tone)
        else:
            self.write(None)

        if "[name]" in self.currentLine:
            self.currentLine = self.currentLine.replace("[name]", self.name)
        else:
            pass

        # name input field loads if the current line is "your name"
        if self.currentLine == "your name":
            self.lineNum += 1  # go to next line
            nameprompt = self.textInBlock[self.lineNum]  # text that prompts for name
            self.name = input.name(screen, myfont, screen.drawbg(), screen.drawDialog("options"), nameprompt)
            # self.lineNum += 1  # once input is given, go to next line
            self.textUpdate(screen, "e")

        if type(self.currentLine) != list:
            if self.tone != self.toneList[self.lineNum] and self.toneList[self.lineNum]:
                self.currentLine = self.textInBlock[self.lineNum + 1]
                self.currentNPC = self.npcList[self.lineNum + 1]
                self.tone = None
                self.lineNum += 1
            else:
                pass
            screen.drawNPC(self.currentNPC)  # again, always Rindri
            screen.drawDialog(self.currentNPC)  # draw the dialog box belonging to the NPC
            self.drawText(self.currentLine)
        else:
            screen.drawDialog("options")
            self.drawChoices(self.currentLine, key)

    def write(self, tone):
        self.choicesList.append(tone)

newText = DialogText()
files = os.listdir("dialog")
for files in files:
    if "start" in files:  # we're only interested in the start file
        newText.start.append(False)


# main dialog loop
def loop():
    newDialog = DialogScreen()
    newText.dialog = True
    newText.getText()
    screen.fill((0, 0, 0))  # black
    newDialog.drawbg()
    newText.textUpdate(newDialog, "e")
    while newText.dialog:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if player presses X, quit the game
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    newText.textUpdate(newDialog, "e")
                elif event.key == pygame.K_s:
                    newText.textUpdate(newDialog, "s")
                elif event.key == pygame.K_w:
                    newText.textUpdate(newDialog, "w")
        pygame.display.flip()
    clock.tick(30)
    return newText.name  # saves name entered by player to use in other dialogs


def removeDuplicates(name, location, num):
    list = newText.choicesList
    i = 0
    while i < len(list)-1:
        if list[i] == list[i+1]:
            list.remove(list[i])
        else:
            i += 1
    for item in range(list.count(None)):
        list.remove(None)
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    filename = "participants/" + name + " choices, " + str(day) + "-" + str(month) + "-" + str(year) + ".csv"
    openFile = open(filename, "a")
    list.insert(0, location + str(num))
    toWrite = ",".join(list) + "\n"
    openFile.write(toWrite)
    openFile.close()