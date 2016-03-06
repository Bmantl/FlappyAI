import FlappyGame
import AgentFlappyGame
import Agent

pipeGapYs = range(130, 160, 10)
trainingRuns = 10000
epsilons = [0, 0.005, 0.001]
alphas = [0.1, 0.3, 0.7]
gammas = [0.99, 0.7, 0.5]
gridRess = [1, 2]

for pipeGapY in pipeGapYs:
    for alpha in alphas:
        for gamma in gammas:
            for epsilon in epsilons:
                for gridRes in gridRess:
                    agent = Agent.QLearningAgent(alpha=alpha, numTraining=trainingRuns, gamma=gamma, epsilon=epsilon)
                    flapGame = AgentFlappyGame.AgentFlappy(pipeGapY, agent, gridRes=gridRes, noGUI=True, trainingTime=180, csvFilename='test1.csv')
                    flapGame.startGame()
