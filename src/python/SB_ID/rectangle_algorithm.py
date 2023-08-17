import numpy as np
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt

#Title: rectangle_algorithm.py
#Author: Harper Chisari

#Contents:
#   CLASS - Rec_Algo:
#       METHOD - find_corners: takes in the graph and identifies all corners as convex or concave

#Version History:
#   Harper: 8/13/23 - V1.0 init

#Use network x? maybe useful methods?
class Rec_Algo:
    def __init__(self, grid: list) -> None:
        # Convert to numpy array for easier manipulation
        self.grid = np.array(grid, dtype=bool)
        self.find_corners()
        self.horizontal_diagonals, self.vertical_diagonals = self.find_good_diagonals()
        #self.find_maximum_independent_set()

    def print_grid(self, grid):
        for row in grid:
            for cell in row:
                if cell:
                    print("\033[94m1\033[0m", end=" ")  # Bright light blue for True
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False
            print()  # New line for each row

    def print_grid_with_diagonals(self, horizontal_diagonals, vertical_diagonals):
        # Create a new grid to represent the diagonal lines
        diagonal_grid = np.full_like(self.grid, ' ', dtype=str)

        # Mark vertical diagonals with red '|'
        for ((x1, y1), (x2, y2)) in vertical_diagonals:
            diagonal_grid[x1, y1] = "\033[91m|\033[0m"

        # Print the grid with diagonals
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid[i, j]:
                    print("\033[94m1\033[0m", end=" ")  # Bright light blue for True
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False
                if j < self.grid.shape[1] - 1:
                    print(diagonal_grid[i, j], end="")
            print()

    def print_vertical_diagonals(self):
        print(f"Vertical Diagonals: \n{self.vertical_diagonals}\n")
        # Iterate through the rows of the grid
        for i in range(self.grid.shape[0]):
            # Iterate through the columns of the grid
            for j in range(self.grid.shape[1]):
                # Print the cell value
                if self.grid[i, j]:
                    print("\033[94m1\033[0m", end=" ")  # Bright light blue for True
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False

                # Check if there is a vertical diagonal at this location
                for ((x1, y1), (x2, y2)) in self.vertical_diagonals:
                    if y1 == y2 and j == y1 and i > x1 and i <= x2:
                        print("\033[91m|\033[0m", end="")  # Red vertical line

            print()  # New line for each row
        print()

    def print_horizontal_diagonals(self):
        print(f"Horizontal Diagonals: \n{self.horizontal_diagonals}\n")
        # Iterate through the rows of the grid
        for i in range(self.grid.shape[0]):
            # Check if there is a horizontal diagonal at this row
            for ((x1, y1), (x2, y2)) in self.horizontal_diagonals:
                if x1 == x2 and i == x1 + 1:
                    # Print spaces to align with the second column of the 2x2 subgrid
                    print(" " * (y1 * 2 + 1), end=" ")  # Added one more space

                    # Print the horizontal line
                    for j in range(y1, y2):
                        print("\033[91m-\033[0m", end=" ")  # Red horizontal line
                    print()  # New line after the horizontal line

            # Iterate through the columns of the grid and print the cell values
            for j in range(self.grid.shape[1]):
                if self.grid[i, j]:
                    print("\033[94m1\033[0m", end=" ")  # Bright light blue for True
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False

            print()  # New line for each row
        print()

    def print_grid_with_subgrid(self, i, j):
        for row in range(self.grid.shape[0]):
            for col in range(self.grid.shape[1]):
                # Print red outline for the left column of the subgrid
                if col == j and row >= i and row < i + 2:
                    print("\033[91m|\033[0m", end="")

                # Print the cell value
                if self.grid[row, col]:
                    print("\033[94m1\033[0m", end=" ")  # Bright light blue for True
                else:
                    print("\033[90m0\033[0m", end=" ")  # Medium grey for False

                # Print red outline for the right column of the subgrid
                if col == j + 1 and row >= i and row < i + 2:
                    print("\033[91m|\033[0m", end="")

            print()  # New line for each row

        # Print red outline for the bottom row of the subgrid
        print()

    def find_corners(self):
        self.convex_corners = []
        self.concave_corners = []
        self.double_concave_corners = []

        # Iterate through the grid and check every 2x2 block
        for i in range(self.grid.shape[0] - 1):
            for j in range(self.grid.shape[1] - 1):
                A, B, C, D = self.grid[i, j], self.grid[i, j + 1], self.grid[i + 1, j], self.grid[i + 1, j + 1]

                # Check the conditions for convex
                if ((C ^ D) & (~A & ~B)) | ((A ^ B) & (~C & ~D)):
                    self.convex_corners.append((i, j))
                    #self.print_grid_with_subgrid(i,j)

                # Check the conditions for concave
                if ((C ^ D) & (A & B)) | ((A ^ B) & (C & D)):
                    self.concave_corners.append((i, j))

                # Check the conditions for double concave
                if (A & ~C & ~B & D) | (~A & C & B & ~D):
                    self.concave_corners.append((i, j))
                    self.double_concave_corners.append((i,j))

        return self.convex_corners, self.concave_corners, self.double_concave_corners
    
    def find_good_diagonals(self):
        horizontal_diagonals = []
        vertical_diagonals = []

        # Iterate through concave corners to find potential connections
        for i, (x1, y1) in enumerate(self.concave_corners):
            for x2, y2 in self.concave_corners[i + 1:]:
                # Check for horizontal alignment (same row, no zeros in between)
                if x1 == x2 and all(self.grid[x1, y] for y in range(min(y1, y2) + 1, max(y1, y2))):
                    horizontal_diagonals.append(((x1, y1), (x2, y2)))

                # Check for vertical alignment (same column, no zeros in between)
                elif y1 == y2 and all(self.grid[x, y1] for x in range(min(x1, x2) + 1, max(x1, x2))):
                    vertical_diagonals.append(((x1, y1), (x2, y2)))

        return horizontal_diagonals, vertical_diagonals
    
    def find_maximum_independent_set(self):
        # Create a bipartite graph
        B = nx.Graph()

        # Add nodes for horizontal and vertical diagonals
        horizontal_nodes = [f'h{i}' for i in range(len(self.horizontal_diagonals))]
        vertical_nodes = [f'v{i}' for i in range(len(self.vertical_diagonals))]
        for node in horizontal_nodes:
            B.add_node(node, bipartite=0)
        for node in vertical_nodes:
            B.add_node(node, bipartite=1)

        # Add edges for intersecting diagonals
        for i, ((hx1, hy1), (hx2, hy2)) in enumerate(self.horizontal_diagonals):
            for j, ((vx1, vy1), (vx2, vy2)) in enumerate(self.vertical_diagonals):
                if hx1 <= vx1 <= hx2 and vy1 <= hy1 <= vy2:
                    B.add_edge(f'h{i}', f'v{j}')

        # Draw the bipartite graph
        pos = nx.bipartite_layout(B, horizontal_nodes)
        nx.draw(B, pos, with_labels=True)
        plt.title('Bipartite Graph')
        print('Plotting Bipartite Graph')
        plt.show()

        # Find maximum matching
        matching = bipartite.maximum_matching(B, top_nodes=[f'h{i}' for i in range(len(self.horizontal_diagonals))])

        # Find maximum independent set
        independent_set = set(B.nodes) - set(matching.keys())

        # Draw the maximum independent set
        nx.draw(B, pos, nodelist=independent_set, with_labels=True, node_color='r')
        print('Plotting Maximum Independent Set')
        plt.title('Maximum Independent Set')
        plt.show()

        # Translate to diagonals
        self.independent_diagonals = [self.horizontal_diagonals[i] if f'h{i}' in independent_set else self.vertical_diagonals[i] for i in range(len(self.horizontal_diagonals))]
        print(f"Maximum Independent Set of Good Diagonals: {self.independent_diagonals}")

        return self.independent_diagonals
    
grid_wide = [
        [0, 1, 0, 0, 1, 1],
        [1, 1, 1, 0, 1, 1],
        [0, 1, 0, 0, 1, 1]
    ]

grid = [
    [0, 1],
    [1, 1],
    [1, 0],
]
#algo = Rec_Algo(grid)
#algo.print_vertical_diagonals()


grid = [
    [0, 0, 1, 1],
    [0, 1, 1, 0]
]
#algo = Rec_Algo(grid)
#algo.print_horizontal_diagonals()


grid = [
    [0, 0,0, 1,1,1, 1],
    [0, 0,1, 1,1,1, 0]
]
#algo = Rec_Algo(grid)
#algo.print_horizontal_diagonals()

grid = [
    [0, 0, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
]
algo = Rec_Algo(grid)
algo.print_vertical_diagonals()
algo.print_horizontal_diagonals()

grid = [
    [0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]