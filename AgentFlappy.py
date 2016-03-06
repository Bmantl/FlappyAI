import Agent
import FlappyGame
import pygame
from pygame.locals import *
import time
import csv

class AgentFlappy(FlappyGame.FlappyGame):

    ALIVE_REWARD = 1
    DEATH_REWARD = -1000

    def __init__(self, pipeGapY, agent, noGUI = False, fps = 30, gridRes = 4, trainingTime = 600, csvFilename = None):
        FlappyGame.FlappyGame.__init__(self, pipeGapY, noGUI, fps)
        self.gridRes = gridRes
        self.agent = agent
        self.scoreSum = 0
        self.firstGame = True
        self.tempScreen = None
        self.learningScreen = pygame.image.load('assets/sprites/background-learning.png').convert_alpha()
        self.startTime = time.time()
        self.trainingTime = trainingTime
        self.csvFilename = csvFilename
        self.csvWriter = None
        self.highScore = 0
        self.lastScore = 0
        if csvFilename is not None:
            self.csvFile = open(csvFilename, 'ab+')
            self.csvWriter = csv.writer(self.csvFile)
            self.csvWriter.writerow(['epsilon', 'gamma', 'alpha',
                                     'pipeGap', 'gridRes'])
            self.csvWriter.writerow([str(self.agent.epsilon), str(self.agent.discount), str(self.agent.alpha),
                                     str(self.pipeGapY), str(self.gridRes)])
            self.csvWriter.writerow(['episodesLasted', 'AvgScore', 'highScore'])


    def mainScreen(self, keyEvents):
        self.lastScore = 0
        if self.firstGame:
            self.firstGame = False
        else:
            self.agent.stopEpisode()
            self.getStatistics()
            self.checkTime()
        self.transitToGameScreen()
        self.agent.startEpisode()

    def gameScreen(self, keyEvents):
        self.keyHandler(keyEvents)
        FlappyGame.FlappyGame.gameScreen(self, keyEvents)
        self.performAgentAction()
        self.checkTime()

    def performAgentAction(self):
        action = self.agent.getAction(self.getState())
        if action is self.FLAP:
            self.player.flap()

    def keyHandler(self, keyEvents):
        for event in keyEvents:
            if event.type == KEYDOWN and (event.key == K_0):
                self.fps = 30
                self.noGUI = True
                self.screen.blit(self.learningScreen, (0, 0))
                pygame.display.update()
            elif event.type == KEYDOWN and (event.key == K_1):
                self.noGUI = False
                self.fps = 30
            elif event.type == KEYDOWN and (event.key == K_2):
                self.noGUI = False
                self.fps = 60
            elif event.type == KEYDOWN and (event.key == K_3):
                self.noGUI = False
                self.fps = 120
            elif event.type == KEYDOWN and (event.key == K_4):
                self.noGUI = False
                self.fps = 240
            elif event.type == KEYDOWN and (event.key == K_s):
                self.noSound = not self.noSound

    def checkTime(self):
        if time.time() - self.startTime > self.trainingTime:
            self.running = False

    def getStatistics(self):
        self.scoreSum += self.score
        self.highScore = self.score if self.score > self.highScore else self.highScore
        # if self.highScore > 1000:
        #     self.agent.alpha = 0

        if self.agent.episodeCounter % 50 == 0:
            if self.csvWriter is not None:
                self.csvWriter.writerow([str(self.agent.episodeCounter), str(self.scoreSum / 50.0), str(self.highScore)])
            else:
                print("episode: " + str(self.agent.episodeCounter) + "\nScore Sum: " + str(self.scoreSum)
                      + "\nScore Avg: " + str(self.scoreSum / 50.0) + "\nHigh Score : " + str(self.highScore))
            self.scoreSum = 0
            self.highScore = 0

    def getState(self):
        legalActions = [self.NOOP, self.FLAP]
        if self.player.alive is True:
            reward = self.ALIVE_REWARD
        else:
            reward = self.DEATH_REWARD

        state = Agent.RewardingState(not self.player.alive, self.getStateData(), legalActions, reward)
        return state

    def getStateData(self):
        # update state
        relevantPipe = None
        rightPos = 1000
        for pipe in self.lowerPipes:
            rightPipePos = pipe['x'] + self.images['pipe'][0].get_width()
            if rightPos > rightPipePos > self.player.x:
                rightPos = rightPipePos
                relevantPipe = pipe

        pipe = relevantPipe
        hDistance = int(pipe['x'] + self.images['pipe'][0].get_width() - (self.player.x + self.player.getWidth())) / self.gridRes
        vDistance = int(pipe['y'] - (self.player.y + self.player.getHeight())) / self.gridRes
        return min(self.SCREENWIDTH / 2 / self.gridRes, hDistance), max(min(vDistance, (self.pipeGapY + 50 ) / self.gridRes), -50 / self.gridRes)


