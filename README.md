# journalists code

Software for discovering Twitter accounts of political
journalists given accounts of politicians.

Run like:

```
python getFollowers.py markrutte sybrandbuma apechtold > getFollowers.out 
```

to collect the people that are followed by the users in
your seed list. The script needs your Twitter account data
to be stored in a file definitions.py in the format:

```
# twitter.com authentication keys
token = "???"
token_secret = "???"
consumer_key = "???"
consumer_secret = "???"
```

Replace the strings "???" with the key information from 
https://apps.twitter.com , see https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/ for instructions

In order to find more relevant users, you can run this command 
after getFollowers.py is finished:

```
python makevec.py markrutte sybrandbuma apechtold < getFollowers.out > makevec.out 2> makevec.err
```

It generates a selection of relevant users (makevec.err) and 
a vector representations for these users (makevec.out)

Input data files for Dutch politicians can be requested
from Erik Tjong Kim Sang e.tjong.kim.sang(at)esciencenter.nl

