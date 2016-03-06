import Game
import sys
import pygame
import random
import Player
import Agent
from pygame.locals import *


class FlappyGame(Game.Game):
    FPS_SCORE_LIMIT = 10000

    SCREENWIDTH = 288
    SCREENHEIGHT = 512
    # amount by which base can maximum shift to left
    PIPEGAPSIZE = 130 # gap between upper and lower part of pipe
    BASE_Y = SCREENHEIGHT * 0.79

    # list of all possible players (tuple of 3 positions of flap)
    PLAYERS_LIST = (
        # red bird
        (
            'assets/sprites/redbird-upflap.png',
            'assets/sprites/redbird-midflap.png',
            'assets/sprites/redbird-downflap.png',
        ),
        # blue bird
        (
            # amount by which base can maximum shift to left
            'assets/sprites/bluebird-upflap.png',
            'assets/sprites/bluebird-midflap.png',
            'assets/sprites/bluebird-downflap.png',
        ),
        # yellow bird
        (
            'assets/sprites/yellowbird-upflap.png',
            'assets/sprites/yellowbird-midflap.png',
            'assets/sprites/yellowbird-downflap.png',
        ),
    )

    # list of backgrounds
    BACKGROUNDS_LIST = (
        'assets/sprites/background-day.png',
        'assets/sprites/background-night.png',
    )

    # list of pipes
    PIPES_LIST = (
        'assets/sprites/pipe-green.png',
        'assets/sprites/pipe-red.png',
    )

    FLAP = 'flap'
    NOOP = 'noop'

    def __init__(self, pipeGapY, noGUI = False, fps = 30):
        Game.Game.__init__(self, 'Flappy Bird', fps, (self.SCREENWIDTH, self.SCREENHEIGHT), noGUI)
        self.images, self.sounds, self.hitMasks = {}, {}, {}

        # load images
        self.images['numbers'] = (
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        self.images['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        # message sprite for welcome screen
        self.images['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
        # base (ground) sprite
        self.images['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

        # sounds
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'
        # load sounds
        self.sounds['die'] = pygame.mixer.Sound('assets/audio/die' + soundExt)
        self.sounds['hit'] = pygame.mixer.Sound('assets/audio/hit' + soundExt)
        self.sounds['point'] = pygame.mixer.Sound('assets/audio/point' + soundExt)
        self.sounds['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
        self.sounds['wing'] = pygame.mixer.Sound('assets/audio/wing' + soundExt)

        self.messagex = int((self.secreenSize[0] - self.images['message'].get_width()) / 2)
        self.messagey = int(self.secreenSize[1] * 0.12)
        self.resetNeeded = True

        # pipes
        self.upperPipes = []
        self.lowerPipes = []
        self.pipeVelX = -4
        self.pipeGapY = pipeGapY
        #general
        self.score = 0
        self.baseShift = 0
        self.baseX = 0

    def reset(self):
        if self.currentScreen is self.MAIN_SCREEN:
            self.resetMain()
        elif self.currentScreen is self.GAME_SCREEN:
            self.resetGame()

    def transitToGameScreen(self):
        self.player.flap()
        self.player.update(self)
        self.currentScreen = self.GAME_SCREEN
        self.resetNeeded = True
        return

    def resetMain(self):
        # select random background sprites
        randBg = random.randint(0, len(self.BACKGROUNDS_LIST) - 1)
        self.images['background'] = pygame.image.load(self.BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(self.PLAYERS_LIST) - 1)
        birdImages = (
            pygame.image.load(self.PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        playerx = int(self.secreenSize[0] * 0.2)
        playery = int((self.secreenSize[0] - birdImages[0].get_height()) / 2)

        # hitmask for player
        pHitMasks = (
            self.getHitmask(birdImages[0]),
            self.getHitmask(birdImages[1]),
            self.getHitmask(birdImages[2])
        )

        self.player = Player.Bird('bird', birdImages, playerx, playery, self.sounds['wing'], 3, pHitMasks)

        # select random pipe sprites
        pipeindex = random.randint(0, len(self.PIPES_LIST) - 1)
        self.images['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        self.hitMasks['pipe'] = (
            self.getHitmask(self.images['pipe'][0]),
            self.getHitmask(self.images['pipe'][1]),
        )

    def mainScreen(self, keyEvents):
        for event in keyEvents:
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                self.transitToGameScreen()
        # draw sprites

        self.imageQueue.append((self.images['message'], (self.messagex, self.messagey)))
        self.imageQueue.append((self.images['base'], (self.baseX, self.BASE_Y)))
        self.player.update(self)
        self.imageQueue.append((self.images['background'], (0, 0)))

    def resetGame(self):
        self.upperPipes = []
        self.lowerPipes = []
        # print ("Score is:" + str(self.score))
        self.score = 0

        self.baseShift = self.images['base'].get_width() - self.images['background'].get_width()

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = self.getRandomPipe()
        newPipe2 = self.getRandomPipe()

        # append new
        self.upperPipes.append({'x': self.SCREENWIDTH + 200, 'y': newPipe1[0]['y']})
        self.upperPipes.append({'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[0]['y']})

        # append new
        self.lowerPipes.append({'x': self.SCREENWIDTH + 200, 'y': newPipe1[1]['y']})
        self.lowerPipes.append({'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[1]['y']})

    def gameScreen(self, keyEvents):
        for event in keyEvents:
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if self.player.y > -2 * self.player.getHeight():
                    self.player.flap()

        # check for crash here
        crashTest = self.checkCrash()

        if crashTest[0]:
            self.player.alive = False
            self.currentScreen = self.MAIN_SCREEN
            self.resetNeeded = True
            return
            #reward = -1000

        # check for score
        playerMidPos = self.player.x + self.player.getWidth() / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe['x'] + self.images['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                self.soundQueue.append(self.sounds['point'])

        self.baseX = -((-self.baseX + 100) % self.baseShift)

        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.pipeVelX
            lPipe['x'] += self.pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < self.upperPipes[0]['x'] < 5:
            newPipe = self.getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if self.upperPipes[0]['x'] < -self.images['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # draw sprites
        self.showScore()
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            self.imageQueue.append((self.images['pipe'][0], (uPipe['x'], uPipe['y'])))
            self.imageQueue.append((self.images['pipe'][1], (lPipe['x'], lPipe['y'])))

        self.imageQueue.append((self.images['base'], (self.baseX, self.BASE_Y)))

        self.player.update(self)

        self.imageQueue.append((self.images['background'], (0, 0)))

    def gameOverScreen(self, keyEvents):
        pass

    def showScore(self):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(self.score))]
        totalWidth = 0  # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += self.images['numbers'][digit].get_width()

        Xoffset = (self.SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            self.imageQueue.append((self.images['numbers'][digit], (Xoffset, self.SCREENHEIGHT * 0.1)))
            Xoffset += self.images['numbers'][digit].get_width()

    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in range(image.get_width()):
            mask.append([])
            for y in range(image.get_height()):
                mask[x].append(bool(image.get_at((x, y))[3]))
        return mask

    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(self.BASE_Y * 0.6 - self.pipeGapY))
        gapY += int(self.BASE_Y * 0.2)
        pipeHeight = self.images['pipe'][0].get_height()
        pipeX = self.SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + self.pipeGapY},  # lower pipe
        ]

    def checkCrash(self):
        """returns True if player collders with base or pipes."""
        # if player crashes into ground
        if self.player.y + self.player.getHeight() >= self.BASE_Y - 1:
            return [True, True]
        else:

            playerRect = pygame.Rect(self.player.x, self.player.y,
                          self.player.getWidth(), self.player.getHeight())

            pipeW = self.images['pipe'][0].get_width()
            pipeH = self.images['pipe'][0].get_height()

            for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = self.player.currentHitMask
                uHitmask = self.hitMasks['pipe'][0]
                lHitmask = self.hitMasks['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]

    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in xrange(rect.width):
            for y in xrange(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False

    def performAgentAction(self):
        action = self.agent.getAction(self.getState())
        if action is self.FLAP:
            self.player.flap()

    def getState(self):
        legalActions = [self.NOOP, self.FLAP]
        if self.player.alive is True:
            reward = 1
        else:
            reward = -1000

        # update state
        relevantPipe = None
        rightPos = 1000
        for pipe in self.lowerPipes:
            rightPipePos = pipe['x'] + self.images['pipe'][0].get_width()
            if rightPos > rightPipePos > self.player.x:
                rightPos = rightPipePos
                relevantPipe = pipe


        pipe = relevantPipe
        hDistance = int(pipe['x'] + self.images['pipe'][0].get_width() - (self.player.x + self.player.getWidth())) / GRID_RESOLUTION
        vDistance = int(pipe['y'] - (self.player.y + self.player.getHeight())) / GRID_RESOLUTION
        stateData = (min(144 / GRID_RESOLUTION, hDistance), max(min(vDistance, (self.player.y + self.player.getHeight()) / GRID_RESOLUTION), -20))
        state = Agent.RewardingState(not self.player.alive, stateData, legalActions, reward)
        return state

