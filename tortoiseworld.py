# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file tortoiseworld.py
#
# @author Régis Clouard

# Definition of the tortoise world
# and its visual rendering.

import sys
if sys.version_info.major >= 3:
    import tkinter as Tkinter
else:
    import Tkinter
from math import *
import random
import time
from utils import *

class TortoiseFrame( Tkinter.Frame ):
    """
    This is the class for the window displaying the tortoise and its world.
    """

    tortoise_image_on_canvas = False
    
    def __init__( self, grid_size, simulation_speed, tortoise_brain, mute ):
        """
        Creates the visual rendering of the tortoise world.
        """
        Tkinter.Frame.__init__(self, None)
        self.mute = mute
        if simulation_speed > 200:
            self.simulation_speed = 200
        else:
            self.simulation_speed = simulation_speed
        self.master.title('Tortoise World')
        self.canvas = Tkinter.Canvas(self, width = 40 * grid_size, height = 40 * grid_size + 60, bg = 'white')
        self.canvas.pack(expand = 1, anchor = Tkinter.CENTER)
        self.pack()
        self.tkraise()
        self.dog_canvas = None
        # Create the world
        self.tw = TortoiseWorld(grid_size, tortoise_brain)
        self.images = {}
        for img in ['wall', 'lettuce', 'pond', 'ground', 'stone', 'tortoise-n', 'tortoise-s', 'tortoise-w', 'tortoise-e', 'tortoise-dead', 'dog-n', 'dog-s', 'dog-w', 'dog-e', 'dog-a', ]:
            self.images[img] = Tkinter.PhotoImage(file = './images/' + img + '.gif')
        for y in range(grid_size):
            for x in range(grid_size):
                self.canvas.create_image(x * 40, y  *40, image = self.images['ground'], anchor = Tkinter.NW)                
                if self.tw.worldmap[y][x] != 'ground':
                    self.canvas.create_image(x * 40, y * 40, image = self.images[self.tw.worldmap[y][x]], anchor = Tkinter.NW)
        # Set up a table for handling the tortoise images to use for each direction
        self.direction_tortoise_image_table = ['tortoise-n', 'tortoise-e', 'tortoise-s', 'tortoise-w']
        self.direction_dog_image_table = ['dog-n', 'dog-e', 'dog-s', 'dog-w', 'dog-a']
        # Set up text item for drawing info
        self.text_item = self.canvas.create_text(40, grid_size * 40, anchor = Tkinter.NW, text = '')
        self.win = False
        if self.mute:
            self.runWithoutGraphics()
        else:
            self.runWithGraphics()
            
    def runWithGraphics( self ):
            self.after(1, self.step)
            self.mainloop()

    def runWithoutGraphics( self ):
        while not self.is_terminated():
            self.step()

    def step( self ):
        """
        Manages the game cycle.
        """
        # Update current time
        self.tw.current_time += 0.1

        # Move the tortoise 
        if self.tw.current_time >= self.tw.next_tortoise_time:
            self.tw.step_tortoise()
            # Update ground if necessary
            if self.tw.update_current_place:
                self.canvas.create_image(self.tw.xpos * 40, self.tw.ypos * 40, image = self.images[self.tw.worldmap[self.tw.ypos][self.tw.xpos]], anchor = Tkinter.NW)
            # Redraw tortoise
            tortoise_image = self.direction_tortoise_image_table[self.tw.direction]
            if self.tw.health <= 0:
                tortoiseImage = 'tortoise-dead'
            if self.tortoise_image_on_canvas != False:
                self.canvas.delete(self.tortoise_image_on_canvas)
            self.tortoise_image_on_canvas = self.canvas.create_image(self.tw.xpos * 40, self.tw.ypos * 40, image = self.images[tortoise_image], anchor = Tkinter.NW)

        # Move the dog
        if self.tw.current_time >= self.tw.next_dog_time:
            self.tw.step_dog()
            dogImage = self.direction_dog_image_table[self.tw.dog_direction]
            if self.dog_canvas != None:
                self.canvas.delete(self.dog_canvas)
            self.dog_canvas = self.canvas.create_image(self.tw.dog_position[0] * 40, self.tw.dog_position[1] * 40, image = self.images[dogImage], anchor = Tkinter.NW)

        # Display text information
        self.canvas.itemconfigure(self.text_item, text = 'Eaten: %2d Time: %4d Score: %3d Drink Level: %2d   Health: %2d Action: %-7s' % (self.tw.eaten, int(self.tw.current_time), self.tw.score, self.tw.drink_level, self.tw.health, self.tw.action))
        if not self.mute and not self.is_terminated() and self.tw.current_time <= self.tw.MAX_TIME:
            self.after(int(200 / self.simulation_speed), self.step)

    def is_terminated( self ):
        return self.tw.action == 'stop' 

    def is_win( self ):
        return self.tw.win

