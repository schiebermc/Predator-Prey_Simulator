# By Matthew Schieber
# Simulation Engine
# All machinery is general, it merely carries out the event-driven simulation

from heapq import heappop
from heapq import heappush
from time import time
from collections import namedtuple
import field

# use heapq if true else use naive list (slow) 
heapq = False

# Future event list (priority queue)
FEL = []

# Event structure
Event = namedtuple('Event', 'timestamp event_name global_data event_data')

# Simulation clock variable
Now = 0.0

# Return current simulation time
def CurrentTime ():
    return (Now)

# Schedule new event in FEL
def Schedule (ts, name, global_data, event_data):
    if(heapq):
         heappush(FEL, Event(ts, name, global_data, event_data))
    else:
        for ind, i in enumerate(FEL):
            if(i.timestamp > ts):
                FEL.insert(ind, Event(ts, name, global_data, event_data))
                return 
        FEL.append(Event(ts, name, global_data, event_data))

# Remove smallest timestamped event from FEL, return pointer to this event
def Remove ():
    if(heapq):
        return heappop(FEL)
    else:
        return FEL.pop(0)

def RunSim (): 
    global Now
    
    # Main scheduler loop
    while (len(FEL)): 
        
        e = Remove()
        Now = e.timestamp
        field.reroute(e)


