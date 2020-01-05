# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file agents.py
#
# @author Régis Clouard

import random
import operator
import copy
import math
import utils
import abc
from enum import Enum



# Useful constants
EAT = 'eat'
DRINK = 'drink'
FORWARD = 'forward'
LEFT = 'left'
RIGHT = 'right'
WAIT = 'wait'

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)] # North, East, South, West

def add_position(a, b) :
	x = a[0] + b[0]
	y = a[1] + b[1]
	return (x, y)

class TortoiseBrain:
	"""
	The base class for various flavors of the tortoise brain.
	This an implementation of the Strategy design pattern.
	"""
	def think( self, sensor ):
		raise Exception("Invalid Brain class, think() not implemented")

class RandomBrain( TortoiseBrain ):
	"""
	An example of simple tortoise brain: acts randomly...
	"""
	def init( self, grid_size ):
		pass

	def think( self, sensor ):
		return random.choice([EAT, DRINK, LEFT, RIGHT, FORWARD, FORWARD, WAIT])

class ReflexBrain( TortoiseBrain ):
	def init( self, grid_size ):
		pass

	def think( self, sensor ):
		# case 1: danger: dog
		if abs(sensor.dog_front) < 3 and abs(sensor.dog_right) < 3:
			if sensor.dog_front <= 0:
				if sensor.free_ahead:
					return FORWARD
				elif sensor.dog_right > 0:
					return LEFT
				else:
					return RIGHT
			elif sensor.dog_front > 0:
				if sensor.dog_right > 0:
					return LEFT
				else:
					return RIGHT
		# increase the performance measure
		if sensor.lettuce_here and sensor.drink_level > 10: return EAT
		if sensor.water_ahead and sensor.drink_level < 50: return FORWARD
		if sensor.water_here and sensor.drink_level < 100: return DRINK
		# Nothing to do: move
		if sensor.free_ahead:
			return random.choice([FORWARD, RIGHT, FORWARD, WAIT, FORWARD, FORWARD, FORWARD])
		else:
			return random.choice([RIGHT, LEFT])
		return random.choice([EAT, DRINK, LEFT, RIGHT, FORWARD, FORWARD, WAIT])


class Square_type(Enum):
	WALL = 0
	WATER = 1
	LETTUCE = 2
	FREE = 3
	UNKNOWN = 4

class State:
	_map = []
	_map_size = 0
	_life = 100
	_thirst = 100
	_position = (1,1)
	_position_dog = (0,0)
	_direction = 0
	_isThirty = False
		
 #  ______                               _              
 # |  ____|                             (_)             
 # | |__    __  __   ___   _ __    ___   _   ___    ___ 
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|

