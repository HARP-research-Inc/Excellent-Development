from gen_tree import gen_tree

#first add to_dataframe method to table in gen_tree, builds a df of a table by going through all the label blocks looking for names.
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
        #self.sheets = {}
        #for Sheet in given tree: 
            #tables = {}
            # get the dfs of every table and expected_position of the data_block within
            #tables[expected_position] = df
            #self.sheets[Sheet.name] = tables
        pass

    def to_json(self):
        self.json_data = {}
        for Sheet, Tables in self.sheets.items():
            self.json_data[Sheet] = []
            for table_df in Tables.values():
                self.json_data[Sheet].append(table_df.to_json())
        return self.json_data


    def populate(self, csv_data=None, notebook=None, name=None):
        #pop_sheets = {}  #sheet_name: Tables({coord: table_df})
            
        #if csv_data:
            #if name and name in self.sheets.keys():
                #pop_sheets[name] = {'csv'=csv_data}
            #else:
                #pop_sheets[self.sheets.keys()[0]] = {'csv'=csv_data}
        #elif notebook: #{sheet_name: csv_data}
            #for name, csv_data in notebook:
                #pop_sheets[self.sheets[name]] = {'csv'=csv_data}

                #csv_data to list of lists
                #for coord within Sheet.keys():
                    #populate df with data from csv starting at coord in top left
