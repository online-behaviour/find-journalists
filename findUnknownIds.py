#!/usr/bin/python3 -W all
"""
    findUnknownIds.py: find ids of tweets that are not in the collection
    usage: gunzip -c file.gz | ./findUnknownIds.py
    20180403 erikt(at)xs4all.nl
"""

import json
import re
import sys

IDFIELDNAME = "id"
REPLYFIELDNAME = "in_reply_to_status_id"
MINLENGTH = 15
knownIds = {}
unknownIds = {}

def addKnownId(thisId):
    global knownIds
    global unknownIds
    global MINLENGTH
    knownIds[thisId] = True
    if thisId in unknownIds: del(unknownIds[thisId])
    if len(thisId) < MINLENGTH: MINLENGTH = len(thisId)

def addUnknownId(thisId):
    global knownIds
    global unknownIds
    if not thisId in knownIds and \
       len(thisId) >= MINLENGTH and \
       re.match(r"^[0-9]+$",thisId): unknownIds[thisId] = True

def check(thisDict):
    for field in [IDFIELDNAME,REPLYFIELDNAME]:
        if field in thisDict: addUnknownId(str(thisDict[field]))
    for field in thisDict:
        if type(thisDict[field]) == type({'a':1}): check(thisDict[field])

for line in sys.stdin:
    try: 
        jsonLine = json.loads(line)
        if IDFIELDNAME in jsonLine: addKnownId(str(jsonLine[IDFIELDNAME]))
        check(jsonLine)
    except: pass
for key in knownIds: print(key+" K")
for key in unknownIds: print(key+" U")
