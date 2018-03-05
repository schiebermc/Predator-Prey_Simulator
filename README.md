# Predator-Prey_Simulator
Simulation engine and application for predator-prey systems with limited resources.

The generalized simulation engine is contained within `engine.py`.  There, you will find general event structures, the `RunSim` function, and FEL structures.  For the FEL, I implemented a naive version using python lists, however, the `heapq` module is much faster and since my simulation processes more than 100,000 events on average, I added an additional workflow which turns the `heapq` machinery on and off with a boolean.

The application code is found in `field.py`, which contains all class structures and event handlers.  At the top of `field.py`, one will find all the model constants and parameters.  To use the simulation, simply edit these variables to your liking, and run `python field.py` at the command line.  You should expect prints to the console at every five time increments which reveal the current population behaviors.  Over time, the population behaviors are logged and can be plotted at the end of the simulation.  I use `matplotlib` in order to plot the final population behaviors.  If you do not have access to the matplotlib module, you can simply turn the `matplot` toggle off at the very top of `field.py`. 

The project proposal and description of the conceptual model is found in `ProjectProposalandConceptualModel.pdf`.

A final report including implementation discussions, verification, validation, and sample results are included in `FinalReport.pdf`.