class TortoiseWorld():
    """
    The tortoise world as a map of cells.
    Manages the game cycle: moves both the dog and the
    tortoise, the latter according to the think() result.
    """
    LETTUCE_PROBABILITY = 6
    WATER_PROBABILITY = 20
    STONE_PROBABILITY = 10
    MAX_DRINK = 100
    MAX_HEALTH = 100
    MAX_TIME = 5000
    xpos, ypos = 1, 1
    drink_level = 0
    eaten = 0
    current_time = 0.0
    direction = 0 #north = 0, east = 1, south = 2, west = 3
    worldmap = None
    action = 'None'
    next_tortoise_time = 0
    next_dog_time = 0
    update_current_place = False
    score = 0
    health = MAX_HEALTH
    pain = False
    lettuce_count = 0;

    def __init__( self, grid_size, tortoise_brain ):
        self.dog_position = [grid_size - 2, grid_size - 5]
        self.dog_direction_vector = [0, 0]
        self.dog_direction = 0 #north = 0, east = 1, south = 2, west = 3
        self.direction_table = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
        self.drink_level = self.MAX_DRINK
        self.create_worldmap(grid_size)
        self.grid_size = grid_size
        self.tortoise_brain = tortoise_brain
        self.health = self.MAX_HEALTH
        self.pain = False
        self.win = False

    def step_tortoise( self ):
        """
        Moves the tortoise one step forward.
        """
        self.current_time = self.next_tortoise_time
        time_change = (int)(4 - (3 * float(self.drink_level) / self.MAX_DRINK))
        self.next_tortoise_time = self.current_time + time_change
        self.update_current_place = False
        dx, dy = self.direction_table[self.direction]

        # Sensing
        ahead = self.worldmap[self.ypos + dy][self.xpos + dx]
        here = self.worldmap[self.ypos][self.xpos] 
        free_ahead = (ahead not in ['stone', 'wall'])
        lettuce_ahead = (ahead == 'lettuce')
        lettuce_here = (here == 'lettuce')
        water_ahead = (ahead == 'pond')
        water_here = (here == 'pond')

        # See in which direction the dog is
        dgx, dgy = self.dog_position[0] - self.xpos, self.dog_position[1] - self.ypos
        rota, rotb = [(0, +1), (+1, 0), (0, -1), (-1, 0)], [(-1, 0), (0, +1), (+1, 0), (0, -1)]
        relX = rota[self.direction][0] * dgx + rotb[self.direction][0] * dgy
        relY = rota[self.direction][1] * dgx + rotb[self.direction][1] * dgy

        # Current sensor
        sensor = Sensor(free_ahead, lettuce_ahead, lettuce_here, water_ahead, water_here, self.drink_level, self.health, relX, relY, self.xpos, self.ypos, self.direction)
        
        timed_func = TimeoutFunction(self.tortoise_brain.think, 1000)
        try:
            start_time = time.time()
            self.action = timed_func(sensor)
        except TimeoutFunctionException:
            print("Timed out on a single move!")
            self.action = 'wait'
        self.pain = False

        # Perform action
        if self.action == 'left':
            self.direction = (self.direction - 1) % 4
            self.drink_level = max(self.drink_level - 1, 0)
        elif self.action == 'right':
            self.direction = (self.direction + 1) % 4
            self.drink_level = max(self.drink_level - 1, 0)
        elif self.action == 'forward':
            if free_ahead:
                self.xpos += dx
                self.ypos += dy
            else:
                self.health -= 1
                self.pain = True
            self.drink_level = max(self.drink_level - 2, 0)

        elif self.action == 'eat' and lettuce_here:
            self.drink_level = max(self.drink_level - 1, 0)
            self.eaten += 1
            self.worldmap[self.ypos][self.xpos] = 'ground'
            self.update_current_place = True

        elif self.action == 'drink' and water_here:
            self.drink_level = self.MAX_DRINK

        elif self.action == 'wait':
            self.drink_level = max(self.drink_level - 1, 0)

        # Update score
        if self.eaten == self.lettuce_count:
            print("You win!")
            self.action = "stop"
            self.win = True
        elif self.drink_level <= 0 or self.health <= 0:
            if self.drink_level <= 0:
                print("You died of thirst!")
                self.win = False
            else:
                print("You died!")
                self.win = False
            self.action = "stop"
            self.health = 0
            self.pain = True