class GoalBasedBrain( TortoiseBrain ):
	_state = State()
	
	def init( self, grid_size ):
		self.init_map(grid_size)
		
	def init_map(self, grid_size):
		self._state._map_size = grid_size
		for i in range(grid_size):
			self._state._map += [[]]
			for j in range(grid_size):
				if (i==0) or (j==0) or (j==grid_size-1) or (i==grid_size-1):
					self._state._map[i] += [Square_type.WALL]
				else:
					self._state._map[i] += [Square_type.UNKNOWN]

	def get_type_of_ahead_square(self, sensor):
		if sensor.free_ahead == 1:
			if sensor.lettuce_ahead == 1:
				return Square_type.LETTUCE
			if sensor.water_ahead == 1:
				return Square_type.WATER
			else:
				return Square_type.FREE
		return Square_type.WALL
	
	def get_type_of_my_square(self,sensor):
		if sensor.lettuce_here == 1:
			return Square_type.LETTUCE
		if sensor.water_here == 1:
			return Square_type.WATER
		else:
			return Square_type.FREE

	def get_position_of_dog(self, sensor):
		if sensor.tortoise_direction == 0:
			return (self._state._position[0] - sensor.tortoise_direction * sensor.dog_right ,self._state._position[1] + sensor.tortoise_direction * sensor.dog_front)
		else:
			return (self._state._position[0] + sensor.tortoise_direction * sensor.dog_front, self._state._position[1] + sensor.tortoise_direction * sensor.dog_right)

	def update_state(self, sensor):
		self._state._life = sensor.health_level
		self._state._thirst = sensor.drink_level
		self._state._position = sensor.tortoise_position
		self._state._position_dog = self.get_position_of_dog(sensor)
		self._state._direction = sensor.tortoise_direction

		self._state._map[self._state._position[0]][self._state._position[1]] = self.get_type_of_my_square(sensor)
		if sensor.tortoise_direction == 0:
			self._state._map[self._state._position[0]][self._state._position[1]-1] = self.get_type_of_ahead_square(sensor)
		if sensor.tortoise_direction == 1:
			self._state._map[self._state._position[0] + 1][self._state._position[1]] = self.get_type_of_ahead_square(sensor)
		if sensor.tortoise_direction == 2:
			self._state._map[self._state._position[0]][self._state._position[1] + 1] = self.get_type_of_ahead_square(sensor)
		if sensor.tortoise_direction == 3:
			self._state._map[self._state._position[0] - 1][self._state._position[1]] = self.get_type_of_ahead_square(sensor)

	def get_best_action(self):
		state = UCS_Drink_State(self._state._map, self._state._position, self._state._direction, self._state._map_size)
		path = self.uc_search(state)

		state_eat = UCS_Eat_State(self._state._map, self._state._position, self._state._direction, self._state._map_size)
		path_to_lettuce = self.uc_search(state_eat)

		print("water cost ", self.get_water_cost(path), " thirst ", self._state._thirst)

		if self.get_water_cost(path) > self._state._thirst - 10:
			self._state._isThirty = True

		if len(path_to_lettuce) != 0 or self._state._map[self._state._position[0]][self._state._position[1]] == Square_type.LETTUCE:
			print("meta action eat")
			return self.perform_meta_action_eat(path_to_lettuce)
		elif self._state._isThirty:
			print("meta action drink")
			return self.perform_meta_action_drink(path)
		else :
			print("meta action explore")
			return self.perform_meta_action_explore()

	def perform_meta_action_drink(self, path):
		if self._state._map[self._state._position[0]][self._state._position[1]] == Square_type.WATER:
			self._state._isThirty = False
			return DRINK
		
		return path[0]

	def perform_meta_action_eat(self, path):
		if self._state._map[self._state._position[0]][self._state._position[1]] == Square_type.LETTUCE:
			return EAT
		
		return path[0]

	def perform_meta_action_explore(self ) :
		if self._state._map[self._state._position[0]][self._state._position[1]] == Square_type.LETTUCE:
			return EAT

		state = UCS_Explore_State(self._state._map, self._state._position, self._state._direction, self._state._map_size)
		path = self.uc_search(state)

		return path[0]
		

	def get_water_cost(self, path) :
		cost = 0
		for step in path :
			if step == FORWARD:
				cost += 2
			if step == LEFT or step == RIGHT:
				cost += 1
		return cost

	def think( self, sensor ):
		"""
		Returns the best action with regard to the current state of the game.
		Available actions are [EAT, DRINK, LEFT, RIGHT, FORWARD, WAIT].

		sensors attributes:
		sensor.free_ahead: there is no stone or wall one step ahead (boolean).
		sensor.lettuce_ahead: there is a lettuce plant one step ahead (boolean).
		sensor.lettuce_here: there is a lettuce plant at the current position (boolean).
		sensor.water_ahead: there is water one step ahead (boolean).
		sensor.water_here :there is water at the current position (boolean).
		sensor.drink_level : the level of water in the tortoise’s body, ranging from 100 to 0.
		sensor.health_level: the level of health in the tortoise’s body, ranging from 100 to 0.
		sensor.dog_front: the relative position of the dog, ie. the number of cells in front (positive) or behind (negative) the tortoise that it is.
		sensor.dog_right: the relative position of the dog to the right, ie. the number of cells to the right (positive) or left (negative) of the tortoise that it is.
		sensor.tortoise_position: the tortoise coordinates (x,y).
		sensor.tortoise_direction: the tortoise direction between 0 (north), 1 (east), 2 (south), and 3 (west).


		Compute the tortoise direction (dx,dy) in the grid from the sensor absolute direction.
		e.g: North -> (0, -1); South -> (0, 1)
		(dx, dy) = DIRECTIONTABLE[sensor.tortoise_direction]

		Compute the coordinates of the dog from the tortoise direction.
		if directionx == 0:
			self.dogx = self.x - directiony * sensor.dog_right
			self.dogy = self.y + directiony * sensor.dog_front
		else:
			self.dogx = self.x + directionx * sensor.dog_front
			self.dogy = self.y + directionx * sensor.dog_right
		"""

		# *** YOUR CODE HERE ***"
		self.update_state(sensor)
		#print(self._state._map)
		action = self.get_best_action()
		print("action -> ", action)
		return action

	def uc_search( self, initial_state ):
		""" Uniform-Cost Search.

		It returns the path as a list of directions among
		{ Direction.left, Direction.right, Direction.up, Direction.down }
		"""

		# use a priority queue with the minimum queue.
		from utils import PriorityQueue
		open_list = PriorityQueue()
		open_list.push([(initial_state, None)], 0)
		closed_list = set([initial_state]) # keep already explored positions
        
		while not open_list.isEmpty():
		# Get the path at the top of the queue
			current_path, cost = open_list.pop()
			# Get the last place of that path
			current_state, current_direction = current_path[-1]
			#print("current_state -> ", current_state._position, " direction -> ", current_state._direction, " cost -> ", cost)

			# Check if we have reached the goal
			if current_state.is_goal_state():
				return (list (map(lambda x : x[1], current_path[1:])))
			else:
				# Check were we can go from here
				next_steps = current_state.get_successor_states()
				# Add the new paths (one step longer) to the queue
				for state, direction, weight in next_steps:
					# Avoid loop!
					if state not in closed_list:
						closed_list.add(state)
						open_list.push((current_path + [ (state, direction) ]), cost + weight)
		return []

