from random import random

import numpy as np

from open_spiel.python import rl_agent
from open_spiel.python import rl_environment
import pyspiel

# ============== Helpers ==============
env = rl_environment.Environment(
    "repeated_game(stage_game=matrix_rps(),num_repetitions=" +
    f"{pyspiel.ROSHAMBO_NUM_THROWS}," +
    f"recall={20})",
    include_full_state=True)


class BotAgent(rl_agent.AbstractAgent):
    """Agent class that wraps a bot.

  Note, the environment must include the OpenSpiel state in its observations,
  which means it must have been created with use_full_state=True.

  This is a simple wrapper that lets the RPS bots be interpreted as agents under
  the RL API.
  """

    def __init__(self, num_actions, bot, name="bot_agent"):
        assert num_actions > 0
        self._bot = bot
        self._num_actions = num_actions

    def restart(self):
        self._bot.restart()

    def step(self, time_step, is_evaluation=False):
        # If it is the end of the episode, don't select an action.
        if time_step.last():
            return
        _, state = pyspiel.deserialize_game_and_state(
            time_step.observations["serialized_state"])
        action = self._bot.step(state)
        probs = np.zeros(self._num_actions)
        probs[action] = 1.0
        return rl_agent.StepOutput(action=action, probs=probs)


#  We will use this function to evaluate the agents. Do not change.

def eval_agents(env, agents, num_players, num_episodes, verbose=False):
    """Evaluate the agent.

  Runs a number of episodes and returns the average returns for each agent as
  a numpy array.

  Arguments:
    env: the RL environment,
    agents: a list of agents (size 2),
    num_players: number of players in the game (for RRPS, this is 2),
    num_episodes: number of evaluation episodes to run.
    verbose: whether to print updates after each episode.
  """
    sum_episode_rewards = np.zeros(num_players)
    for ep in range(num_episodes):
        for agent in agents:
            # Bots need to be restarted at the start of the episode.
            if hasattr(agent, "restart"):
                agent.restart()
        time_step = env.reset()
        episode_rewards = np.zeros(num_players)
        while not time_step.last():
            agents_output = [
                agent.step(time_step, is_evaluation=True) for agent in agents
            ]
            action_list = [agent_output.action for agent_output in agents_output]
            time_step = env.step(action_list)
            episode_rewards += time_step.rewards
        sum_episode_rewards += episode_rewards
        if verbose:
            print(f"Finished episode {ep}, "
                  + f"avg returns: {sum_episode_rewards / (ep + 1)}")

    return sum_episode_rewards / num_episodes


def print_roshambo_bot_names_and_ids(roshambo_bot_names):
    print("Roshambo bot population:")
    for i in range(len(roshambo_bot_names)):
        print(f"{i}: {roshambo_bot_names[i]}")


def create_roshambo_bot_agent(player_id, num_actions, bot_names, pop_id):
    name = bot_names[pop_id]
    # Creates an OpenSpiel bot with the default number of throws
    # (pyspiel.ROSHAMBO_NUM_THROWS). To create one for a different number of
    # throws per episode, add the number as the third argument here.
    bot = pyspiel.make_roshambo_bot(player_id, name)
    return BotAgent(num_actions, bot, name=name)


# ============== Agent ================

# --- HELPERS ---

# Really basic function for calculating best response
def beatPred(expectedMove):
    match expectedMove:
        case 0:  # Get rock
            return 1  # -> return paper
        case 1:  # Get paper
            return 2  # -> return scissors
        case 2:  # Get scissors
            return 0  # -> return rock


# Update the positional accuracy of predictions
def updatePredDict(enemyMoveToPredict, actualEnemyMove, ourMoves, pastDict):
    pastSamples = np.array([[[0, 0], [0, 0], [0, 0]]] * NUM_LEARNERS)

    if enemyMoveToPredict in pastDict:
        if type(enemyMoveToPredict) == int:
            pastSamples = pastDict[enemyMoveToPredict] * FORGET_RATE
        else:
            pastSamples = pastDict[enemyMoveToPredict]
    for idx in range(0, len(ourMoves)):
        if ourMoves[idx] == beatPred(actualEnemyMove):
            pastSamples[idx][ourMoves[idx]][0] += 1
        elif ourMoves[idx] != actualEnemyMove:
            pastSamples[idx][ourMoves[idx]][1] += 1
    pastDict[enemyMoveToPredict] = pastSamples


