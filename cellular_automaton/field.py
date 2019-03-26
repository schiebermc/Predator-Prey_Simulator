# CSE 6730: Project 2
# Modeling Population dynamics using cellular automata

# Author:
#   Matthew Schieber

from time import sleep
from math import ceil
from time import time
from copy import deepcopy
from random import sample
from random import randint
from numpy.random import normal
from numpy.random import choice
from collections import namedtuple
from gifgen import GifCreator
from functools import reduce
from zoo import Rabbit
from zoo import Coyote
from zoo import Wolf

################################################################################
## Read-only globals ~ Simulation constants and parameters
################################################################################

# printing knob, do you want to see the entire pop, or each cell pop per frame?
# True: prints the total number of each species on the grid (suggested)
# False: prints the total number of each species in each cell on the grid
print_entire_pop = True

# movie generation knob
generate_movie = True

# initial population sizes
InitialRabbitCount = 200
InitialCoyoteCount   = 50 
InitialWolfCount   = 50

# regular intervals for reproduction
R_Repopulation = 6

# days to simulate
SimulationLength = 100

# size of NxM field 
FieldSize_N = 300
FieldSize_M = 300

# movement distr. weights
HungryWeight = 1
DangerWeight = 0.01

# how tall can it go?
MaxGrass = 2

# reproduction rates
RabbitBreedingRate = 0.20
CoyoteBreedingRate = 0.05
WolfBreedingRate   = 0.05

# movement distributions
MOVEMENT_DISTRIBUTIONS = {
    "Rabbit" :  [[0.025, 0.200, 0.025], 
                 [0.200, 0.100, 0.200],
                 [0.025, 0.200, 0.025]],
                
    "Coyote" :  [[0.025, 0.200, 0.025], 
                 [0.200, 0.100, 0.200],
                 [0.025, 0.200, 0.025]],

    "Wolf"   :  [[0.025, 0.200, 0.025], 
                 [0.200, 0.100, 0.200],
                 [0.025, 0.200, 0.025]]
                        }

PREDATORS_OF = {"Rabbit" : ["Coyote", "Wolf"],
                "Coyote" : ["Wolf"],
                "Wolf"   : []}

PREY_OF =     {"Rabbit" : ["Grass"],
                "Coyote" : ["Rabbit"],
                "Wolf"   : ["Rabbit", "Coyote"]}

# model parameter!
G = [1, 20]

################################################################################
## Data structures 
################################################################################

# cell structures (dicts will be easier)
Cell = { 'Grass'   : 0,
         'Rabbit' : [],
         'Coyote' : [],
         'Wolf'  : [] }

