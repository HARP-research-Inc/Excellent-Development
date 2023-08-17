from structures.sheet import Sheet as sht

csv_data = """column_1_name,column_2_name,column_3_name
12,crack,23
13,meth,45"""
sheet = sht(name="test")
sheet.transform(csv_data = csv_data)
