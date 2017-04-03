#!/usr/bin/python
# makevec: create vectors with information about followers
# usage: makevec < file
# 20170307 erikt(at)xs4all.nl

import re
import sys
import csv

command = sys.argv[0]
# get seed set of screen names from command line arguments
seedScreenNames = sys.argv
# convert to lower case
for i in range(0,len(seedScreenNames)):
   seedScreenNames[i] = seedScreenNames[i].lower()
# remove program call from seeds list
seedScreenNames.pop(0)
# ids of seeds: fill it when we know the ids
seedIds = {}
# factor for determining if a user is interesting
# 1. follows at least this percentage seeds
# 2. at least this percentage of seeds follows this user
FACTOR = 0.10
# file with data on newly found users
othersFile = "others.csv"
# screen name column in the others file
SCREENNAMECOLUMN = 3
# occupation column in the others file
OCCUPATIONSCOLUMN = 1

# test if a user is interesting
def interesting(user):
    # seed users are interesting
    if user["SCREENNAME"] in seedScreenNames:
        return(True)
    # determine the strength of the link of this user with the seeds
    # first check i the two follower counts are above zero
    if not user["ID"] in userFollowedBySeed or not user["ID"] in seedFollowedByUser:
        # if not they they are not high enough
        return(False)
    minimum = min([userFollowedBySeed[user["ID"]],seedFollowedByUser[user["ID"]]])
    if (minimum >= FACTOR*len(seedScreenNames)): return(True)
    else: return(False)

# information on the current user: id, screen name and friends
user = None
# user information: ids
userIdsDict = {}
userIdsList = []
# user information: names (aka screen_names)
userNamesList = []
# friends: the accounts that are followed by the users
friendsDict = {}
friendsList = []
# screen names by id
screenNames = {}
# ids by screen name
ids = {}

# pattern for checking for initial space and removing it
patternStartSpace = re.compile("^ ")
# pattern for checking for initial digit, first of a user id
patternStartNumber = re.compile("^\d")
# pattern for removing the line-initial token
patternFirstToken = re.compile("^\S+\s")
# pattern for removing all but the line-initial token
patternEnd = re.compile(" .*$")