# cellular automaton
class CA(object):
    
    def __init__(self, n, m, cell, seed):
        # saves n and instantiates the grid according to the cell structure    

        self.n = n
        self.m = m
        self.grass_seed = seed
        self.current_frame = 0
        self.grid = [[deepcopy(cell) for col in range(m)] for row in range(n)]
        
        # save a copy of the initial grid for updates later in automate
        self.initial_grid = deepcopy(self.grid)


    def init_population(self, spawn_count, animal, new_organism):
        # initializes the grid with m organisms of type animal
        # current algo: totally random drop of m animals, may not be realistic
        for spawn in range(spawn_count):
            i = randint(0, self.n-1)
            j = randint(0, self.m-1)
            self.grid[i][j][animal].append(deepcopy(new_organism))
        
    
    def sum_population(self, animal):
        # returns a sum of all organisms in the field of type animal
        return sum(sum([len(self.grid[row][col][animal]) for col in range(self.m)]) 
            for row in range(self.n)) 


    def print_grid(self):
        # prints grid for debugging purposes
        for row in range(self.n):
            for col in range(self.m):
                print("(%d, %d) - Grass: %d, Rabbit: %d, Coyote: %d, Wolf: %d" %
                     (row, col, *self.get_cell_counts(row, col)))


    def get_cell_counts(self, row, col):
        # return a list of counts of each organism within a cell
        # return order: Grass, Rabbit, Coyote, Wolf  
        return [self.grid[row][col]['Grass'], len(self.grid[row][col]['Rabbit']), 
                len(self.grid[row][col]['Coyote']), len(self.grid[row][col]['Wolf'])]


    def get_cell_counts_dict(self, row, col):
        # return a dict of counts of each organism within a cell
        counts = {}
        for species, val in self.grid[row][col].items():
            if(isinstance(val, int)):
                counts[species] = val
            elif(isinstance(val, list)):
                counts[species] = len(val)
            else:
                raise Exception("this shouldn't happen")
        return counts

    def get_entire_populations(self):
        # return a list of counts of each organism on the entire grid
        # return order: Grass, Rabbit, Coyote, Wolf  
        return [sum([self.grid[row][col]['Grass'] for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Rabbit']) for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Coyote']) for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Wolf']) for row in range(self.n) for col in range(self.m)])]


    def produce_movement_distribution(self, row, col, animal, instance):
        # return a movement distribution for a given animal.
        # current algo: static movement distributions
        # an animal can move into any neighboring cell and is
        # agnostic to danger, food, or reproductive advantages
        # future work: score cells and normalize a distribution
        # none of the discription is true anymore             
       
        movement = deepcopy(MOVEMENT_DISTRIBUTIONS[animal])
        for row_bump in range(-1,2,1):
            for col_bump in range(-1,2,1):
                new_row = row + row_bump
                new_col = col + col_bump
                
                # not possible to move to this cell, set p(cell) = 0.0
                if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
                    movement[row_bump][col_bump] = 0.0
                    continue

                counts = self.get_cell_counts_dict(new_row, new_col)
                
                # the goal here is to increase the goodness of a cell 
                # depending on whether the cell contains food or danger
                # elif is added to avoid food if the cell is dangerous
                nprey = sum([counts[prey] for prey in PREY_OF[animal]])
                npredators = sum([counts[predator] for predator in PREDATORS_OF[animal]])
                if (npredators):
                    movement[row_bump][col_bump] *= DangerWeight / (npredators)
                
                elif (nprey and instance.hungry()):
                    movement[row_bump][col_bump] *= HungryWeight * nprey
        
        # normalize the distribution and return
        tots = sum([sum(row) for row in movement])
        movement = [[val / tots for val in row] for row in movement]
        
        # unroll the matrix and return
        movement = reduce(lambda x, y : x+y, movement)
        return movement


    def automate(self):
        
        # propogate to the next time frame
        # 1. growth
        # 2. mating
        # 3. interactions
        # 4. movement

        # 1. growth
        if (self.current_frame % self.grass_seed[1] == 0):
            for row in range(self.n):                
                for col in range(self.m):                
                    self.grid[row][col]['Grass'] += self.grass_seed[0] if self.grid[row][col]['Grass'] < MaxGrass else 0
        
        # 2. interactions
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbit', 'Coyote', 'Wolf']:
                    for organism in self.grid[row][col][animal]:
                        organism.interact(self.grid[row][col])

        # check if any animal has starved to death
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbit', 'Coyote', 'Wolf']:
                    # we need to delete animals while iterating
                    ind = 0
                    while(ind != len(self.grid[row][col][animal])):
                        if(self.grid[row][col][animal][ind].starving()):
                            self.grid[row][col][animal].pop(ind)
                        else:
                            ind += 1

        # 3. mating
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbit', 'Coyote', 'Wolf']:
                    repopulate(self.grid[row][col][animal], animal)        

        # 4. movement 
        # (this is expensive, lots of copying)
        new_grid = deepcopy(self.initial_grid)
        for row in range(self.n):
            for col in range(self.m): 
                new_grid[row][col]['Grass'] = self.grid[row][col]['Grass']
                for animal in ['Rabbit', 'Coyote', 'Wolf']:
                    for instance in self.grid[row][col][animal]:
                        movement_distro = self.produce_movement_distribution(row, col, animal, instance)
                        new_row, new_col = instance.move(row, col, self.n, self.m, movement_distro)
                        new_grid[new_row][new_col][animal].append(instance)
        
        # update grid
        self.grid = new_grid
 
        # update frame 
        self.current_frame += 1

################################################################################
## Miscelaneous simulation machinery
################################################################################

def repopulate(arr, animal):
    # repopulate an animal population within a cell 
    # given list arr is the current population of animal within a cell
    # the new spawn will start with the MINIMUM hunger level of current animals

    current_count = len(arr)
    average_health = 0 if current_count == 0 else max([a.get_health() for a in arr])

    if(average_health > 0):

        if(animal == 'Rabbit'):
            to_add = ceil(current_count * RabbitBreedingRate)
            for spawn in range(to_add):
                arr.append(Rabbit(average_health))

        if(animal == 'Coyote'):
            to_add = ceil(current_count * CoyoteBreedingRate)
            for spawn in range(to_add):
                arr.append(Coyote(average_health))

        if(animal == 'Wolf'):
            to_add = ceil(current_count * WolfBreedingRate)
            for spawn in range(to_add):
                arr.append(Wolf(average_health))
    

################################################################################
## main simulation loop
################################################################################

if __name__ == "__main__":

    # initialize grid
    grid = CA(FieldSize_N, FieldSize_M, Cell, G)
    
    # initialize populations
    grid.init_population(InitialWolfCount, 'Wolf', Wolf())
    grid.init_population(InitialRabbitCount, 'Rabbit', Rabbit())
    grid.init_population(InitialCoyoteCount, 'Coyote', Coyote())

    # for generating move of simulation
    if(generate_movie):
        figure_list = []

    # main simulation loop
    for frame in range(1, SimulationLength + 1):
    
        # propogate the CA
        grid.automate()    
        
        # print info to the terminal
        print('Frame: %d ~~~~~~~~~~~~~~~~~~~~~~~~~~' % frame)
        if(print_entire_pop):
            print(" Grass: %d, Rabbit: %d, Coyote: %d, Wolf: %d" % (*grid.get_entire_populations(),))
        else:
            grid.print_grid()
        print('')

        # get the info of each cell on the grid and append it to image list
        if(generate_movie):
            image = []
            for i in range(FieldSize_N):
                image.append([[] for cell in range(FieldSize_M)])
                for j in range(FieldSize_M):
                    image[i][j] = grid.get_cell_counts(i, j)
            figure_list.append(image)

    if(generate_movie):
        gc = GifCreator(figure_list, save=True, filename='giffy', rule='')
        gc.create_fig() 


