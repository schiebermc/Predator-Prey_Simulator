# Predator-Prey_Simulator
Simulation engine and application for predator-prey systems with limited resources.

The generalized simulation engine is contained within `engine.py`.  There, you will find general event structures, the `RunSim` function, and FEL structures.  For the FEL, I implemented a naive version using python lists, however, the `heapq` module is much faster and since my simulation processes more than 100,000 events on average, I added an additional workflow which turns the `heapq` machinery on and off with a boolean.

The application code is found in `field.py`, which contains all class structures and event handlers.  At the top of `field.py`, one will find all the model constants and parameters.  To use the simulation, simply edit these variables to you liking, and run `python field.py` at the command line.  I use `matplotlib` in order to plot population behaviors over time. 

The project proposal and description of the conceptual model is found in `ProjectProposalandConceptualModel.pdf`.

Some results are included in `Results.pdf`.
