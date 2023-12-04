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

NUMLEARNERS = 1

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
def updatePredDict(enemyMoveToPredict, actualEnemyMove , ourMoves, pastDict):
    pastSamples = [[[0, 0], [0, 0], [0, 0]]] * NUMLEARNERS

    if enemyMoveToPredict in pastDict:
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

        accuracy = (1+correctPredictions)/(1+incorrectPredictions+correctPredictions)

        if accuracy > maxAccuracy:
            maxAccuracy = accuracy
            predictionNum = idx
    if maxAccuracy <= 0.7:
        return np.random.randint(0, 3)
    else:
        return predictions[predictionNum]





# --- LEARNERS ---

# [Basic] === 1
# Prob learner. Does not care about transitions, returns most common result of opponent given a mem threshold
def learner1(move):
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



class MyAgent20878339(rl_agent.AbstractAgent):
    def __init__(self, num_actions, name="bot_agent"):
        assert num_actions > 0
        self._num_actions = num_actions  # 3

        self.learners = [learner1(0)]
        self.predictions = [0] * len(self.learners)

        for learner in self.learners:
            next(learner)

        # Keep track of how successful predictions have been in the past
        self.personalHistory = {}
        self.enemyHistory = {}
        self.enemyPlusPersonal = {}
        self.totalNumberOfPredictions = 0

    def step(self, time_step, is_evaluation=False):
        if time_step.last():
            return

        game, state = pyspiel.deserialize_game_and_state(time_step.observations["serialized_state"])

        action = 1

        if len(state.history()) >= 6:
            2 + 2
        if len(state.history()) >= 4:
            moveToPredictOn = state.history()[-3]
            moveTheyActuallyDid = state.history()[-1]

            updatePredDict(moveToPredictOn, moveTheyActuallyDid, self.predictions, self.enemyHistory)

        if len(state.history()) != 0:
            pastAction = state.history()[-1]

            for i in range(0, len(self.learners)):
                self.predictions[i] = beatPred(self.learners[i].send(pastAction))

            action = determineBestMove(pastAction, self.predictions, self.enemyHistory)

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

agents = [
    my_agent,
    create_roshambo_bot_agent(1, 3, roshambo_bot_names, rockbot)
]

print("Starting eval run.")

avg_eval_returns = eval_agents(env, agents, num_players, 1, verbose=True)

print("Avg return ", avg_eval_returns)