#        self.score = self.eaten * 10 - int(sqrt(self.current_time / 100.0) * 10)
        self.score = self.eaten * 10 - int(self.current_time / 10.0)

    def step_dog( self ):
        """
        Moves the dog one step forward.
        """
        self.next_dog_time += 1.25
        # If the dog steps on the tortoise it hurts
        if self.dog_position[0] == self.xpos and self.dog_position[1] == self.ypos:
            self.health -= 5
        # The dog keeps moving - if possible and unless it decides to turn
        nx = self.dog_position[0]+self.dog_direction_vector[0]
        ny = self.dog_position[1]+self.dog_direction_vector[1]
        if nx >= 1 and ny >= 1 and nx < self.grid_size - 1 and ny < self.grid_size - 1 and self.worldmap[ny][nx] not in ['stone', 'wall'] and random.randint(0, 3) != 0:
            self.dog_position[0] = nx
            self.dog_position[1] = ny
        else:
            # Steer dog randomly - or towards the turtle
            if random.randrange(0, 3) == 0:
                self.dog_direction = random.randrange(0, 4)
            elif random.randrange(0, 2) == 0:
                if self.xpos > self.dog_position[0]:
                    self.dog_direction = 1
                elif self.xpos < self.dog_position[0]:
                    self.dog_direction = 3
                elif self.ypos > self.dog_position[1]:
                    self.dog_direction = 2
                elif self.ypos < self.dog_position[1]:
                    self.dog_direction = 0
                else:
                    self.dog_direction = 4
            else:
                if self.ypos > self.dog_position[1]:
                    self.dog_direction = 2
                elif self.ypos < self.dog_position[1]:
                    self.dog_direction = 0
                elif self.xpos > self.dog_position[0]:
                    self.dog_direction = 1
                elif self.xpos < self.dog_position[0]:
                    self.dog_direction = 3
                else:
                    self.dog_direction = 4
            self.dog_direction_vector = self.direction_table[self.dog_direction]

    def create_worldmap( self, grid_size ):
        """
        Builds a random world map.
        """
        self.worldmap = [ [ ((y in [0, grid_size - 1] or  x in [0, grid_size - 1]) and 'wall') or 'ground'
                        for x in range(grid_size)] for y in range(grid_size)]
        self.worldmap[1][1] = 'pond'
        # First put out the stones randomly
        for i in range(int((grid_size - 2) ** 2 / self.STONE_PROBABILITY)):
            ok = False
            while not ok: 
                (x, y) = random.randint(1, grid_size - 1), random.randint(1, grid_size - 1)
                if self.worldmap[y][x] == 'ground':
                    count_stones = 0
                    count_walls = 0
                    # Check that the stone will not be adjacent to two other stones, 
                    # or one other stone and a wall.
                    # This is to prevent the appearance of inaccessible areas.
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                           if self.worldmap[y + dy][x + dx] == 'stone':
                               count_stones += 1
                           if self.worldmap[y + dy][x + dx] == 'wall':
                               count_walls += 1
                    if count_stones == 0 or (count_stones <= 1 and count_walls == 0):
                        self.worldmap[y][x] = 'stone'
                        ok = True
                    elif random.random() <= 0.1:
                        ok = True
        # Then put out the lettuces randomly
        for i in range(int((grid_size - 2) ** 2 / self.LETTUCE_PROBABILITY)):
            ok = False
            while not ok: 
                (x, y) = random.randint(1, grid_size - 1), random.randint(1, grid_size - 1)
                if self.worldmap[y][x] == 'ground':
                    self.worldmap[y][x] = 'lettuce'
                    self.lettuce_count += 1;
                    ok = True
        # Finally put out the water ponds randomly
        for i in range(int((grid_size - 2) ** 2 / self.WATER_PROBABILITY)):
            ok = False
            while not ok: 
                (x, y) = random.randint(1, grid_size - 1), random.randint(1, grid_size - 1)
                if self.worldmap[y][x] == 'ground':
                    self.worldmap[y][x] = 'pond'
                    ok = True


class Sensor():

    def __init__( self, free_ahead, lettuce_ahead, lettuce_here, water_ahead, water_here, drink_level, health_level, dog_front, dog_right, tortoisex, tortoisey, tortoise_direction ):
        self.free_ahead = free_ahead
        self.lettuce_ahead = lettuce_ahead
        self.lettuce_here = lettuce_here
        self.water_ahead = water_ahead
        self.water_here = water_here
        self.drink_level = drink_level
        self.health_level = health_level
        self.dog_front = dog_front
        self.dog_right = dog_right
        self.tortoise_position = (tortoisex, tortoisey)
        self.tortoise_direction = tortoise_direction
