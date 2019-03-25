
from random import randint
from numpy.random import choice

# hunting constants
CoyoteCatchingRabbitRate = 0.05
WolfCatchingRabbitRate = 0.02
WolfCatchingCoyoteRate = 0.01 

# days until each organism will starve (on average)
# actual starvation is 2x, this is now grace period
RabbitStarvation = 2
CoyoteStarvation = 3
WolfStarvation = 4

class Animal(object):

    # base class for animals
    # the essential stuff that all animals do

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
        #print("a %s is eating" % self.name)
        self.days_to_starvation = self.r_starvation * 2

    def dont_eat(self):
        self.days_to_starvation -= 1

    def hungry(self):
        return True if self.days_to_starvation <= self.r_starvation else False

    def starving(self):
        return True if self.days_to_starvation == 0 else False

    def get_health(self):
        return self.days_to_starvation


class Rabbit(Animal):

    def __init__(self, health=2*RabbitStarvation):
        Animal.__init__(self, 'Rabbit', RabbitStarvation, health) 

    def interact(self, cell):

        if(self.hungry()):
            
            if(cell['Grass']):
                cell['Grass'] -= 1
                self.eat()
            
            else:
                self.dont_eat() 

        else:
            self.dont_eat()

                
class Coyote(Animal):

    def __init__(self, health=2*CoyoteStarvation):
        Animal.__init__(self, 'Coyote', CoyoteStarvation, health) 

    
    def interact(self, cell):

        if(self.hungry()):

            successful_hunt = False
            for hunt in range(len(cell['Rabbits'])):
                outcome = randint(1, int(1 / CoyoteCatchingRabbitRate)) 
                if(outcome == True):
                    successful_hunt = True 
                    break
            
            if(successful_hunt):
                cell['Rabbits'].pop() # just pop the last one. it didnt' matter
                self.eat()
                
            else:
                self.dont_eat()

        else:
            self.dont_eat()
            

class Wolf(Animal):

    def __init__(self, health=2*WolfStarvation):
        Animal.__init__(self, 'Wolf', WolfStarvation, health) 

    def interact(self, cell):
        
        if(self.hungry()):

            successful_hunt = False
            for hunt in range(len(cell['Rabbits'])):
                outcome = randint(1, int(1 / WolfCatchingRabbitRate)) 
                if(outcome == 1):
                    successful_hunt = True 
                    break
        
            if(successful_hunt):
                cell['Rabbits'].pop() # just pop the last one. it didnt' matter
                self.eat()
                
            else:
                self.dont_eat()
        
        else:    
            self.dont_eat()

        for hunt in range(len(cell['Coyotes'])):
            outcome = randint(1, int(1 / WolfCatchingCoyoteRate)) 
            if(outcome == 1):
                cell['Coyotes'].pop() # this is effective, right..?
                self.eat()



