#!/usr/bin/python
"""
getTweets.py: get recent tweets from Twitter within certain time frame
usage: ./getTweets > file
20170309 erikt(at)xs4all.nl
"""

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
COMMAND = sys.argv[0]
# maximum id of tweet, start of backwards search; empty value: -1
MAXID = 848626338844090373 # 20170402 22:01
# minimum id of tweet; empty value: -1
MINID = 848610736943374336 # 20170402 20:59
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
# twiqsTrack: list of twiqs track queries
twiqsTrack = ["een","het","ik","niet","maar","voor","ook","als","heb","naar","nog","echt","moet","weer","mijn","zijn","bij","jij","toch","lekker","geen","gewoon","gaat","meer","slapen","weet","mensen","alleen","kijken","leren","heeft","vandaag","eens","hoor","uur","jou","veel","denk","maken","leuk","heel","zou","daar","komt","eten","iets","vind","hebben","altijd","vanavond","jullie","thuis","iemand","helemaal","waar","waarom","wakker","komen","beetje","nieuwe","worden","steeds","gezellig","straks","kunnen","zeggen","iedereen","ofzo","omdat","werken","allemaal","moeten","andere","jaar","terug","staat","kut","ging","erg","zien","vroeg","bijna","zelf","zegt","vrij","zeker","werk","#gtst","#tienerthings","#bzv","#wiedoethet","#durftevragen","#nieuws","#tienerfeiten","#dutchteenagers","#dwdd","#penw","#widm","#slajezelf","#voetbalfans","#pownews","#geenzin","#slapen","#lekker","#rtl7","informatiekunde","infokunde","op","wel","zo","aan","gaan","wil","doen","mij","dus","uit","morgen","goed","wie","dit","hij","hier","nou","bent","zit","zin","rug","niks","dag","laat","weg","alles","doet","hem","tegen","deze","haar","zie","anders","zeg","huis","zal","jaa","nooit","tijd","hou","klaar","keer","wordt","hele","wij","snel","hebt","vakantie","kijk","beter","mooi","ons","eerst","toen","krijg","gwn","moeder","slaap","dood","weten","leven","gedaan","dingen","dacht","halen","leuke","eigenlijk","maakt","hoop","volgens","schatje","laatste","zitten","gelukkig","gezien","misschien","eindelijk","stad","gehad","buiten","zei","wanneer","geweest","daarna","wachten","haat","zonder","verder","lief","maandag","blij","egt","staan","binnen","eerste","paar","laten","soms","beneden","alweer","niemand","voel","kamer","dagen","zaterdag","enzo","mooie","onder","gelijk","praten","onze","wilt","moest","volgende","maak","willen","gemaakt","lieve","achter","nodig","kapot","wereld"]

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

def main():
    # Twitter autnetication keys
    token = definitions.token
    token_secret = definitions.token_secret
    consumer_key =  definitions.consumer_key
    consumer_secret = definitions.consumer_secret
    # warning count
    nbrOfWarnings = 0

    # authenticate
    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
    # start with this element of the query list
    i = 0
    # repeat while there are unprocessed query words
    while i+1 < len(twiqsTrack):
        # create the query: add first word
        query = twiqsTrack[i]
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
        # set initial ids for backward search: start from maxId, stop at minId
        maxId = MAXID
        minId = MINID
        # run counter initialization
        runCounter = 0
        # remmeber which tweets have been collected
        seen = {}
        # repeat while tweets found
        while "statuses" in results and len(results["statuses"]) > 0:
            # empty results list
            results = []
            # increase run counter
            runCounter += 1
            # get tweets from Twitter
            try:
                if maxId < 0 and minId < 0:
                    # query arguments: https://dev.twitter.com/rest/reference/get/search/tweets
                    results = t.search.tweets(q = query, lang = "nl", count = 100)
                elif maxId < 0 and minId >= 0:
                    results = t.search.tweets(q = query, lang = "nl", count = 100, since_id = minId)
                elif maxId >= 0 and minId < 0:
                    results = t.search.tweets(q = query, lang = "nl", count = 100, max_id = maxId)
                elif maxId >= 0 and minId >= 0:
                    results = t.search.tweets(q = query, lang = "nl", count = 100, max_id = maxId, since_id = minId)
                else:
                    sys.exit(COMMAND+": cannot happen\n")
            except TwitterHTTPError as e:
                # if there is an error: report this
                sys.stderr.write("error: "+str(e))
                nbrOfWarnings += 1
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
                        print json.dumps(tweet,sort_keys=True)
                        # add tweet id to seen dictionary
                        seen[thisId] = True
                # decrease maxId to avoid fetching the same tweet
                maxId -= 1
                # log message
                sys.stderr.write(str(startI)+"."+str(runCounter)+" "+str(maxId)+" "+maxTime+"\n")
                # decrement remaining counter
                remaining -= 1
                # check if we can still access the api
                if remaining < 1: remaining = checkRemaining(t,APIGROUP,API)

# default action on script call: run main function
if __name__ == "__main__":
    sys.exit(main())
