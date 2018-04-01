# CSE 6730: Project 2
# Modeling Population dynamics using cellular automata


# Authors:
#   Matthew Schieber
#   Jordi Wolfson-Pou
#   Abhay Dalmia


from time import sleep
from math import ceil
from time import time
from copy import deepcopy
from random import sample
from random import randint
from numpy.random import normal
from numpy.random import choice
from collections import namedtuple


################################################################################
## Read-only globals ~ Simulation constants and parameters
################################################################################

# initial population sizes
InitialRabbitCount = 30
InitialCayoteCount   = 4 
InitialWolfCount   = 4 

# days until each organism will starve (on average)
RabbitStarvation = 2
CayoteStarvation = 4
WolfStarvation = 6

# reproduction rates
RabbitBreedingRate = 0.10
CayoteBreedingRate = 0.02
WolfBreedingRate   = 0.02

# regular intervals for reproduction
R_Repopulation = 6

# hunting constants
CayoteCatchingRabbitRate = 0.25
WolfCatchingRabbitRate = 0.25

# days to simulate
SimulationLength = 2000

# how often to record states of system
RecordInterval = 5

# Time to sleep at each record interval
SleepTime = 0.001

# size of NxM field 
FieldSize_N = 10
FieldSize_M = 10

# movement distributions
RabbitMovement = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]
CayoteMovement = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]
WolfMovement   = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]

# model parameter!
G = [1, 6]

################################################################################
## Data structures 
################################################################################

# cell structures (dicts will be easier)
Cell = { 'Grass'   : 0,
         'Rabbits' : [],
         'Cayotes' : [],
         'Wolves'  : [] }

# class for animals
class animal(object):

    def __init__(self, name, movement, r_starvation):

        self.name = name 
        self.sex = randint(0, 1)
        self.movement = movement
        self.r_starvation = r_starvation
        self.days_to_starvation = r_starvation

    def move(self, current_row, current_col, total_rows, total_cols):

        new_row = -1
        new_col = -1

        while(new_row >= 0 and new_row < total_rows and new_col >= 0 and new_col < total_cols):

            outcome = choice(9, 1, p=self.movement)   
            col_bump = ((outcome)  % 3) - 1
            row_bump = ((outcome + 1) // 3) - 1
            
            new_row = current_row + row_bump
            new_col = current_col + col_bump
            
        return new_row, new_col

    def eat(self):
    
        self.days_to_starvation = self.r_starvation


# cellular automaton
class CA(object):
    
    def __init__(self, n, m, cell, seed):
        # saves n and instantiates the grid according to the cell structure    

        self.n = n
        self.m = m
        self.grass_seed = seed
        self.total_counts = {} 
        self.current_frame = 0
        self.grid = [[deepcopy(cell) for col in range(m)] for row in range(n)]
  
    def init_population(self, spawn_count, animal, new_organism):
        # initializes the grid with m organisms of type animal
        
        # current algo: totally random drop of m animals, may not be realistic
        for spawn in range(spawn_count):
            i = randint(0, self.n-1)
            j = randint(0, self.n-1)
            self.grid[i][j][animal].append(deepcopy(new_organism))
        
        # keep global tally of each animal
        try:
            self.total_counts[animal] += spawn_count
        except:
            self.total_counts[animal] = spawn_count

    
    def sum_population(self, animal):
        # returns a sum of all organisms in the field of type animal
        
        return sum(sum([len(self.grid[row][col][animal]) for col in range(self.m)]) 
            for row in range(self.n)) 


    def print_grid(self):
        # prints grid for debugging purposes

        for row in range(self.n):
            for col in range(self.m):
                print("(%d, %d) - Grass: %d, Rabbits: %d, Cayotes: %d, Wolves: %d" %
                     (row, col, *self.get_cell_counts(row, col)))

    def get_cell_counts(self, row, col):
        # return a list of counts of each organism within a cell
        # return order: Grass, Rabbits, Cayotes, Wolves  
 
        return [self.grid[row][col]['Grass'], len(self.grid[row][col]['Rabbits']), 
                len(self.grid[row][col]['Cayotes']), len(self.grid[row][col]['Wolves'])]

    def get_grid_counts(self):
        # return a list of counts of each organism on the entire grid
        # return order: Grass, Rabbits, Cayotes, Wolves  

        return self.total_counts 

        


    def automate(self):
        pass
        # propogate to the next time frame

        # 1. growth
        # 2. mating
        # 3. interactions
        # 4. movement

        
                

# initialize grid
grid = CA(FieldSize_N, FieldSize_M, Cell, G)

# initialize populations
grid.init_population(InitialWolfCount, 'Wolves', animal('Wolf', WolfMovement, WolfStarvation))
grid.init_population(InitialRabbitCount, 'Rabbits', animal('Rabbit', RabbitMovement, RabbitStarvation))
grid.init_population(InitialCayoteCount, 'Cayotes', animal('Cayote', CayoteMovement, CayoteStarvation))

grid.print_grid()


# main simulation loop
for frame in range(1, SimulationLength):

    print(grid.get_grid_counts())
    grid.automate()    

 
