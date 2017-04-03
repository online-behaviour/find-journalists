#!/usr/bin/python
"""
getFollowers.py: find users based on on followers of seed users
usage: ./getFollowers.py seed1 [seed2 ...] < file
notes: input file contains two types of line:
A. twitter user ids followed by a space and other information
B. a space followed by a user id: a follower of the last user of type A
20170306 erikt(at)xs4all.nl
"""

import operator
import re
import sys
import time
# import twitter library: https://github.com/sixohsix/twitter
from twitter import *

# constants
COMMAND = sys.argv[0]
# stop the program after this many warnings
MAXWARNINGS =  50
# maximum count for remaining Twitter requests
MAXREMAINING = 15

# put your authentication keys for Twitter in the local file definitions.py
# like: token = "..."
import definitions
token = definitions.token
token_secret = definitions.token_secret
consumer_key =  definitions.consumer_key
consumer_secret = definitions.consumer_secret

# user dictionaries
followerCounts = {}     # counts of followers of seed users, by ids
crawledFollowers = {}   # follower lists of crawled users, by screen names
crawledScreenNames = {} # screen names of crawled users, by ids 
crawledIds = {}         # ids of crawled users, by  screen names
seedScreenNames = sys.argv;       # seeds, by screen names
# convert to lower case
for i in range(0,len(seedScreenNames)):
   seedScreenNames[i] = seedScreenNames[i].lower()
seedIds = []
# remove program call from seeds list
seedScreenNames.pop(0)
# warning count
nbrOfWarnings = 0
# remaining count: while Twitter does not work
remaining = MAXREMAINING 

# select the next user to be processed:
# frequent in the user list but unprocessed
def selectUser():
    global followerCounts
    for userId in sorted(followerCounts,key=followerCounts.get,reverse=True):
        if not userId in seedIds:
            return userId
    return False

# add a potentionally interesting user to the list
def countFollower(userId):
    global followerCounts
    if userId in followerCounts:
        followerCounts[userId] += 1
    else:
        followerCounts[userId] = 1

# read known and unknown users
def readCrawled():
    global crawledFollowers
    global crawledScreenNames
    global crawledIds

    patternStartSpace = re.compile("^ ")     # matches initial space
    patternNumber = re.compile("^\d")        # matches a line-initial integer number
    patternFirstToken = re.compile("^\S+\s") # matches first token
    patternEnd = re.compile(" .*$")          # matches everything but the first token
    userId = None
    userScreenName = None
    followers = []
    for line in sys.stdin:
        # remove final newline
        line = line.rstrip()
        if patternStartSpace.match(line):
            # remove initial space to obtain the follower id
            followerId = patternStartSpace.sub("",line)
            # check if we are reading followers of a seed user
            if userScreenName in seedScreenNames:
                # count this follower of a seed user
               countFollower(followerId)
            followers.append(followerId)
        elif patternNumber.match(line):
            # check if there is a previous user
            if not userScreenName is None:
                # store the followers of this user in crawled
                crawledFollowers[userScreenName] = followers
                crawledScreenNames[userId] = userScreenName
                crawledIds[userScreenName] = userId
                sys.stdout.write("# storing user "+userScreenName+" in tables\n")
            # get the user id from the line: the first token
            userId = patternEnd.sub("",line)
            # get the user name from the lineL the second token
            userScreenName = patternFirstToken.sub("",line)
            userScreenName = patternEnd.sub("",userScreenName).lower()
            # add user id to seed ids if this is a seed user
            if userScreenName in seedScreenNames and not userId in seedIds:
                seedIds.append(userId)
                print "# added seed %d %s %s" % (len(seedIds),userScreenName,userId)
                sys.stdout.flush()
            # clear followers list
            followers = []

