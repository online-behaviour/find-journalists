#!/usr/bin/python -W all
# occupationStats.py: compute occupation statistics based on makevec.err
# usage: occupationStats < makevec.err
# note: expected input line format: 61,212,61,fritswester,YES,journalist
# 20170330 erikt(at)xs4all.nl

import sys
import csv

# expected number of columns in complete line
NBROFCOLUMNS = 6
# main column with relvant count for a row
MAINCOLUMN = 0
# target occupation
TARGET = "journalist"
# other occupation
OTHER = "other"
# number of values to use with smoothing
MAXSMOOTH = 15

# counts
counts = {}
# open csv file at stdin
csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
# read each line of the csv file, store it in list row
for row in csvreader: 
    # only process complete lines: with 6 columns
    if len(row) == NBROFCOLUMNS:
        occupation = row[NBROFCOLUMNS-1]
        count = int(row[MAINCOLUMN])
        # check if this is a new count value
        if not count in counts:
            # initialize counts dictionary for this new value
            counts[count] = {}
            counts[count][TARGET] = 0
            counts[count][OTHER] = 0
        # increase the counter depeding on the occupation value
        if occupation == TARGET: 
            counts[count][TARGET] += 1
        else:
            counts[count][OTHER] += 1

# print all counts
smoothHistory = []
for count in sorted(counts):
     value = 100*counts[count][TARGET]/(counts[count][TARGET]+counts[count][OTHER])
     smoothHistory.append(value)
     while len(smoothHistory) > MAXSMOOTH: smoothHistory.pop(0)
     smooth = 0
     for s in smoothHistory: smooth += s
     smooth /= len(smoothHistory)
     print "%s %0.1f %0.1f" % (count,value,smooth)

# done
sys.exit()
