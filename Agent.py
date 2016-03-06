import abc
import random
import util


class State:
    def __init__(self, isTerminal, stateData, legalActions):
        self.isTerminal = isTerminal
        self.stateData = stateData
        self.legalActions = legalActions

    def getLegalActions(self):
        return self.legalActions


class RewardingState(State):
    def __init__(self, isTerminal, stateData, legalActions, reward):
        State.__init__(self, isTerminal, stateData, legalActions)
        self.reward = reward

    def getReward(self):
        return self.reward


class Agent:
    def __init__(self, id):
        self.id = id

    @abc.abstractmethod
    def getAction(self, state):
        pass


class ValueEstimationAgent(Agent):

    def __init__(self, alpha=1.0, epsilon=0.05, gamma=0.8, numTraining = 10):
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(gamma)
        self.numTraining = int(numTraining)

    @abc.abstractmethod
    def getQValue(self, state, action):
        pass

    @abc.abstractmethod
    def getValue(self, state):
        pass

    @abc.abstractmethod
    def getPolicy(self, state):
        pass


class ReinforcementAgent(ValueEstimationAgent):
    def __init__(self, actionFn = None, numTraining=10000, epsilon=0.001, alpha=0.7, gamma=0.99, rewardFn = None):
        ValueEstimationAgent.__init__(self, alpha, epsilon, gamma, numTraining)

        if actionFn is None:
            actionFn = lambda state: state.getLegalActions()
        if rewardFn is None:
            rewardFn = lambda state: state.getReward()
        self.actionFn = actionFn
        self.rewardFn = rewardFn
        self.lastState = None
        self.lastAction = None
        self.episodeCounter = 0
        self.accumTrainRewards = 0.0
        self.accumTestRewards = 0.0
        self.lastState = None
        self.episodeRewards = 0

    @abc.abstractmethod
    def update(self, nextState):
        pass

    def getLegalActions(self, state):
        return self.actionFn(state)

    def getReward(self, state):
        return self.rewardFn(state)

    def transit(self, nextState):
        self.episodeRewards += self.getReward(nextState)
        self.update(nextState)

    def startEpisode(self):
        self.lastState = None
        self.lastAction = None
        self.episodeRewards = 0.0

    def stopEpisode(self):
        if self.episodeCounter < self.numTraining:
            self.accumTrainRewards += self.episodeRewards
        else:
            self.accumTestRewards += self.episodeRewards
        self.episodeCounter += 1
        if self.episodeCounter >= self.numTraining:
            # Take off the training wheels
            self.epsilon = 0.0    # no exploration
            self.alpha = 0.0      # no learning

    def isInTraining(self):
        return self.episodeCounter < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()


class QLearningAgent(ReinforcementAgent):
    def __init__(self, **args):
        ReinforcementAgent.__init__(self, **args)
        self.qValues = util.Counter()

    def getQValue(self, state, action):
        value = self.qValues[(state.stateData, action)]
        return 0.0 if value is None else value

    def getValue(self, state):
        actions = self.getLegalActions(state)
        if actions.__len__() is 0:
            return 0.0

        value = -float('inf')
        for action in actions:
            qValue = self.getQValue(state, action)
            if value is None or qValue > value:
                value = max(value, qValue)

        return value

    def getPolicy(self, state):
        actions = self.getLegalActions(state)

        if actions.__len__() is 0:
            return None

        value = bestAction = None
        for action in actions:
            qValue = self.getQValue(state, action)
            if value is None or qValue > value:
                value = qValue
                bestAction = action

        return bestAction

    def getAction(self, state):
        # Pick Action
        self.transit(state)
        self.lastState = state
        legalActions = self.getLegalActions(self.lastState)

        self.lastAction = None if legalActions.__len__() is 0 \
            else random.choice(legalActions) if util.flipCoin(self.epsilon) \
            else self.getPolicy(self.lastState)

        return self.lastAction

    def update(self, nextState):
        if self.lastState is None:
            return
        qValue = self.getQValue(self.lastState, self.lastAction)
        self.qValues[(self.lastState.stateData, self.lastAction)] = qValue + \
            self.alpha * (self.getReward(nextState) + (self.discount * self.getValue(nextState)) - qValue)