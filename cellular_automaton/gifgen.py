import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib import colors
import matplotlib.pyplot as plt

#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)


class GifCreator:
    def __init__(self, universe, save=False, filename='', rule=''):
        """
        :param universe:is a list of grids (numpy arrays originally)
        :param save: False or True to save
        :param filename:
        """
            
        self.universe = [self.get_new_grid(grid) for grid in universe]
        self.save = save
        self.filename = filename
        self.rule = rule

    def create_fig(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        temp_frame = self._create_first_frame()

        def update(i):
            temp_frame.set_data(self.universe[i])

        anim = FuncAnimation(
            fig, update, interval=100, frames=len(self.universe), repeat=False)
        if self.save:
            anim.save(self.filename + '.html', fps=10, writer='imagemagick')
        plt.draw()
        plt.show()

    def get_new_grid(self, grid):
        # make the new grids so they are NxMx3(RGB)
        colors = [(0,0,0), (51, 255, 51), (192, 192, 192), (255, 153, 51), (255, 0, 0)]
        new_grid = []
        for i, row in enumerate(grid):
            new_grid.append([])
            for j, col in enumerate(row):
                num = 0
                for ind, val in enumerate(col):
                    if(val != 0):
                        num = ind+1
                new_grid[i].append(colors[num])
        return new_grid
                    
 
    def _create_first_frame(self):
        temp_frame = plt.imshow(self.universe[0])
        return temp_frame


