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
InitialRabbitCount = 100
InitialCoyoteCount   = 30 
InitialWolfCount   = 20

# regular intervals for reproduction
R_Repopulation = 6

# days to simulate
SimulationLength = 100

# size of NxM field 
FieldSize_N = 50
FieldSize_M = 50

# movement distr. weights
HungryWeight = 1
DangerWeight = 0.01

# how tall can it go?
MaxGrass = 10

# reproduction rates
RabbitBreedingRate = 0.10
CoyoteBreedingRate = 0.05
WolfBreedingRate   = 0.05

# movement distributions
RabbitMovement = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]
CoyoteMovement = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]
WolfMovement   = [0.025, 0.200, 0.025, 
                  0.200, 0.100, 0.200,
                  0.025, 0.200, 0.025]
# model parameter!
G = [1, 10]

################################################################################
## Data structures 
################################################################################

# cell structures (dicts will be easier)
Cell = { 'Grass'   : 0,
         'Rabbits' : [],
         'Coyotes' : [],
         'Wolves'  : [] }


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
            j = randint(0, self.n-1)
            self.grid[i][j][animal].append(deepcopy(new_organism))
        
    
    def sum_population(self, animal):
        # returns a sum of all organisms in the field of type animal
        return sum(sum([len(self.grid[row][col][animal]) for col in range(self.m)]) 
            for row in range(self.n)) 


    def print_grid(self):
        # prints grid for debugging purposes
        for row in range(self.n):
            for col in range(self.m):
                print("(%d, %d) - Grass: %d, Rabbits: %d, Coyotes: %d, Wolves: %d" %
                     (row, col, *self.get_cell_counts(row, col)))


    def get_cell_counts(self, row, col):
        # return a list of counts of each organism within a cell
        # return order: Grass, Rabbits, Coyotes, Wolves  
        return [self.grid[row][col]['Grass'], len(self.grid[row][col]['Rabbits']), 
                len(self.grid[row][col]['Coyotes']), len(self.grid[row][col]['Wolves'])]


    def get_entire_populations(self):
        # return a list of counts of each organism on the entire grid
        # return order: Grass, Rabbits, Coyotes, Wolves  
        return [sum([self.grid[row][col]['Grass'] for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Rabbits']) for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Coyotes']) for row in range(self.n) for col in range(self.m)]),
                sum([len(self.grid[row][col]['Wolves']) for row in range(self.n) for col in range(self.m)])]


    def produce_movement_distribution(self, row, col, animal, instance):
        # return a movement distribution for a given animal.
        # current algo: static movement distributions
        # an animal can move into any neighboring cell and is
        # agnostic to danger, food, or reproductive advantages
        # future work: score cells and normalize a distribution

        if(animal == 'Rabbits'):
            Movement = deepcopy(RabbitMovement)
            for row_bump in range(-1,2,1):
                for col_bump in range(-1,2,1):
                    new_row = row + row_bump
                    new_col = col + col_bump
                    
                    if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
                        Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
                        continue

                    counts = self.get_cell_counts(new_row, new_col)
                    if (counts[2] or counts[3]):
                        Movement[3*row_bump + col_bump] *= DangerWeight / (counts[2] + counts[3])
                    elif (counts[0] and instance.hungry()):
                        Movement[3*row_bump + col_bump] *= HungryWeight * counts[0]
            

        if(animal == 'Coyotes'):
            Movement = deepcopy(CoyoteMovement)
            for row_bump in range(-1,2,1):
                for col_bump in range(-1,2,1):
                    new_row = row + row_bump
                    new_col = col + col_bump
                     
                    if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
                        Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
                        continue

                    counts = self.get_cell_counts(new_row, new_col)
                    sum_counts = sum(counts)

                    # bear and burrito theory
                    if (counts[3]):
                        Movement[3*row_bump + col_bump] *= DangerWeight / (counts[3])
                    elif (sum_counts and instance.hungry()):
                        Movement[3*row_bump + col_bump] *= HungryWeight * sum_counts
            

        if(animal == 'Wolves'):
            Movement = deepcopy(WolfMovement)
            for row_bump in range(-1,2,1):
                for col_bump in range(-1,2,1):
                    new_row = row + row_bump
                    new_col = col + col_bump
                    
                    if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
                        Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
                        continue

                    counts = self.get_cell_counts(new_row, new_col)
                    Movement[3*row_bump + col_bump] = HungryWeight * sum(counts)
        
        tots = sum(Movement)
        Movement = [val / tots for val in Movement]
        return Movement

    def automate(self):
        
        # propogate to the next time frame
        # 1. growth
        # 2. mating
        # 3. interactions
        # 4. movement

        # 1. growth
        if (not (self.current_frame % self.grass_seed[1])):
            for row in range(self.n):                
                for col in range(self.m):                
                    self.grid[row][col]['Grass'] += self.grass_seed[0] if self.grid[row][col]['Grass'] < MaxGrass else 0
        
        # 2. interactions
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    for organism in self.grid[row][col][animal]:
                        organism.interact(self.grid[row][col])

        # check if any animal has starved to death
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
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
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    repopulate(self.grid[row][col][animal], animal)        

        # 4. movement 
        # (this is expensive, lots of copying)
        new_grid = deepcopy(self.initial_grid)
        for row in range(self.n):
            for col in range(self.m): 
                new_grid[row][col]['Grass'] = self.grid[row][col]['Grass']
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
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
    average_health = 0 if current_count == 0 else min([a.get_health() for a in arr])

    if(average_health > 0):

        if(animal == 'Rabbits'):
            to_add = ceil(current_count * RabbitBreedingRate)
            for spawn in range(to_add):
                arr.append(Rabbit(average_health))

        if(animal == 'Coyotes'):
            to_add = ceil(current_count * CoyoteBreedingRate)
            for spawn in range(to_add):
                arr.append(Coyote(average_health))

        if(animal == 'Wolves'):
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
    grid.init_population(InitialWolfCount, 'Wolves', Wolf())
    grid.init_population(InitialRabbitCount, 'Rabbits', Rabbit())
    grid.init_population(InitialCoyoteCount, 'Coyotes', Coyote())

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
            print(" Grass: %d, Rabbits: %d, Coyotes: %d, Wolves: %d" % (*grid.get_entire_populations(),))
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


