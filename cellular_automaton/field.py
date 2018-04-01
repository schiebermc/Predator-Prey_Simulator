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
InitialRabbitCount = 60
InitialCoyoteCount   = 20 
InitialWolfCount   = 10

# days until each organism will starve (on average)
# actual starvation is 2x, this is now grace period
RabbitStarvation = 2
CoyoteStarvation = 4
WolfStarvation = 6

# reproduction rates
RabbitBreedingRate = 0.10
CoyoteBreedingRate = 0.05
WolfBreedingRate   = 0.05

# regular intervals for reproduction
R_Repopulation = 6

# hunting constants
CoyoteCatchingRabbitRate = 0.25
WolfCatchingRabbitRate = 0.25
WolfCatchingCoyoteRate = 0.25

# days to simulate
SimulationLength = 1000

# size of NxM field 
FieldSize_N = 5
FieldSize_M = 5

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
G = [2, 5]

################################################################################
## Data structures 
################################################################################

# cell structures (dicts will be easier)
Cell = { 'Grass'   : 0,
         'Rabbits' : [],
         'Coyotes' : [],
         'Wolves'  : [] }

# class for animals
class Animal(object):

    def __init__(self, name, r_starvation, spawn_health):

        self.name = name 
        self.r_starvation = r_starvation
        self.days_to_starvation = spawn_health

    def move(self, current_row, current_col, total_rows, total_cols, movement):

        new_row = -1
        new_col = -1

        while(new_row >= 0 and new_row < total_rows and new_col >= 0 and new_col < total_cols):

            outcome = choice(9, 1, p=movement)   
            col_bump = ((outcome)  % 3) - 1
            row_bump = ((outcome + 1) // 3) - 1
            
            new_row = current_row + row_bump
            new_col = current_col + col_bump
            
        return new_row, new_col

    def eat(self):
    
        self.days_to_starvation = self.r_starvation * 2

    def dont_eat(self):
    
        self.days_to_starvation -= 1

    def hungry(self):
    
        return True if self.days_to_starvation <= self.r_starvation else False

    def starving(self):

        return True if self.days_to_starvation == 0 else False

    def get_health(self):

        return self.days_to_starvation


def repopulate(arr, animal):

    current_count = len(arr)
    average_health = 0 if current_count == 0 else sum([a.get_health() for a in arr]) / current_count

    if(average_health > 0):

        if(animal == 'Rabbits'):
            to_add = ceil(current_count * RabbitBreedingRate)
            for spawn in range(to_add):
                arr.append(Animal('Rabbit', RabbitStarvation, average_health))

        if(animal == 'Coyotes'):
            to_add = ceil(current_count * CoyoteBreedingRate)
            for spawn in range(to_add):
                arr.append(Animal('Coyote', CoyoteStarvation, average_health))

        if(animal == 'Wolves'):
            to_add = ceil(current_count * WolfBreedingRate)
            for spawn in range(to_add):
                arr.append(Animal('Wolf', WolfStarvation, average_health))


def interact(cell, animal):
        
    p = 0
    while(p != len(cell[animal])):

        if(animal == 'Rabbits'):
        
            if(cell[animal][p].hungry()):

                if(cell['Grass']):
            
                    cell['Grass'] -= 1
                    cell[animal][p].eat()
        
                else:
        
                    cell[animal][p].dont_eat()
                    if(cell[animal][p].starving()):
                        del cell[animal][p]
                        p -= 1

            else:
                cell[animal][p].dont_eat()


        if(animal == 'Coyotes'):

            if(cell[animal][p].hungry()):

                successful_hunt = False
                for hunt in range(len(cell['Rabbits'])):
                    outcome = randint(1, int(1 / CoyoteCatchingRabbitRate)) 
                    if(outcome == True):
                        successful_hunt = True 
                        break
                
                if(successful_hunt):
                    cell['Rabbits'].pop()
                    cell[animal][p].eat()
                    
                else:
                    cell[animal][p].dont_eat()
                    if(cell[animal][p].starving()):
                        del cell[animal][p]
                        p -= 1

            else:
                cell[animal][p].dont_eat()
                


        if(animal == 'Wolves'):

            if(cell[animal][p].hungry()):

                successful_hunt = False
                for hunt in range(len(cell['Rabbits'])):
                    outcome = randint(1, int(1 / WolfCatchingRabbitRate)) 
                    if(outcome == True):
                        successful_hunt = True 
                        cell['Rabbits'].pop()
                        break
                
                if(successful_hunt):
                    cell[animal][p].eat()
                    
                else:
                    cell[animal][p].dont_eat()

            else:    
                cell[animal][p].dont_eat()
            
            for hunt in range(len(cell['Coyotes'])):
                outcome = randint(1, int(1 / WolfCatchingCoyoteRate)) 
                if(outcome == True):
                    cell['Coyotes'].pop()
                    cell[animal][p].eat()

            
            if(cell[animal][p].starving()):
                del cell[animal][p]
                p -= 1
            
                    
        p += 1


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
                print("(%d, %d) - Grass: %d, Rabbits: %d, Coyotes: %d, Wolves: %d" %
                     (row, col, *self.get_cell_counts(row, col)))


    def get_cell_counts(self, row, col):
        # return a list of counts of each organism within a cell
        # return order: Grass, Rabbits, Coyotes, Wolves  
 
        return [self.grid[row][col]['Grass'], len(self.grid[row][col]['Rabbits']), 
                len(self.grid[row][col]['Coyotes']), len(self.grid[row][col]['Wolves'])]


    def get_grid_counts(self):
        # return a list of counts of each organism on the entire grid
        # return order: Grass, Rabbits, Coyotes, Wolves  

        return self.total_counts 


    def automate(self):
        
        # propogate to the next time frame

        # 1. growth
        # 2. mating
        # 3. interactions
        # 4. movement

        # growth
        if (not (self.current_frame % self.grass_seed[1])):
            for row in range(self.n):                
                for col in range(self.n):                
                    self.grid[row][col]['Grass'] += self.grass_seed[0] 
        
        
        # interactions
        for row in range(self.n):                
            for col in range(self.n):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    interact(self.grid[row][col], animal)        
       
 
        # mating
        for row in range(self.n):                
            for col in range(self.n):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    repopulate(self.grid[row][col][animal], animal)        

                
        self.current_frame += 1

# initialize grid
grid = CA(FieldSize_N, FieldSize_M, Cell, G)

# initialize populations
grid.init_population(InitialWolfCount, 'Wolves', Animal('Wolf', WolfStarvation, 2 *  WolfStarvation))
grid.init_population(InitialRabbitCount, 'Rabbits', Animal('Rabbit', RabbitStarvation, 2 *  RabbitStarvation))
grid.init_population(InitialCoyoteCount, 'Coyotes', Animal('Coyote', CoyoteStarvation, 2 *  CoyoteStarvation))

grid.print_grid()


# main simulation loop
for frame in range(1, SimulationLength):

    #pass
    #print(grid.get_grid_counts())
    grid.automate()    
    grid.print_grid()
    print('')




 
