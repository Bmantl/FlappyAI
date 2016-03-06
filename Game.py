import sys
import pygame
from pygame.locals import *
import abc


class Game:

    MAIN_SCREEN = 'main'
    GAME_SCREEN = 'game'
    GAME_OVER_SCREEN = 'gameOver'

    def __init__(self, name, fps, screenSize, noGUI = False, noSound = False):
        self.noSound = noSound
        self.name = name
        self.player = None
        self.npcs = {}
        self.secreenSize = screenSize  # (w, h)
        self.fps = fps
        self.noGUI = noGUI
        self.soundQueue = []
        self.imageQueue = []
        self.currentScreen = None
        self.gameOverInfo = None
        self.screens = {self.MAIN_SCREEN: self.mainScreen, self.GAME_SCREEN: self.gameScreen,
                        self.GAME_OVER_SCREEN: self.gameOverScreen}
        pygame.init()
        self.fpsClock = pygame.time.Clock()
        self.resetNeeded = False
        self.screen = pygame.display.set_mode(screenSize)
        self.running = True

    def startGame(self):
        pygame.display.set_caption(self.name)
        self.currentScreen = self.MAIN_SCREEN
        self.gameLoop()

    def gameLoop(self):
        while self.running:
            if self.resetNeeded:
                self.reset()
                self.resetNeeded = False
            keyEvents = pygame.event.get()
            for event in keyEvents:
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            self.screens[self.currentScreen](keyEvents)
            if not self.noGUI:
                self.draw()
                self.playSounds()
                self.fpsClock.tick(self.fps)
            else:
                self.clearQueues()

    def clearQueues(self):
        self.imageQueue = []
        self.soundQueue = []

    def draw(self):
        while len(self.imageQueue) > 0:
            imageInfo = self.imageQueue.pop()
            self.screen.blit(imageInfo[0], imageInfo[1])
        pygame.display.update()

    def playSounds(self):
        if self.noSound:
            self.soundQueue = []
            return
        while len(self.soundQueue) > 0:
            self.soundQueue.pop().play()

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def mainScreen(self, keyEvents):
        pass

    @abc.abstractmethod
    def gameScreen(self, keyEvents):
        pass

    @abc.abstractmethod
    def gameOverScreen(self, keyEvents):
        pass
