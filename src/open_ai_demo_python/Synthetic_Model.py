from gen_tree import gen_tree

#first add to_dataframe method, builds a df of a table by going through all the label blocks looking for names.
#go through t0, t1, l0 and l1 labels:
    #if yes there is a label block for position:
        # make left of df have values of cells l0 or l1 (prioritizing l0)
        # make top of df have values of cells t0 or t1 (prioritizing t0)
#return df with populated data from data block, and names from above
#started code:
#{'same_width':[],'same_height': []}
#for dim in (('same_width',"t0"), ('same_width',"t1"), ('same_height',"l0"), ('same_height',"l1")):
    #if self.label_blocks[dim[0]][dim[1]] has a block and :
        #if dim[0] == 'same_width'

class synthetic_model:
    def __init__(self, gen_tree):
        #for given tree, output 
        pass