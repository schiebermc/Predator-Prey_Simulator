# By Matthew Schieber
# Simulation Engine

from heapq import heappop
from heapq import heappush
from time import time
from collections import namedtuple
import field

# Use an event structure as the header for the future event list (priority queue)
Event = namedtuple('Event', 'timestamp event_name global_data event_data')
FEL = []

# Simulation clock variable
Now = 0.0

# Return current simulation time
def CurrentTime ():
    return (Now)

# Schedule new event in FEL
def Schedule (ts, name, global_data, event_data):
    heappush(FEL, Event(ts, name, global_data, event_data))

# Remove smallest timestamped event from FEL, return pointer to this event
def Remove ():
    return heappop(FEL)

def RunSim (): 
    global Now
    
    # Main scheduler loop
    while (len(FEL)): 
        
        e = Remove()
        Now = e.timestamp
        field.reroute(e)


