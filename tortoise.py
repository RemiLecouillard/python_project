#! /usr/bin/env python
# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file tortoise.py
#
# @author Régis Clouard

import sys
import random
from tortoiseworld import TortoiseFrame

def run_agents( agent, speed, width, random_seed ):
    """ The real main. """
    if random_seed >=0:
        random.seed(random_seed)
    agent.init(width)
    tf = TortoiseFrame(width, speed, agent, False)
    print("Score:", tf.tw.score, "Time:", tf.tw.current_time)

def default( str ):
    return str + ' [Default: %default]'

def read_command( argv ):
    """ Processes the command used to run Tortoise from the command line. """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python tortoise.py <options>
    EXAMPLES:   python tortoise.py --agent ReflexBrain
                OR  python tortoise.py -a ReflexBrain
                    - run tortoise with the reflex agent
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-a', '--agent', dest = 'agent',
                      help = default('The agent to use'),
                      metavar = 'TYPE', default = 'ReflexBrain')
    parser.add_option('-w', '--width', dest = 'width',
                      help = default('World width'), default = 15)
    parser.add_option('-s', '--speed', dest = 'speed',
                      help = default('Speed'), default = 40)
    parser.add_option('-r', '--random-seed', dest = 'random_seed',
                      help = default('Random'), default = -1)
    
    options, otherjunk = parser.parse_args(argv)

    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()
    
    # Choose a Tortoise solver
    try:
        module = __import__('agents')
        if options.agent in dir(module):
            agent = getattr(module, options.agent)
            args['agent'] = agent()
        else:
            raise Exception('Unknown agent: ' + options.agent)
    except ImportError:
        raise Exception('No file agents.py')
    
    args['width'] = int(options.width)
    args['speed'] = int(options.speed)
    args['random_seed'] = int(options.random_seed)
    return args

if __name__ == '__main__':
    """ The main function called when tortoise.py is run
    from the command line:

    > python tortoise.py

    See the usage string for more details.

    > python tortoise.py --help
    > python tortoise.py -h """
    args = read_command(sys.argv[1:]) # Get game components based on input
    print("\n-------------------------------------------------------")
    for arg in sys.argv:
        print(arg, end=" ")
    print("\n-------------------------------------------------------")
    run_agents(**args)