def determineBestMove(enemyMove, predictions, history):
    maxAccuracy = 0
    predictionNum = 0

    for idx in range(0, len(predictions)):
        if enemyMove not in history:
            continue
        correctPredictions = history[enemyMove][idx][predictions[idx]][0]
        incorrectPredictions = history[enemyMove][idx][predictions[idx]][1]

        accuracy = (1 + correctPredictions) / (3 + incorrectPredictions + correctPredictions)

        if accuracy > maxAccuracy:
            maxAccuracy = accuracy
            predictionNum = idx

    return predictions[predictionNum], maxAccuracy


NUM_LEARNERS = 8
FORGET_RATE = 0.95


# --- LEARNERS ---

# [Dumb] === 1
# Plays rock
def dumbLearner1(move):
    while True:
        yield 0


# [Dumb] === 2
# Plays paper
def dumbLearner2(move):
    while True:
        yield 1


# [Dumb] === 3
# Plays Scissors
def dumbLearner3(move):
    while True:
        yield 2


# [Basic] === 1
# Prob learner. Does not care about transitions, returns most common result of opponent given a mem threshold
def basicLearner1(move):
    MEMORY = 7

    values = []

    numRock = 0
    numPaper = 0
    numScissors = 0
    while True:
        match move:
            case 0:  # Get rock
                numRock += 1
            case 1:  # Get paper
                numPaper += 1
            case 2:  # Get scissors
                numScissors += 1

        values.append(move)
        if len(values) > MEMORY:
            poppedVal = values.pop(0)
            match poppedVal:
                case 0:  # Get rock
                    numRock -= 1
                case 1:  # Get paper
                    numPaper -= 1
                case 2:  # Get scissors
                    numScissors -= 1

        if numRock >= numPaper and numRock >= numScissors:
            prediction = 0
        elif numPaper >= numRock and numPaper >= numScissors:
            prediction = 1
        else:
            prediction = 2
        move = yield prediction


# [Basic] === 2
# Prob learner. Does not care about transitions, returns most common result of opponent given a mem threshold
def basicLearner2(move):
    MEMORY = 15

    values = []

    numRock = 0
    numPaper = 0
    numScissors = 0
    while True:
        match move:
            case 0:  # Get rock
                numRock += 1
            case 1:  # Get paper
                numPaper += 1
            case 2:  # Get scissors
                numScissors += 1

        values.append(move)
        if len(values) > MEMORY:
            poppedVal = values.pop(0)
            match poppedVal:
                case 0:  # Get rock
                    numRock -= 1
                case 1:  # Get paper
                    numPaper -= 1
                case 2:  # Get scissors
                    numScissors -= 1

        if numRock >= numPaper and numRock >= numScissors:
            prediction = 0
        elif numPaper >= numRock and numPaper >= numScissors:
            prediction = 1
        else:
            prediction = 2
        move = yield prediction


# [Intermediate] === 1
# Constantly rotate values from rock to paper to scissors
def intermediate1(move):
    while True:
        move = yield (move + 1) % 3


# [Intermediate] === 2
# Constantly rotate values from rock to scissors to paper
def intermediate2(move):
    while True:
        move = yield (move - 1) % 3


# [Hard] === 1
# Keep track of most
def hard1(move):
    pastMove = 0
    likeyMoves = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    while True:
        likeyMoves[pastMove][move] += 1
        pastMove = move
        move = yield np.argmax(likeyMoves[move])


