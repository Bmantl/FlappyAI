import abc
import Agent
from itertools import cycle


class Player:
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def update(self, game):
        pass


class Bird(Player):

    def __init__(self, name, images, startX, startY, flapSound, flapSpeed, hitMasks):
        Player.__init__(self, name)
        self.x = startX
        self.y = startY
        self.images = images
        self.currentImage = images[0]
        self.yVelocity = -9
        self.yMaxVelocity = 10
        self.yMinVelocity = -8
        self.yAcceleration = 1
        self.flapAcceleration = -9
        self.playerFlapped = False
        self.imageCycle = cycle([0, 1, 2, 1])
        self.flapped = False
        self.flapSound = flapSound
        self.flapSpeed = flapSpeed
        self.flapIterator = 0
        self.hitMasks = hitMasks
        self.currentHitMask = hitMasks[0]
        self.alive = True


    def update(self, game):
        self.flapIterator += 1
        if self.flapIterator % (game.fps / (self.flapSpeed * 3)) is 0:
            index = self.imageCycle.next()
            self.currentImage = self.images[index]
            self.currentHitMask = self.hitMasks[index]
            self.flapIterator = 0

        if game.currentScreen is game.GAME_SCREEN:
            if self.yVelocity < self.yMaxVelocity and not self.flapped:
                self.yVelocity += self.yAcceleration
            if self.flapped:
                self.flapped = False
                game.soundQueue.append(self.flapSound)
            self.y = max(self.y + min(self.yVelocity, game.BASE_Y - self.y - self.getHeight()), 0)
        game.imageQueue.append((self.currentImage, (self.x, self.y)))

    def flap(self):
        self.yVelocity = self.flapAcceleration
        self.flapped = True

    def getWidth(self):
        return self.currentImage.get_width()

    def getHeight(self):
        return self.currentImage.get_height()



    class FlappyState(Agent.RewardingState):
        def __init__(self, actionFn, reward, isTerminal):
            Agent.RewardingState.__init__(self, isTerminal)
            self.actionFn = actionFn
            self.reward = reward

        def getLegalActions(self):
            return self.actionFn()

        def getReward(self):
            return self.reward


class BirdPipeDist(Bird):
    FLAP = 'flap'
    NOOP = 'noop'

    def __init__(self, agent, name, image):
        Bird.__init__(self, agent, name, image)

    def createState(self, game):
        # TODO: implement pipe dist calculation!!!
        vPipeDist = None
        hPipeDist = None
        reward = None
        return BirdPipeDist.DistState(self.getLegalAction, reward, hPipeDist, vPipeDist, self.isTerminal(game))


    class DistState(Bird.FlappyState):
        def __init__(self, actionFn, reward, hPipeDist, vPipeDist, isTerminal):
            Bird.FlappyState(actionFn, reward, isTerminal)
            self.hPipeDist = hPipeDist
            self.vPipeDist = vPipeDist
