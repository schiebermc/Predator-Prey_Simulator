
from random import randint
from numpy.random import choice

# days until each organism will starve (on average)
# actual starvation is 2x, this is now grace period
STARVATION_RATES = {"Rabbit" : 2,
                    "Coyote" : 4,
                    "Wolf"   : 4
                    }

# lists of foods for each herbivore
HERBIVORE_EATING_LIST = {"Rabbit" : ['Grass'] }

# rates at which predators can catch and kill a prey
PREY_HUNTING_RATES = {"Coyote" : [["Rabbit", 0.15]],
                      "Wolf"   : [["Rabbit", 0.1]]}

# rates at which predators can chase and kill a prey
COMPETITION_HUNTING_RATES = {"Coyote" : [],
                             "Wolf" : [["Coyote", 0.01]]}


class Animal():

    # base class for animals
    # the essential stuff that all animals do
    # eat, move

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


class Carnivore(Animal):

    def __init__(self, name, r_starvation, spawn_health, prey, competition):
    
        self.prey = prey
        self.competition = competition
        Animal.__init__(self, name, r_starvation, spawn_health) 

    def hunt_prey(self, cell):
        
        # hunt each type of prey in the current cell
        # TODO add neighborhood cells for hunting?
        for animal, hunting_rate in self.prey:

            successful_hunt = False
            for hunt in range(len(cell[animal])):
                outcome = randint(1, int(1 / hunting_rate)) 
                if(outcome == True):
                    successful_hunt = True 
                    break
            
            # if a hunt was successful, stop hunting, time to
            # rest up a fully belly
            if(successful_hunt):
                cell[animal].pop() 
                self.eat()
                break
                
        # hunting is exhausting, so failure results in lost health
        if(not successful_hunt):
            self.dont_eat()


    def chase_competition(self, cell):

        # if there is an animal in the competition list, this is
        # deemed as a more alpha carnivore. There is a chance this
        # carnivore will kill some of the compeition
        for animal, hunting_rate in self.competition:
            for hunt in range(len(cell[animal])):
                outcome = randint(1, int(1 / hunting_rate)) 
                if(outcome == 1):
                    cell[animal].pop() 
                    self.eat()


class Herbivore(Animal):

    def __init__(self, name, r_starvation, spawn_health, prey):
    
        self.prey = prey
        Animal.__init__(self, name, r_starvation, spawn_health) 


    def find_and_eat_food(self, cell):

        if(self.hungry()):
            
            if(cell['Grass']):
                cell['Grass'] -= 1
                self.eat()
            
            else:
                self.dont_eat() 

        else:
            self.dont_eat()
        

class Rabbit(Herbivore):

    def __init__(self, health=2*STARVATION_RATES["Rabbit"]):

        Herbivore.__init__(self, 'Rabbit', STARVATION_RATES["Rabbit"], 
                            health, HERBIVORE_EATING_LIST["Rabbit"])
   
 
    def interact(self, cell):

        self.find_and_eat_food(cell)

                
class Coyote(Carnivore):

    def __init__(self, health=2*STARVATION_RATES["Coyote"]):

        Carnivore.__init__(self, 'Coyote', 
                            STARVATION_RATES["Coyote"],
                            health,
                            PREY_HUNTING_RATES["Coyote"],
                            COMPETITION_HUNTING_RATES["Coyote"])

    def interact(self, cell):

        self.hunt_prey(cell)
        self.chase_competition(cell)        


class Wolf(Carnivore):

    def __init__(self, health=2*STARVATION_RATES["Wolf"]):

        Carnivore.__init__(self, 'Wolf', 
                            STARVATION_RATES["Wolf"],
                            health,
                            PREY_HUNTING_RATES["Wolf"],
                            COMPETITION_HUNTING_RATES["Wolf"])

    def interact(self, cell):

        self.hunt_prey(cell)
        self.chase_competition(cell)        
















