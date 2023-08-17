 #? Title: relative_location_processor.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - RLP:
#       #!LAST TESTED: N/A
#       METHOD - __init__: Initializes a Relative Location Processor object with expected position, expected size, t, l, r, b, and sheet size
#       METHOD - generate_offsets: Generates the offsets dictionary, with coordinates based off of the t l r and b tuples, with the first number being the start, and the second number being the end of the offset in a given direction.

#? Version History:
#   Harper: 8/17/23 - V1.0: seperated from gen_tree_helper.py, moved border_id method to sheet_transformer.py to avoid circular import. Fixed accidental offset.


# Relative Location Processor
class RLP:
    def __init__(self, expected_position=(1, 1), expected_size=(2, 2),
                 t=(1, 2), l=(1, 2), r=(1, 2), b=(1, 2), sheet_size=(100, 100),
                 structure=None):

        if structure:
            self.expected_position = structure.expected_position
            self.expected_size = structure.expected_size
        else:
            self.expected_position = expected_position
            self.expected_size = expected_size
        self.t = t if t else (1, 2)
        self.l = l if l else (1, 2)
        self.r = r if r else (1, 2)
        self.b = b if b else (1, 2)
        self.sheet_size = sheet_size

        self.border_eps = {
            'same_height':
                {'l': [],
                 'r': []},
            'same_width':
                {'t': [],
                 'b': []}}

        self.generate_offsets()

    # Function to generate the offsets dictionary, with coordinates based off of the t l r and b tuples, with the first number being the start, and the second number being the end of the offset in a given direction.
    def generate_offsets(self) -> None:
        #  If the second of the tuple is -1, then the offset is infinite in
        #   that direction.
        #  If the first of the tuple is -1, then the offset is 0 in
        #   that direction.
        #  If t or l, this means that the maximum offset is the ep, and to create a list up to 1 in a given direction
        #  If b or r, this means that the maximum offset is the end of the sheet, and to create a list up to the given sheet size, which is an otherwise optional parameter.

        # top border eps
        if self.t[0] != -1:
            for i in range(self.t[1] - self.t[0] + 1):
                self.border_eps['same_width']['t'].append(
                    (self.expected_position[0],
                     self.expected_position[1] - i - 1))
        elif self.t[1] != -1:
            for i in range(self.expected_position[1]):
                self.border_eps['same_width']['t'].append(
                    (self.expected_position[0],
                     self.expected_position[1] - i))

        # left border_eps
        if self.l[0] != -1:
            for i in range(self.l[1] - self.l[0] + 1):
                self.border_eps['same_height']['l'].append(
                    (self.expected_position[0] - i - 1,
                     self.expected_position[1]))
        elif self.l[1] != -1:
            for i in range(self.expected_position[1]):
                self.border_eps['same_height']['l'].append(
                    (self.expected_position[0] - i,
                     self.expected_position[1]))

        # bottom border_eps
        if self.b[0] != -1:
            for i in range(self.b[1] - self.b[0] + 1):
                self.border_eps['same_width']['b'].append(
                    (self.expected_position[0] + self.expected_size[0],
                     self.expected_position[1] + self.expected_size[1] + i - 1))
        elif self.b[1] != -1:
            for i in range(self.expected_position[1]):
                self.border_eps['same_width']['b'].append(
                    (self.expected_position[0] + self.expected_size[0],
                     self.expected_position[1] + self.expected_size[1] + i - 1))

        # right border_eps
        if self.l[0] != -1:
            for i in range(self.r[1] - self.r[0] + 1):
                self.border_eps['same_height']['r'].append(
                    (self.expected_position[0] + self.expected_size[0] + i - 1,
                     self.expected_position[1] + self.expected_size[1]))
        elif self.r[1] != -1:
            for i in range(self.expected_position[1]):
                self.border_eps['same_height']['r'].append(
                    (self.expected_position[0] + self.expected_size[0] + i - 1,
                     self.expected_position[1] + self.expected_size[1]))