class AgentFlappyMidPipe(AgentFlappy):

    def __init__(self, pipeGapY, agent, noGUI = False, fps = 30, gridRes = 4, trainingTime = 600, csvFilename = None):
        AgentFlappy.__init__(self, pipeGapY, agent, noGUI, fps, gridRes, trainingTime, csvFilename)

    def getStateData(self):
        # update state
        relevantPipe = None
        rightPos = 1000
        for pipe in self.lowerPipes:
            rightPipePos = pipe['x'] + self.images['pipe'][0].get_width()
            if rightPos > rightPipePos > self.player.x:
                rightPos = rightPipePos
                relevantPipe = pipe

        pipe = relevantPipe
        hDistance = int(pipe['x'] + self.images['pipe'][0].get_width() - (self.player.x + self.player.getWidth())) / self.gridRes
        vDistance = (int(pipe['y'] - self.pipeGapY/2) - (self.player.y + self.player.getHeight()/2)) / self.gridRes
        return min(self.SCREENWIDTH / 2 / self.gridRes, hDistance), \
               max(min(vDistance, (self.pipeGapY / 2 + 20) / self.gridRes), -(self.pipeGapY / 2 + 20) / self.gridRes)


class AgentFlappyHorizontal(AgentFlappy):

    def __init__(self, pipeGapY, agent, noGUI = False, fps = 30, gridRes = 4, trainingTime = 600, csvFilename = None):
        AgentFlappy.__init__(self, pipeGapY, agent, noGUI, fps, gridRes, trainingTime, csvFilename)

    def getStateData(self):
        # update state
        relevantPipe = None
        rightPos = 1000
        for pipe in self.lowerPipes:
            rightPipePos = pipe['x'] + self.images['pipe'][0].get_width()
            if rightPos > rightPipePos > self.player.x:
                rightPos = rightPipePos
                relevantPipe = pipe

        pipe = relevantPipe
        if int(pipe['x'] - (self.player.x + self.player.getWidth())) > 0:
            hLoc = 'before'
        elif int(pipe['x'] + self.images['pipe'][0].get_width() - self.player.x) < 0:
            hLoc = 'after'
        else:
            hLoc = 'inside'
        vDistance = int(pipe['y'] - (self.player.y + self.player.getHeight())) / self.gridRes
        return hLoc, max(min(vDistance, (self.pipeGapY + 50) / self.gridRes), -50 / self.gridRes)


class AgentFlappyAll(AgentFlappy):

    def __init__(self, pipeGapY, agent, noGUI = False, fps = 30, gridRes = 4, trainingTime = 600, csvFilename = None):
        AgentFlappy.__init__(self, pipeGapY, agent, noGUI, fps, gridRes, trainingTime, csvFilename)

    def getStateData(self):
        # update state
        relevantPipe = None
        rightPos = 1000
        for pipe in self.lowerPipes:
            rightPipePos = pipe['x'] + self.images['pipe'][0].get_width()
            if rightPos > rightPipePos > self.player.x:
                rightPos = rightPipePos
                relevantPipe = pipe

        pipe = relevantPipe
        if int(pipe['x'] - (self.player.x + self.player.getWidth())) > 0:
            hLoc = 'before'
        elif int(pipe['x'] + self.images['pipe'][0].get_width() - self.player.x) < 0:
            hLoc = 'after'
        else:
            hLoc = 'inside'
        hDistance = int(pipe['x'] + self.images['pipe'][0].get_width() - (self.player.x + self.player.getWidth())) / self.gridRes
        vDistance = int(pipe['y']) - (self.player.y + self.player.getHeight()) / self.gridRes

        return max(min(vDistance, (self.pipeGapY + 50) / self.gridRes), -50 / self.gridRes), self.player.yVelocity