class UCS_State :
	__metaclass__ = abc.ABCMeta
	_map = []
	_position = (0,0)
	_size = 0
	_direction = 0

	@abc.abstractmethod
	def get_instance(self, map, position, direction, size) :
		return

	def __hash__(self) :
		return hash((self._position,self._direction))

	def __eq__(self, other) :
		if self._position == other._position and self._direction == other._direction :
			return True
		return False

	def canGoTo(self, next_to) :
		if next_to[0] > 0 and next_to[0] < self._size and next_to[1] > 0 and next_to[1] < self._size and self._map[next_to[0]][next_to[1]] != Square_type.WALL and self._map[next_to[0]][next_to[1]] != Square_type.UNKNOWN:
			return True
		return False

	def __init__(self, map, position, direction, size) :
		self._map = copy.deepcopy(map)
		self._position = position
		self._size = size
		self._direction = direction

	def get_successor_states(self) :
		succ_list = []

		next_to = add_position(self._position,  DIRECTIONTABLE[self._direction])

		if (self.canGoTo(next_to)) :
			succ_state = self.get_instance(self._map, next_to, self._direction, self._size)
			succ_list.append((succ_state, FORWARD, 1))

		new_direction = (self._direction + 1) % 4
		succ_state = self.get_instance(self._map, self._position, new_direction, self._size)
		succ_list.append((succ_state, RIGHT, 1))

		new_direction = (self._direction - 1) % 4
		succ_state = self.get_instance(self._map, self._position, new_direction, self._size)
		succ_list.append((succ_state, LEFT, 1))

		return succ_list
		

class UCS_Drink_State(UCS_State) :

	def get_instance(self, map, position, direction, size) :
		return UCS_Drink_State(map, position, direction, size)

	def is_goal_state(self) :
		return self._map[self._position[0]][self._position[1]] == Square_type.WATER

class UCS_Explore_State(UCS_State) :

	def get_instance(self, map, position, direction, size) :
		return UCS_Explore_State(map, position, direction, size)

	def canGoTo(self, next_to) :
		if next_to[0] > 0 and next_to[0] < self._size and next_to[1] > 0 and next_to[1] < self._size and self._map[next_to[0]][next_to[1]] != Square_type.WALL:
			return True
		return False

	def is_goal_state(self) :
		return self._map[self._position[0]][self._position[1]] == Square_type.UNKNOWN

class UCS_Eat_State(UCS_State) :

	def get_instance(self, map, position, direction, size) :
		return UCS_Eat_State(map, position, direction, size)
	
	def is_goal_state(self) :
		return self._map[self._position[0]][self._position[1]] == Square_type.LETTUCE