 #? Title: max_area_rectangles.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - MaxAreaRectangles:
#       #!LAST TESTED: 8/15/23
#       METHOD - __init__: initializes grid: a 2D array of booleans, print: a boolean to print the grid with subgrids
#       METHOD - find_largest_rectangles: Finds the largest rectangles in the grid
#       METHOD - _recursive_find: Recursively finds the largest rectangles in the grid
#       METHOD - print_grid_with_subgrid: Prints the grid with a subgrid

#? Version History:
#   Harper: 8/17/23 - V1.0 seperated from utilities.py, now gen_tree_helper.py


import numpy as np
import largestinteriorrectangle as largest_interior_rectangle


# Class to find the largest rectangles in a grid
class MaxAreaRectangles:
    def __init__(self, grid, print: bool):
        self.grid = np.array(grid, dtype=bool)  # Convert to boolean array
        self.rectangles = []
        self.print = print

    # Function to find the largest rectangles in the grid
    def find_largest_rectangles(self):
        # Make a copy of the grid to modify during recursion
        grid_copy = self.grid.copy()
        self._recursive_find(grid_copy)

        # Print the found rectangles
        if self.print:
            for rectangle in self.rectangles:
                x, y, width, height = rectangle
                print(
                    f"Rectangle found at ({x}, {y}) with width {width} and height {height}")
                self.print_grid_with_subgrid(
                    y, x, y + height - 1, x + width - 1)

        return self.rectangles

    # Function to recursively find the largest rectangles in the grid
    def _recursive_find(self, grid):
        # Check if the entire grid is covered
        if np.all(grid == False):
            return

        # Find the largest interior rectangle in the current grid
        lir = largest_interior_rectangle.lir(grid)
        if lir is None:
            return

        # Add the found rectangle to the list
        x, y, width, height = lir
        self.rectangles.append((x, y, width, height))

        # Mark the found rectangle area as covered in the grid
        grid[y:y+height, x:x+width] = False

        # Recursively find the largest rectangle in the remaining uncovered parts
        self._recursive_find(grid)

    # Function to print the grid with a subgrid
    def print_grid_with_subgrid(self, i1, j1, i2, j2):
        for row in range(self.grid.shape[0]):
            for col in range(self.grid.shape[1]):
                # Print red outline for the left column of the subgrid
                if col == j1 and row >= i1 and row <= i2:
                    print("\033[91m|\033[0m", end="")

                # Print the cell value
                if self.grid[row, col]:
                    # Bright light blue for True
                    print("\033[94m1\033[0m", end=" ")
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False

                # Print red outline for the right column of the subgrid
                if col == j2 and row >= i1 and row <= i2:
                    print("\033[91m|\033[0m", end="")

            print()  # New line for each row

            # Print red outline for the bottom row of the subgrid
            if row == i2 or row == (i1-1):
                print(" " * (j1 * 2), end=" ")  # Added one more space
                print("\033[91m-\033[0m " * (j2 - j1+1))
