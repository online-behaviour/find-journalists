#!/usr/bin/python3 -Wall
"""
    removeDuplicates.py: remove duplicate ids from the output of findUnknownIds.py
    usage: for f in *; do findDuplicateIds.py < f; done | sort -n | ./removeDuplicates.py
    20180403 erikt(at)xs4all.nl
"""

import sys

COMMAND = sys.argv[0]
KNOWNTAG = "K"
UNKNOWNTAG = "U"

lastId = ""
lastUnknownId = ""
for line in sys.stdin:
    thisId,thisTag = line.split()
    if thisId == lastUnknownId and thisTag != UNKNOWNTAG:
        sys.exit(COMMAND+": input error: illegal line order: "+thisId)
    if thisTag == UNKNOWNTAG and thisId != lastId: print(thisId)
    lastId = thisId
    if thisTag == UNKNOWNTAG: lastUnknownId = thisId

