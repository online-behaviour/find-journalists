#!/usr/bin/python -W all
"""
    tweets2hours: store tweets from stdin to hourly files
    usage: tweets2hours < file
    20170404 erikt(at)xs4all.nl
"""

import time
import json
import re
import sys

# constants
COMMAND = sys.argv
# hours to subtract/add to get real time from GMT in tweets
DELTAHOURS = 2
# list with open file handles
files = {}

# read a tweet
for line in sys.stdin:
    # remove final newline character
    line = line.rstrip()
    # convert line to json
    try: 
        jsonLine = json.loads(line)
    except:
        sys.exit(COMMAND+": unknown format of input line: "+line+"\n")
    if not "created_at" in jsonLine:
        sys.stderr.write(COMMAND+": skipping line (no date found): "+line+"\n")
        continue
    # parse the date string
    date = time.strptime(jsonLine["created_at"].encode("utf-8"),"%a %b %d %H:%M:%S +0000 %Y")
    # make the file name
    # get real local time from GMT in tweets
    month = date[1]
    day = date[2]
    hour = date[3]+DELTAHOURS
    while hour >= 24:
        hour -= 24
        day += 1 # this may result in an invalid date
    while hour < 0:
        hour += 24
        day -= 1 # this may result in an invalid date
    if month > 0 and month < 10: month = "0"+str(month)
    else: month = str(month)
    if day > 0 and day < 10: day = "0"+str(day)
    else: day = str(day)
    if hour < 10: hour = "0"+str(hour)
    else: hour = str(hour)
    thisFile = str(date[0])+month+day+"-"+hour+".out"
    # open file
    if not thisFile in files:
        outFile = open(thisFile,"w")
        files[thisFile] = outFile
    # write the tweet to the file
    files[thisFile].write(line+"\n")

# done: close all file handles
for fileName in files: files[fileName].close()
