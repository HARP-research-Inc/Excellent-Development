from structures.sheet import Sheet as sht

'''csv_data = """column_1_name,column_2_name,column_3_name
12,crack,23
13,meth,45"""
sheet = sht(name="test")
sheet.transform(csv_data = csv_data)'''

csv_data = """                            ,"Date"        ,"Time" ,"Address",
"George Costanza"    ,"10/12/2023"   ,              ,"1600 Burdette Ave, Troy NY",
                            ,"09/01/2002"   ,              ,"35 Wagon Wheel Trail, CLinton NJ",
"Harper Giorgo"      ,"11/22/1963"   ,              ,"10 Pennsylvania Ave, Washington DC","""
sheet = sht(name="test2")
sheet.transform(csv_data = csv_data)