class MyAgent20878339(rl_agent.AbstractAgent):

    def resetAllValues(self):
        self.learners = [dumbLearner1(0), dumbLearner2(0), dumbLearner3(0), basicLearner1(0), basicLearner2(0),
                         intermediate1(0), intermediate2(0), hard1(0)]
        self.predictions = [0] * NUM_LEARNERS

        # === Keep track of how accurate bots have been for a specific move
        self.enemyHistory = {}

        self.threeHistory = {}

        self.totalNumberOfPredictions = 0
        self.playedRandom = 0

        self.winsWhenNotRandom = 0
        self.randomLast = True

        for learner in self.learners:
            next(learner)

    def __init__(self, num_actions, name="bot_agent"):
        assert num_actions > 0
        self._num_actions = num_actions  # 3

        self.resetAllValues()

    def printDebug(self, state):
        if len(state.history()) == 0:
            print(self.winsWhenNotRandom, " / ", self.totalNumberOfPredictions - self.playedRandom)
            self.resetAllValues()

        if not self.randomLast:
            if state.history()[-2] == beatPred(state.history()[-1]):
                self.winsWhenNotRandom += 1

    def updateHistory(self, state):
        self.randomLast = False

        if len(state.history()) >= 4:
            # -> History based on their last move
            moveToPredictOn = state.history()[-3]
            moveTheyActuallyDid = state.history()[-1]

            updatePredDict(moveToPredictOn, moveTheyActuallyDid, self.predictions, self.enemyHistory)

        if len(state.history()) >= 6:
            # -> History based on their 2 last moves and our last move
            moveToPredictOn = str(state.history()[-5]) + str(state.history()[-4]) + str(state.history()[-3])
            moveTheyActuallyDid = state.history()[-1]

            updatePredDict(moveToPredictOn, moveTheyActuallyDid, self.predictions, self.threeHistory)

    def calcMove(self, state):
        action = 1
        currentAccuracy = 0

        if len(state.history()) >= 2:

            # ============ Prediction based on transition ============

            pastAction = state.history()[-1]
            for i in range(0, len(self.learners)):
                self.predictions[i] = beatPred(self.learners[i].send(pastAction))

            pred, acc = determineBestMove(pastAction, self.predictions, self.enemyHistory)

            if acc > currentAccuracy:
                currentAccuracy = acc
                action = pred

        if len(state.history()) >= 4:

            pastAction = str(state.history()[-3]) + str(state.history()[-2]) + str(state.history()[-1])
            pred, acc = determineBestMove(pastAction, self.predictions, self.threeHistory)

            if acc > currentAccuracy:
                currentAccuracy = acc
                action = pred

        if currentAccuracy < 0.85:
            self.playedRandom += 1
            self.randomLast = True
            action = np.random.randint(0, 3)

        return action

    def step(self, time_step, is_evaluation=False):

        if time_step.last():
            return

        game, state = pyspiel.deserialize_game_and_state(time_step.observations["serialized_state"])

        self.printDebug(state)

        self.updateHistory(state)

        action = self.calcMove(state)

        self.totalNumberOfPredictions += 1
        probs = np.ones(self._num_actions) / self._num_actions
        return rl_agent.StepOutput(action=action, probs=probs)


# ============== Testing ================

my_agent = MyAgent20878339(3, name="robbie_agent")

num_players = 2

roshambo_bot_names = pyspiel.roshambo_bot_names()
roshambo_bot_names.sort()

print(print_roshambo_bot_names_and_ids(roshambo_bot_names))

greenberg = 14
copybot = 7
addshiftbot = 3
predbot = 28
sweetrock = 38
switchbot = 40
rockbot = 32
rotatebot = 33

'''
agents = [
    my_agent,
    create_roshambo_bot_agent(1, 3, roshambo_bot_names, 37)
]
eval_agents(env, agents, num_players, 1, verbose=True)
eval_agents(env, agents, num_players, 1, verbose=True)
'''

print("Starting eval run.")
for i in range(1, 40):
    print(i)
    agents = [
        my_agent,
        create_roshambo_bot_agent(1, 3, roshambo_bot_names, i)
    ]
    avg_eval_returns = eval_agents(env, agents, num_players, 1, verbose=True)
    print()
    print()

print("Avg return ", avg_eval_returns)
