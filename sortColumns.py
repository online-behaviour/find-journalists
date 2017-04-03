#!/usr/bin/python -W all
"""
    sortColumns: sort the columns of a csv file with binary data
    usage: sortColumns < file
    note: assumes that the file does not contain a heading and
                  that the first column contains a row id
    20170328 erikt(at)xs4all.nl
"""

import sys
import csv

# row data
rows = []
# counts of the number of ones per column
columnCounts = {}
# read csv data from stdin
csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
# for every line
for row in csvreader:
    # add the row to the list of rows
    rows.append(row)
    # process the binary data in the row
    for i in range(1,len(row)):
        # if the current element is 1
        if int(row[i]) == 1:
            # add one to the column count
            if i in columnCounts: columnCounts[i] += 1
            else: columnCounts[i] = 1
        # else set the column count to zero, if it is not yet set
        # this is necessary to keep the columnCounts complete
        elif not i in columnCounts: columnCounts[i] = 0
# set the count of the first column (row id) lower than the rest
columnCounts[0] = -1

# show the input file with columns sorted by the number of ones they contain
for row in rows:
    # process all columns ordered by the counts of ones
    for column in sorted(columnCounts,key=columnCounts.get):
        # if this is not the first column: print a separator character
        if column > 0: sys.stdout.write(",")
        # print the column data
        sys.stdout.write(row[column])
    # print a newline character
    sys.stdout.write("\n")

# done
sys.exit()
