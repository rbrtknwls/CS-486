from random import random
import tensorflow as tf

import numpy as np

from open_spiel.python import rl_agent
from open_spiel.python import rl_environment
import pyspiel
import os.path


from tensorflow.keras import layers, models


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
            + f"avg returns: {sum_episode_rewards / (ep+1)}")

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

model = 2
if ( os.path.isfile("model.keras") ):
  model = tf.keras.models.load_model('RPS.keras')
else:
  model = models.Sequential()

  model.add(layers.LSTM(2000, return_sequences=False, dropout=0.1, recurrent_dropout=0.1, input_shape=(None, 2000)))

  model.add(layers.Dense(2000, activation='relu'))

  model.add(layers.Dense(64, activation='relu'))

  model.add(layers.Dropout(0.1))

  model.add(layers.Dense(3))

  model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
  )


MyMoves = []
YourMoves = []
class MyAgent20878339(rl_agent.AbstractAgent):
  def __init__(self, num_actions, name="bot_agent"):
    assert num_actions > 0
    self._num_actions = num_actions  # 3

  def step(self, time_step, is_evaluation=False):
    if time_step.last():
      return

    game, state = pyspiel.deserialize_game_and_state(time_step.observations["serialized_state"])
    if len(state.history())==0:
      action = 1
    else:
      action = state.history()[-1]
      YourMoves.append(state.history()[-1])
      MyMoves.append(action)
    probs = np.ones(self._num_actions) / self._num_actions
    return rl_agent.StepOutput(action=action, probs=probs)

# ============== Testing ================

my_agent = MyAgent20878339(3, name="robbie_agent")

num_players = 2

roshambo_bot_names = pyspiel.roshambo_bot_names()
roshambo_bot_names.sort()

p1_pop_id = 14   # adddriftbot2
agents = [
    my_agent,
    create_roshambo_bot_agent(1, 3, roshambo_bot_names, p1_pop_id)
]


print("Starting eval run.")

avg_eval_returns = eval_agents(env, agents, num_players, 1, verbose=True)

print("Avg return ", avg_eval_returns)

inputSection = np.zeros((2, 1000, 2000))
expected = np.zeros(1000)
for i in range(0, len(MyMoves)):
  for x in range(0, i):
    inputSection[i][x] = (1 + MyMoves[x])
    inputSection[i][1000+x] = (1 + YourMoves[x])

  expected[i] = (YourMoves[i])



model.fit(inputSection, expected)