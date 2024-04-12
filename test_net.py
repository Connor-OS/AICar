import pickle
import neat

from recorder import PygameRecord
from vector_racing import indefinite_game_loop as drive_car
from vector_racing import Car
import visualize

with open("example_net.txt", "rb") as file:
    nn = pickle.load(file)

with open("example_course.txt", "rb") as file:
    course = pickle.load(file)

# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

winner_net = neat.nn.FeedForwardNetwork.create(nn, config)

visualize.draw_net(config, nn, True)

recorder = PygameRecord("output.gif", 30)

drive_car(Car(brain=winner_net), course)