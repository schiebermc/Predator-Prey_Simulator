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

# printing knob, do you want to see the entire pop, or each cell pop per frame?
print_entire_pop = True

# data collection knob
log_cells = True

# initial population sizes
InitialRabbitCount = 60
InitialCoyoteCount   = 20 
InitialWolfCount   = 10

# days until each organism will starve (on average)
# actual starvation is 2x, this is now grace period
RabbitStarvation = 2
CoyoteStarvation = 3
WolfStarvation = 3

# reproduction rates
RabbitBreedingRate = 0.40
CoyoteBreedingRate = 0.05
WolfBreedingRate   = 0.05

# regular intervals for reproduction
R_Repopulation = 6

# hunting constants
CoyoteCatchingRabbitRate = 0.05
WolfCatchingRabbitRate = 0.05
WolfCatchingCoyoteRate = 0.01

# days to simulate
SimulationLength = 100

# size of NxM field 
FieldSize_N = 50
FieldSize_M = 50

# movement distr. weights
HungryWeight = 1
DangerWeight = 0.01

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

# how tall can it go?
MaxGrass = 10

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

# class for animals
class Animal(object):

    def __init__(self, name, r_starvation, spawn_health):

        self.name = name 
        self.r_starvation = r_starvation
        self.days_to_starvation = spawn_health

    def move(self, current_row, current_col, total_rows, total_cols, movement_distro):

        new_row = -1
        new_col = -1

        while(new_row < 0 or new_row >= total_rows or new_col < 0 or new_col >= total_cols):
            
            outcome = choice(9, 1, p=movement_distro)[0]   
            col_bump = ((outcome)  % 3) - 1
            row_bump = ((outcome) // 3) - 1
            
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
        #    for row_bump in range(-1,2,1):
        #        for col_bump in range(-1,2,1):
        #            new_row = row + row_bump
        #            new_col = col + col_bump
        #            
        #            if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
        #                Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
        #                continue

        #            counts = self.get_cell_counts(new_row, new_col)
        #            if (counts[2] or counts[3]):
        #                Movement[3*row_bump + col_bump] *= DangerWeight / (counts[2] + counts[3])
        #            elif (counts[0] and instance.hungry()):
        #                Movement[3*row_bump + col_bump] *= HungryWeight * counts[0]
        #    

        if(animal == 'Coyotes'):
            Movement = deepcopy(CoyoteMovement)
        #    for row_bump in range(-1,2,1):
        #        for col_bump in range(-1,2,1):
        #            new_row = row + row_bump
        #            new_col = col + col_bump
        #             
        #            if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
        #                Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
        #                continue

        #            counts = self.get_cell_counts(new_row, new_col)
        #            sum_counts = sum(counts)
        #            if (counts[3]):
        #                Movement[3*row_bump + col_bump] *= DangerWeight / (counts[3])
        #            elif (sum_counts and instance.hungry()):
        #                Movement[3*row_bump + col_bump] *= HungryWeight * sum_counts
        #    

        if(animal == 'Wolves'):
            Movement = deepcopy(WolfMovement)
        #    for row_bump in range(-1,2,1):
        #        for col_bump in range(-1,2,1):
        #            new_row = row + row_bump
        #            new_col = col + col_bump
        #            
        #            if(new_row < 0 or new_row >= self.n or new_col < 0 or new_col >= self.m):
        #                Movement[3*(row_bump+1) + (col_bump+1)] = 0.0               
        #                continue

        #            counts = self.get_cell_counts(new_row, new_col)
        #            Movement[3*row_bump + col_bump] = HungryWeight * sum(counts)
        #            #if ((counts[0])):
        #            #    Movement[3*row_bump + col_bump] *= HungryWeight * (counts[0])
        #            #if ((counts[1] or counts[2]) and instance.hungry()):
        #            #    Movement[3*row_bump + col_bump] *= HungryWeight * (counts[1] + counts[2])
        #    
        
        tots = sum(Movement)
        Movement = [val / tots for val in Movement]
        return Movement

    def automate(self):
        
        # propogate to the next time frame

        # 1. growth
        # 2. mating
        # 3. interactions
        # 4. movement

        # growth
        if (not (self.current_frame % self.grass_seed[1])):
            for row in range(self.n):                
                for col in range(self.m):                
                    self.grid[row][col]['Grass'] += self.grass_seed[0] if self.grid[row][col]['Grass'] < MaxGrass else 0
        
        # interactions
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    interact(self.grid[row][col], animal)        
       
        # mating
        for row in range(self.n):                
            for col in range(self.m):                
                for animal in ['Rabbits', 'Coyotes', 'Wolves']:
                    repopulate(self.grid[row][col][animal], animal)        

        # movement (this is expensive, lots of copying)
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
    # the new spawn will start with the minimum hunger level of current animals

    current_count = len(arr)
    average_health = 0 if current_count == 0 else min([a.get_health() for a in arr])

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
    # all animal interactions, mostly feeding and hunting
    # 1. Rabbits eat
    # 2. Coyotes hunt Rabbits
    # 3. Wolves hunt Rabbits
    # 4. Wolves hunt Coyotes    
    
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


################################################################################
## main simulation loop
################################################################################

if __name__ == "__main__":

    # initialize grid
    grid = CA(FieldSize_N, FieldSize_M, Cell, G)
    
    # initialize populations
    grid.init_population(InitialWolfCount, 'Wolves', Animal('Wolf', WolfStarvation, 2 *  WolfStarvation))
    grid.init_population(InitialRabbitCount, 'Rabbits', Animal('Rabbit', RabbitStarvation, 2 *  RabbitStarvation))
    grid.init_population(InitialCoyoteCount, 'Coyotes', Animal('Coyote', CoyoteStarvation, 2 *  CoyoteStarvation))
    
    if(log_cells):
        wfile = open('logged_cells.txt', 'a')

    # main simulation loop
    for frame in range(1, SimulationLength + 1):
    
        print('Frame: %d ~~~~~~~~~~~~~~~~~~~~~~~~~~' % frame)
        grid.automate()    
        if(print_entire_pop):
            print(" Grass: %d, Rabbits: %d, Coyotes: %d, Wolves: %d" % (*grid.get_entire_populations(),))
        else:
            grid.print_grid()

        if(log_cells):
            for row in range(FieldSize_N):
                for col in range(FieldSize_N):
                    counts = grid.get_cell_counts(row, col)
                    outcome = 0
                    for i in range(3, -1, -1):
                        if(counts[i]):
                            outcome = i + 1
                            break
                    wfile.write("%d %d %d\n" % (row, col, outcome))        
                        
        print('')


    if(log_cells):
        wfile.close()

        

 
