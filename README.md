# journalists code

Software for discovering Twitter accounts of political
journalists given accounts of politicians.

Run like:

```
python getFollowers.py markrutte sybrandbuma apechtold > getFollowers.out 
```

to collect the people that are followed by the users in
your seed list

And then run:

```
python makevec.py markrutte sybrandbuma apechtold < getFollowers.out > makevec.out 2> makevec.err
```

to obtain a selection of relevant users (makevec.err) and 
a vector representations for these users (makevec.out)

Input data files for Dutch politicians can be requested
from Erik Tjong Kim Sang e.tjong.kim.sang(at)esciencenter.nl