# get all the followers of a user (id or screen name) from Twitter
def getAllFollowers(user):
    global crawledFollowers
    global crawledScreenNames
    global crawledIds
    global nbrOfWarnings

    # authenticate
    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
    # lookup the screen name and the id of the current user
    patternNumber = re.compile("^\d+$") # matches an integer number
    # initialize followers list
    followers = []
    userScreenName = "UNKNOWN"
    userId = 0
    try:
        # if the user is a number: assume a user id
        if patternNumber.match(user):
            userId = user
            # get the user info from Twitter
            user_info = t.users.lookup(user_id = user)
        # else assume a screen name
        else:
            userScreenName = user.lower()
            # get the user info from Twitter
            user_info = t.users.lookup(screen_name = user)
        # get the id and the name of the user
        userId = user_info[0]["id_str"]
        userScreenName = user_info[0]["screen_name"].lower()
        # get followers from Twitter
        results = getFollowers(t,userScreenName,-1)
        followers = results["followers"]
        # check if there are more followers
        while results["next_cursor"] > 0:
            results = getFollowers(t,userScreenName,results["next_cursor"])
            followers.extend(results["followers"])
        # extract the followers from the query result
        # add user to crawled list
    except:
        sys.stderr.write("error crawling user "+str(userId)+" "+userScreenName+"\n")
        nbrOfWarnings += 1
    crawledFollowers[userScreenName] = followers
    crawledScreenNames[userId] = userScreenName
    crawledIds[userScreenName] = userId
    # write the results for future runs
    print "%s %s :" % (userId,userScreenName)
    for f in followers:
        print " %s" % (f)
    print "# crawled user: %s and %s (%d)" % (userScreenName,userId,len(seedIds))
    sys.stdout.flush()

# get a single batch (5000 ids) of followers of a user (screen name) from Twitter
def getFollowers(t,userScreenName,cursor):
    global nbrOfWarnings
    global remaining

    print "# calling getFollowers for %s" % (userScreenName)
# 20170330 twitter rate check stopped working: always returns remaining=15
#   # check the rate limit; if 0 then wait
#   rates = t.application.rate_limit_status(resources = "friends")
#   # extract the remaining count from the results
#   remaining = rates['resources']['friends']['/friends/ids']['remaining']
#   # check if there are remaining calls
#   while remaining < 1:
#       # if not: wait one minute
#       time.sleep(60)
#       # fetch the value of the remaining count from Twitter
#       rates = t.application.rate_limit_status(resources = "friends")
#       remaining = rates['resources']['friends']['/friends/ids']['remaining']
    if remaining <= 0:
       time.sleep(1+(MAXREMAINING*60))
       remaining = MAXREMAINING
    sys.stdout.write("# searching with "+str(remaining)+" remaining calls\n")
    followers = []
    nextCursor = 0
    # check which users this user follows
    try:
        query = t.friends.ids(screen_name = userScreenName, cursor = cursor)
        followers = query["ids"]
        nextCursor = query["next_cursor"]
    except TwitterHTTPError as e:
        # if there is an error: report this
        sys.stderr.write("error for user "+userScreenName+"!\n")
        nbrOfWarnings += 1
        # continue and assume that the user follows no one
    remaining -= 1
    print "# finished call getFollowers for %s (%d)" % (userScreenName,len(followers))
    sys.stdout.flush()
    return({"next_cursor":nextCursor,"followers":followers})

# collect the followers of the seed users
def getFollowersSeeds():
    global crawledFollowers
    global seedScreenNames

    # check all seed users
    for userScreenName in seedScreenNames:
        # check if the followers of this user are known
        if not userScreenName in crawledFollowers:
            # if not: fetch the followers from Twitter
            getAllFollowers(userScreenName)
        if nbrOfWarnings >= MAXWARNINGS:
            sys.exit(COMMAND+": too many warnings: "+str(nbrOfWarnings))

def main():
    global seedScreenNames
    global seedIds
    global crawledScreenNames
    global crawledFollowers
    global followerCounts

    # read the crawled users from STDIN
    readCrawled()
    # get the followers of the seed users from Twitter
    getFollowersSeeds()
    # expand the seed list: find other users that the seed users follow
    while True:
        # select the most frequent unprocessed user
        userId = selectUser()
        # quit if no suitable user was found
        if userId is False:
            sys.exit(COMMAND+": cannot select user! len(followerCounts)="+str(len(followerCounts)))
        if nbrOfWarnings >= MAXWARNINGS:
            sys.exit(COMMAND+": too many warnings: "+str(nbrOfWarnings))
        # check if the followers of this user are known
        if not userId in crawledScreenNames or not crawledScreenNames[userId] in crawledFollowers:
            # if not: fetch the followers from Twitter
            getAllFollowers(userId)
        # get the screen name of this user from the stored data
        userScreenName = crawledScreenNames[userId]
        # add the screen name of the user to the seed users
        seedScreenNames.append(userScreenName)
        # add the id of the user to the seed users
        seedIds.append(userId)
        # show log line
        print "# added to seeds: %d %s %s" % (len(seedIds),userScreenName,userId)
        sys.stdout.flush()

if __name__ == "__main__":
    sys.exit(main())
