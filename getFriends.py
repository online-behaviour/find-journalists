#!/usr/bin/python3
"""
getFriends.py: get ids of users that some user is following
usage: ./getFriends.py screenname
notes: * based on getTweets.py and getFollwers.py
       * manual: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
20200907 erikt(at)xs4all.nl
"""

import sys
from twitter import *
import definitions

COMMAND = sys.argv.pop(0)
FOLLOWERS = "followers"
USAGE = "usage: "+COMMAND+" screenname"

def getFollowers(t,userScreenName,cursor):
    followers = []
    nextCursor = 0
    try:
        query = t.friends.ids(screen_name = userScreenName, cursor = cursor)
        followers = query["ids"]
        nextCursor = query["next_cursor"]
    except TwitterHTTPError as e:
        sys.stderr.write("error for user "+userScreenName+"!\n")
    sys.stdout.flush()
    return({"next_cursor":nextCursor,"followers":followers})

def main(argv):
    token = definitions.token
    token_secret = definitions.token_secret
    consumer_key =  definitions.consumer_key
    consumer_secret = definitions.consumer_secret
    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
    for userScreenName in argv:
        results = getFollowers(t,userScreenName,-1)
        print(userScreenName," ".join([str(x) for x in results[FOLLOWERS]]))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
