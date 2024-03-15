"""
cse6242 s23
Q5.py - utilities to supply data to the templates.

This file contains a pair of functions for retrieving and manipulating data
that will be supplied to the template for generating the table. """
import csv

def username():
    return 'yyang3041'

def data_wrangling():
    with open('data/movies.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        table = list()
        # Feel free to add any additional variables
        idx = 0

        # Read in the header
        for header in reader:
            break
        
        # Read in each row
        for row in reader:
            row[2] = str(row[2])
            table.append(row)
            idx += 1
            # Only read first 100 data rows - [2 points] Q5.a
            if idx == 100:
                break
        
        # Order table by the last column - [3 points] Q5.b
        table = sorted(table, key=lambda x:float(x[2]), reverse=True)
    
    return header, table

