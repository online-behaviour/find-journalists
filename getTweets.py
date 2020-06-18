#!/usr/bin/python3
"""
getTweets.py: get recent tweets from Twitter within certain time frame
usage: ./getTweets -n MINIMUMID -x MAXIMUMID > file
20170309 erikt(at)xs4all.nl
"""

import getopt
import json
import operator
import re
import sys
import time
# import twitter library: https://github.com/sixohsix/twitter
from twitter import *
# put your authentication keys for Twitter in the local file definitions.py
# like: token = "..."
import definitions

# constants
COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -n MINIMUMID -x MAXIMUMID > file"
NL = "nl"
LANG = "lang"
SINCEID = "since_id"
MAXID = "max_id"
# stop the program after this many warnings
MAXWARNINGS =  50
# maximum count for remaining Twitter requests
MAXREMAINING = 180
# group of Twitter REST api used
APIGROUP = "search"
# Twitter REST api used
API = "/"+APIGROUP+"/tweets"
# maximum length of query in characters
MAXQUERY = 360
# if the query is too long, Twitter will fail with error missing url parameter
# file with query words
TRACKFILE = "/home/cloud/etc/track.20200612.unsorted"
# maximum number of tweets to fetch with one query
MAXTWEETCOUNT = 100

def readTrack():
    inFile = open(TRACKFILE,"r")
    line = re.sub(r"track *= *","",inFile.read().strip())
    twiqsTrack = line.split(",")
    inFile.close()
    return(twiqsTrack)

def checkRemaining(t,apigroup,api):
    # check the rate limit; if 0 then wait
    rates = t.application.rate_limit_status(resources = apigroup)
    remaining = rates['resources'][apigroup][api]['remaining']
    # check if there are remaining calls
    while remaining < 1:
        # if not: wait one minute
        time.sleep(60)
        # fetch the value of the remaining count from Twitter
        rates = t.application.rate_limit_status(resources = apigroup)
        remaining = rates['resources'][apigroup][api]['remaining']
    return(remaining)

def main(argv):
    # maximum id of tweet, start of backwards search; empty value: -1
    maxId = -1 # 20151216
    # minimum id of tweet; empty value: -1
    minId = -1
    # Twitter autnetication keys
    token = definitions.token
    token_secret = definitions.token_secret
    consumer_key =  definitions.consumer_key
    consumer_secret = definitions.consumer_secret
    # warning count
    nbrOfWarnings = 0
    # process command line options
    try: options = getopt.getopt(argv,"n:x:",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if option[0] == "-n": 
            try: minId = int(option[1])
            except: sys.exit(COMMAND+": "+option[1]+" is not a number")
        elif option[0] == "-x": 
            try: maxId = int(option[1])
            except: sys.exit(COMMAND+": "+option[1]+" is not a number")
        else: sys.exit(USAGE)
    if minId > maxId: sys.exit(COMMAND+": requested minimum id is larger than maximum id")

    # authenticate
    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
    # start with this element of the query list
    i = 0
    # remmeber which tweets have been collected
    seen = {}
    # twiqsTrack: list of twiqs track queries
    twiqsTrack = readTrack()
    # repeat while there are unprocessed query words
    while i+1 < len(twiqsTrack):
        # create the query: add first word
        query = "{0}:{1}".format(LANG,NL)
        if minId >= 0: query += " {0}:{1}".format(SINCEID,str(minId))
        if maxId >= 0: query += " {0}:{1}".format(MAXID,str(maxId))
        query += " "+twiqsTrack[i]
        # keep initial value of i for log messages
        startI = i
        # increment index pointer
        i += 1
        # add more words to the query, when available and 
        #     when query is not too long; 8 is length of %20OR%20
        while i+1 < len(twiqsTrack) and len(query)+8+len(twiqsTrack[i]) < MAXQUERY:
            query += "%20OR%20"+twiqsTrack[i]
            i += 1
        # check if we can access the api at Twitter, wait if necessary
        remaining = checkRemaining(t,APIGROUP,API)
        # start with dummy element in results list
        results = { "statuses" : [ "dummy "] }
        # run counter initialization
        runCounter = 0
        # repeat while tweets found
        while "statuses" in results and len(results["statuses"]) > 0:
            # empty results list
            results = []
            # increase run counter
            runCounter += 1
            # get tweets from Twitter
            #try:
            if True:
                # query arguments: https://dev.twitter.com/rest/reference/get/search/tweets
                #results = t.search.tweets(q = "de OR het OR een"+" lang:"+NL+" since:2020-06-08 until:2020-06-09", count = MAXTWEETCOUNT)
                results = t.search.tweets(q = query, count = MAXTWEETCOUNT)
            #except TwitterHTTPError as e:
            #    # if there is an error: report this
            #    sys.stderr.write("error: "+str(e))
            #    nbrOfWarnings += 1
            # stop if there were too many errors
            if nbrOfWarnings >= MAXWARNINGS:
                sys.exit(COMMAND+": too many warnings: "+nbrOfWarnings+"\n")
            # check if we have some results
            if not "statuses" in results:
                sys.exit(COMMAND+": incomplete results: aborting!\n")
            # process results
            if len(results["statuses"]) > 0:
                # extract new value of max id from the results
                maxId = -1
                # time stamp associated with the new max id
                maxTime = ""
                # process the tweets in the results
                for tweet in results["statuses"]:
                    # get the id of this tweet
                    thisId = tweet["id"]
                    # get the time stamp of this tweet
                    time = tweet["created_at"]
                    if maxId < 0 or thisId < maxId:
                        maxId = thisId
                        maxTime = time
                    # only print each tweet once
                    if not thisId in seen:
                        # print the tweet in json format
                        print(json.dumps(tweet,sort_keys=True))
                        # add tweet id to seen dictionary
                        seen[thisId] = True
                # decrease maxId to avoid fetching the same tweet
                maxId -= 1
                if not re.search(MAXID,query): 
                    print("expected call with maxId in query!")
                    exit(1)
                query = re.sub(MAXID+":"+r"[0-9]+",MAXID+":"+str(maxId),query)
                # log message
                sys.stderr.write(str(startI)+"."+str(runCounter)+" "+str(maxId)+" "+maxTime+"\n")
                # decrement remaining counter
                remaining -= 1
                # check if we can still access the api
                if remaining < 1: remaining = checkRemaining(t,APIGROUP,API)

# default action on script call: run main function
if __name__ == "__main__":
    sys.exit(main(sys.argv))
