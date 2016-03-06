import FlappyGame
import AgentFlappyGame
import Agent
import easygui

ValueIndeces = {'trainRuns': 0, 'epsilon': 1, 'alpha': 2, 'gamma': 3, 'pipeGapY': 4,
                'fps': 5, 'agent': 6, 'gridRes': 7, 'dataType': 8}

def main():
    msg = "Enter the game settings"
    title = "AI - Flappy Bird Settings:"
    fieldNames = ["training runs", "exploration(epsilon)", "learning rate(alpha)","discount factor(gamma)", "pipe vertical gap", "FPS",
              "Agent", "Grid resolution", "dataType"]
    fieldValues = [10000, 0, 0.7, 0.99, 130, 30, True, 4, 1]  # we start with blanks for the values
    fieldValues = easygui.multenterbox(msg, title, fieldNames, fieldValues)

    isAgent = fieldValues[ValueIndeces['agent']]
    pipeGapY = int(fieldValues[ValueIndeces['pipeGapY']])
    fps = int(fieldValues[ValueIndeces['fps']])
    if isAgent == 'False':
        flapGame = FlappyGame.FlappyGame(pipeGapY, fps=fps)
    else:
        alpha = float(fieldValues[ValueIndeces['alpha']])
        gamma = float(fieldValues[ValueIndeces['gamma']])
        epsilon = float(fieldValues[ValueIndeces['epsilon']])
        trainingRuns = int(fieldValues[ValueIndeces['trainRuns']])
        gridRes = int(fieldValues[ValueIndeces['gridRes']])
        dataType =  int(fieldValues[ValueIndeces['dataType']])

        agent = Agent.QLearningAgent(alpha=alpha, numTraining=trainingRuns, gamma=gamma, epsilon=epsilon)
        if dataType is 1:
            flapGame = AgentFlappyGame.AgentFlappy(pipeGapY, agent, gridRes=gridRes, noGUI=True, trainingTime=600)
        elif dataType is 2:
            flapGame = AgentFlappyGame.AgentFlappyMidPipe(pipeGapY, agent, gridRes=gridRes, noGUI=True, trainingTime=600)
        elif dataType is 3:
            flapGame = AgentFlappyGame.AgentFlappyHorizontal(pipeGapY, agent, gridRes=gridRes, noGUI=True, trainingTime=600)
        elif dataType is 4:
            flapGame = AgentFlappyGame.AgentFlappyAll(pipeGapY, agent, gridRes=gridRes, noGUI=True, trainingTime=600)

    flapGame.startGame()

if __name__ == '__main__':
    main()