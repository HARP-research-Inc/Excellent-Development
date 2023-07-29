import sys

class Gen_Tree_Helper:
    def debug_print(*args, **kwargs):
        if 'pytest' in sys.modules:
            print(*args, **kwargs)

    def tuple_string_to_tuple(tuple_string: str) -> tuple[int, int]:
        assert isinstance(tuple_string, str), f"not a tuple string: {tuple_string}"
        return tuple(map(int, tuple_string.replace("(", "").replace(")", "").split(', ')))

    def build_csv(cells, origin=(1, 1)):
        # Check if the origin is valid
        if any(cell.coord[i] < origin[i] for i in range(2) for cell in cells):
            raise ValueError("Origin is out of cells' range")
        if len(cells) < 1:
            raise ValueError("No Cells!")

        max_rows = max(cell.coord[1] for cell in cells)
        max_cols = max(cell.coord[0] for cell in cells)

        # Initialize an empty grid starting at the origin
        grid = [["' '" for _ in range(origin[1]-1, max_cols)]
                for _ in range(origin[0]-1, max_rows)]

        for cell in cells:
            row = cell.coord[1] - origin[1]
            col = cell.coord[0] - origin[0]
            grid[row][col] = str(cell)

        string_rows = []
        for row in grid:
            string_rows.append(', '.join(row))

        return '\n'.join(string_rows)