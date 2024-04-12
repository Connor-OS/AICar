"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import neat
from vector_racing import indefinite_game_loop as drive_car
from vector_racing import Car
import pickle
import visualize

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        ai_car = Car(brain=net)
        genome.fitness = drive_car(ai_car)


# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(False))

# Run until a solution is found.
winner = p.run(eval_genomes)

# Display the winning genome.
print('\nBest genome:\n{!s}'.format(winner))

# Show output of the most fit genome against training data.
print('\nOutput:')
winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

with open("winning_net_04.txt", "wb") as file:
    pickle.dump(winner, file)

visualize.draw_net(config, winner, True)