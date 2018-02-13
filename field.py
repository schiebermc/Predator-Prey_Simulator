# By Matthew Schieber
# Application code
# Includes event handlers, class structures, and main loop

import engine
from time import sleep
from math import ceil
from time import time
from random import sample
from random import randint
from numpy.random import normal
import matplotlib.pyplot as plt

################################################################################
## Read-only globals ~ Simulation constants and parameters
################################################################################

# number of events executed
NEvents = 0

# initial population sizes
InitialRabbitCount = 30 
InitialWolfCount   = 4 

# days until each organism will starve (on average)
R_Starvation = 2
W_Starvation = 5

# Reproduction rates
RabbitBreedingRate = 0.20
WolfBreedingRate   = 0.05
R_Repopulation = 5

# Wolf hunting constants
RabbitsToHunt = 0.10
WolfCatchingRabbitRate = 0.25

# days to simulate
SimulationLength = 500

# how often to record states of system
RecordInterval = 5

# size of field
FieldSize = 500

# model parameter!
G = [1, 4]

################################################################################
## Data structures for events
################################################################################

# population class for both rabbits and wolves
class Population(object):
    
    def __init__(self, n, repopulation_rate, animal):
    
        self.n = n
        self.repopulation_rate = repopulation_rate
        self.used_keys = set([])
        self.alive = set([_ for _ in range(self.n)])
        self.animal = animal

    def schedule_all(self, global_data):

        for i in range(self.n):
            self.used_keys.add(i)
            if(self.animal == 'rabbit'):
                ScheduleEatGrass(i, global_data)    
            elif(self.animal == 'wolf'):
                ScheduleHuntRabbit(i, global_data)
            else:
                raise Exception("Incorrect animal type")
        if(self.animal == 'rabbit'):
            ScheduleRepopulation('REPOPULATE_RABBITS', global_data)
        else:
            ScheduleRepopulation('REPOPULATE_WOLVES', global_data)

    def kill(self, key):

        self.used_keys.remove(key)
        self.alive.remove(self.n-1)
        self.n -= 1

    def repopulate(self, global_data):

        # update how many animals are alive
        to_add = int(ceil(self.n * self.repopulation_rate))
        for i in range(self.n, self.n + to_add):
            self.alive.add(i)
        self.n += to_add
            
        # obtain unique keys for animals, schedule events
        keys_to_use = self.alive.difference(self.used_keys)
        for i in range(to_add):
            key = keys_to_use.pop()
            if(self.animal == 'rabbit'):
                ScheduleEatGrass(key, global_data)    
            elif(self.animal == 'wolf'):
                ScheduleHuntRabbit(key, global_data)
            else:
                raise Exception("Incorrect animal type")
            self.used_keys.add(key)
        
 
################################################################################
# Schedule Utilities
################################################################################

def ScheduleEatGrass (rabbit_id, global_data):

    ts = engine.CurrentTime() + NormalSample(R_Starvation)
    event_name = 'EAT_GRASS'
    event_data = {'rabbit_id' : rabbit_id} 
    if(ts <= SimulationLength):
        engine.Schedule(ts, event_name, global_data, event_data)

def ScheduleHuntRabbit (wolf_id, global_data):

    ts = engine.CurrentTime() + NormalSample(W_Starvation)
    event_name = 'HUNT_RABBIT'
    event_data = {'wolf_id' : wolf_id} 
    if(ts <= SimulationLength):
        engine.Schedule(ts, event_name, global_data, event_data)

def ScheduleRepopulation (event_name, global_data):

    ts = engine.CurrentTime() + R_Repopulation
    if(ts <= SimulationLength):
        engine.Schedule(ts, event_name, global_data, {})

def ScheduleGrowGrass (event_name, global_data):
    ts = engine.CurrentTime() + G[1] 
    if(ts <= SimulationLength):
        engine.Schedule(ts, event_name, global_data, {})

def ScheduleRecordState (event_name, global_data):
    ts = engine.CurrentTime() + RecordInterval 
    if(ts <= SimulationLength):
        engine.Schedule(ts, event_name, global_data, {})

################################################################################
# Event Utilities
################################################################################

def RepopulateRabbits (event):

    RabbitPopulation = event.global_data['RabbitPopulation']   
    RabbitPopulation.repopulate(event.global_data)
    ScheduleRepopulation('REPOPULATE_RABBITS', event.global_data)

def RepopulateWolves (event):

    WolfPopulation = event.global_data['WolfPopulation']   
    WolfPopulation.repopulate(event.global_data)
    ScheduleRepopulation('REPOPULATE_WOLVES', event.global_data)