# read information in others.csv file for statistical analysis
others = {}
try:
    with open(othersFile,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader: 
            others[row[SCREENNAMECOLUMN].lower()] = row
        csvfile.close()
except:
    # do nothing when the file cannot be read
    pass

# read users and the friends they follow, from files *out*
# expected line format: 
# - line starts with user id: the main user; next: space name space colon
# - line starts with space: account followed by the user
# for every line in the input
for line in sys.stdin:
    # remove final newline
    line = line.rstrip()
    # if the line starts with a single space: expect a friend id
    if patternStartSpace.match(line):
        # remove initial space
        line = patternStartSpace.sub("",line)
        # add user to the friends list
        user["FRIENDS"].append(line)
        # if this is a unknown friend id
        if not line in friendsDict:
            # mark the friend id as known
            friendsDict[line] = 1
            # add the friend id to the list with friend ids
            friendsList.append(line)
        else:
            # if the friend id is known: count its usage
            friendsDict[line] += 1
    # if the line starts with a number: expect a user id
    elif patternStartNumber.match(line):
        # user change: check if we already processed a user
        if not user is None and not user["ID"] in userIdsDict:
            # add the previously processed user to the user lists
            userIdsDict[user["ID"]] = len(userIdsList)
            # usersIdsDict points to the user info in usersIdsList
            userIdsList.append(user)
        # clear the user info
        user = {}
        # get the user id from the line
        userId = patternEnd.sub("",line)
        # get the user name (screen_name) from the line
        userName = patternFirstToken.sub("",line)
        userName = patternEnd.sub("",userName).lower()
        # add the user id to the user info
        user["ID"] = userId
        # add the user name to the user info
        user["SCREENNAME"] = userName
        user["FRIENDS"] = []
        screenNames[userId] = userName
        ids[userName] = userId
        # if the user id is not in the friends list
        if not userId in friendsDict:
            # user unknown as friend: add the user to the friends list
            friendsDict[userId] = 0
            friendsList.append(userId)

# if we processed a user
if not user is None:
    # add the previously processed user to the user lists
    userIdsDict[user["ID"]] = len(userIdsList)
    # usersIdsDict points to the user info in usersIdsList
    userIdsList.append(user)

# create dictionary of seed ids
for seedUser in seedScreenNames:
    if not seedUser in ids:
        # seed user has no information: was it crawled?
        sys.exit(command+": unknown seed user "+seedUser+"!")
    seedIds[ids[seedUser]] = 1
 
# count how often every user follows a seed user and vice versa
seedFollowedByUser = {}
userFollowedBySeed = {}
# for every user
for user in userIdsList:
    # assume a reflexive relation: each user follows himself
    if user["ID"] in seedIds:
        if user["ID"] in userFollowedBySeed: userFollowedBySeed[user["ID"]] += 1
        else: userFollowedBySeed[user["ID"]] = 1
        if user["ID"] in seedFollowedByUser: seedFollowedByUser[user["ID"]] += 1
        else: seedFollowedByUser[user["ID"]] = 1
    # for every friend of this user
    for friend in user["FRIENDS"]:
        if user["ID"] in seedIds:
            if friend in userFollowedBySeed: userFollowedBySeed[friend] += 1
            else: userFollowedBySeed[friend] = 1
        if friend in seedIds:
            if user["ID"] in seedFollowedByUser: seedFollowedByUser[user["ID"]] += 1
            else: seedFollowedByUser[user["ID"]] = 1
   
# make a list of interesting users for the columns of the output table
interestingUsers = []
for user in userIdsList:
    # if the user is interesting
    if interesting(user): interestingUsers.append(user["ID"])

# output a vector for each interesting users
for user in userIdsList:
    if not user["ID"] in userFollowedBySeed: userFollowedBySeed[user["ID"]] = 0
    if not user["ID"] in seedFollowedByUser: seedFollowedByUser[user["ID"]] = 0
    minimum = min([userFollowedBySeed[user["ID"]],seedFollowedByUser[user["ID"]]])
    info = ""
    if user["SCREENNAME"] in others: info = ","+others[user["SCREENNAME"]][OCCUPATIONSCOLUMN]
    # if the user is not interesting
    if not interesting(user):
        # print log line 
        sys.stderr.write(str(minimum)+","+str(userFollowedBySeed[user["ID"]])+","+str(seedFollowedByUser[user["ID"]])+","+user["SCREENNAME"]+",NO"+ info+"\n")
    else: # this is an interesting user
        # print log line 
        sys.stderr.write(str(minimum)+","+str(userFollowedBySeed[user["ID"]])+","+str(seedFollowedByUser[user["ID"]])+","+user["SCREENNAME"]+",YES"+info+"\n")
        # add the user name to the output list
        out = [user["SCREENNAME"]]
        # for every selected followed user
        for friendId in interestingUsers:
            # if the user follows this friend
            if friendId in user["FRIENDS"] or friendId is user["ID"]:
                # add 1 to the output list
                out.append(1)
            # if the user does not follow this friend
            else:
                # add 0 to the output list
                out.append(0)
            # if this friend follows the user
            if user["ID"] in userIdsList[userIdsDict[friendId]]["FRIENDS"] or \
               user["ID"] is friendId:
                # add 1 to the output list
                out.append(1)
            # if this friend does not follow the user
            else:
                # add 0 to the output list
                out.append(0)
        # print the output list
        for i in range(0,len(out)):
            if i > 0: sys.stdout.write(",")
            sys.stdout.write(str(out[i]))
        sys.stdout.write("\n") 

sys.exit()
