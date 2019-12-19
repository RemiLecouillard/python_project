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

def runs( agent, width, number ):
    """ The real main. """
    wins = 0
    meanScore = 0 
    random.seed(0)
    for i in range(number):
        tortoise = agent()
        tortoise.init(width)
        tf = TortoiseFrame(width, 0, tortoise, True)
        print("Score:", tf.tw.score, "Time:", tf.tw.current_time)
        meanScore += tf.tw.score
        if tf.is_win():
            wins += 1
    print("\nStatistics")
    print("   Matches   : %d wins / %d loses." % (wins, number - wins))
    print("   Mean score: %.1f." % (meanScore / number))

def default( str ):
    return str + ' [Default: %default]'

def read_command( argv ):
    """ Processes the command used to run Tortoise from the command line. """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python run.py <options>
    EXAMPLES:   python run.py --agent ReflexBrain
                OR  python tortoise.py -a ReflexBrain
                    - run tortoise with the reflex agent
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-a', '--agent', dest = 'agent',
                      help = default('the agent to use'),
                      metavar = 'TYPE', default = 'ReflexBrain')
    parser.add_option('-w', '--width', dest = 'width',
                      help = default('World width'), default = 15)
    parser.add_option('-n', '--number', dest = 'number',
                      help = default('Number of executions'), default = 10)
    
    options, otherjunk = parser.parse_args(argv)

    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()
    
    # Choose a Tortoise solver
    try:
        module = __import__('agents')
        if options.agent in dir(module):
            agent = getattr(module, options.agent)
            args['agent'] = agent
        else:
            raise Exception('Unknown agent: ' + options.agent)
    except ImportError:
        raise Exception('No file agents.py')
    
    args['width'] = int(options.width)
    args['number'] = int(options.number)

    return args

if __name__ == '__main__':
    """ The main function called when tortoise.py is run
    from the command line:

    > python runs.py

    See the usage string for more details.

    > python runs.py --help
    > python runs.py -h """
    args = read_command(sys.argv[1:]) # Get game components based on input
    print("\n-------------------------------------------------------")
    for arg in sys.argv:
        print(arg, end=" ")
    print("\n-------------------------------------------------------")
    runs(**args)