def EatGrass (event):
    
    # setup ~
    rabbit_id = event.event_data['rabbit_id']
    WolfPopulation = event.global_data['WolfPopulation']   
    RabbitPopulation = event.global_data['RabbitPopulation']   
    
    # make sure this rabbit is still alive
    if(not rabbit_id in RabbitPopulation.used_keys):
        return

    # Eat grass and schedule next feeding
    if(event.global_data['N_Grass']):
        
        event.global_data['N_Grass'] -= 1
        ScheduleEatGrass(rabbit_id, event.global_data)     

    # The rabbit dies
    else:
   
        RabbitPopulation.kill(rabbit_id) 
       
    UpdateGlobals(event)

def HuntRabbit (event):
    
    # setup ~
    wolf_id = event.event_data['wolf_id']
    WolfPopulation = event.global_data['WolfPopulation']   
    RabbitPopulation = event.global_data['RabbitPopulation']   

    # Get a selection of rabbits to hunt
    selection = int(ceil(RabbitPopulation.n * RabbitsToHunt)) 

    # hunt each one
    success = False
    flipped_rate = ceil(1. / WolfCatchingRabbitRate)
    for i in range(selection):
        state = randint(1, flipped_rate)
        if(state == 1):
            success = True
            break 
     
    # the hunt was succesfull, wolf eats rabbit
    if(success):
    
        # kill rabbit
        rabbit_to_eat = sample(RabbitPopulation.used_keys, 1)[0]
        RabbitPopulation.kill(rabbit_to_eat) 

        # schedule next hunt
        ScheduleHuntRabbit (wolf_id, event.global_data)

    # the hunt was not successful, wolf starves to death
    else:
        WolfPopulation.kill(wolf_id)

    UpdateGlobals(event)

def GrowGrass (event):

    event.global_data['N_Grass'] += G[0] * FieldSize
    ScheduleGrowGrass('GROW_GRASS', event.global_data)
    UpdateGlobals(event)

def RecordState (event):
    
    sleep(0.05)
    global_data = event.global_data
    print('Time: ', event.timestamp, 'Rabbits: ', global_data['RabbitPopulation'].n, 'Wolves: ',
         global_data['WolfPopulation'].n, 'Grass: ', global_data['N_Grass'])
    global_data['Rabbits_Data'].append(global_data['RabbitPopulation'].n)
    global_data['Wolves_Data'].append(global_data['WolfPopulation'].n)
    ScheduleRecordState('RECORD_STATE', event.global_data)
    UpdateGlobals(event)

################################################################################
# Misc Utilities
################################################################################

# rerouting function to emulate the pointer callback method
def reroute (event):

    name = event.event_name
    #print(name, event.timestamp)
    if(name == 'EAT_GRASS'):
        EatGrass(event)
    elif(name == 'HUNT_RABBIT'):
        HuntRabbit(event)
    elif(name == 'GROW_GRASS'):
        GrowGrass(event)
    elif(name == 'REPOPULATE_RABBITS'):
        RepopulateRabbits(event)
    elif(name == 'REPOPULATE_WOLVES'):
        RepopulateWolves(event)
    elif(name == 'RECORD_STATE'):
        RecordState(event)

def UpdateGlobals(event):

    event.global_data['N_Events'] += 1

def NormalSample(mean):

    return normal(loc=mean)    

################################################################################
# Main Loop
################################################################################

if __name__ == "__main__":
    
#worst, medians, best = pop.solve(niters)

#x = [_ for _ in range(niters)]
#plt.plot(x, worst, 'r--', medians, 'bs', best, 'g^')
#plt.legend()
#plt.show()

    print ("Welcome to the Preditor/Prey Simulation!");
    
    # Initialize populations
    # Only using globals for read-only variables (e.g. model constants and params)
    # Anything else will be passed around as in a dict as global data
    WolfPopulation = Population(InitialWolfCount, WolfBreedingRate, 'wolf')
    RabbitPopulation = Population(InitialRabbitCount, RabbitBreedingRate, 'rabbit')
    global_data = {'RabbitPopulation' : RabbitPopulation,
                  'WolfPopulation' : WolfPopulation,
                  'N_Events'   : 0,
                  'N_Grass'   : G[1]*FieldSize,
                  'Rabbits_Data' : [InitialRabbitCount],
                  'Wolves_Data' : [InitialWolfCount]}

    # Prepare the field
    RabbitPopulation.schedule_all(global_data)
    WolfPopulation.schedule_all(global_data)
    ScheduleGrowGrass('GROW_GRASS', global_data)
    ScheduleRecordState('RECORD_STATE', global_data)

    StartTime = time()
    engine.RunSim()
    EndTime = time()

    x = [_ for _ in range(SimulationLength//RecordInterval+1)] 
    print(len(global_data['Rabbits_Data']))
    print(len(global_data['Wolves_Data']))
    plt.plot(x, [_/10 for _ in global_data['Rabbits_Data']], 'r--', global_data['Wolves_Data'], 'bs')
    plt.legend()
    plt.show()

    # print final statistics
    print("done! -- Events executed: ", global_data['N_Events'])



