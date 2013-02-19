from __future__ import print_function
import pymongo
import itertools as it
import functools as ft
import operator as op

db = pymongo.MongoClient('localhost', 1337)['rss-database']

SE1055_raw = it.chain(
    *map(
        op.methodcaller('split',', '),
        map(
            op.methodcaller('strip'),
            open('SE1055.dat')
        )
    )
)

SE1055 = map(
    lambda t: dict(title=t),
    SE1055_raw
)

db['SE1055'].remove() #swipe the collection
db['SE1055'].insert(SE1055)

