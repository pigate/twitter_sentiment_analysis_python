# -*- coding: utf-8 -*-
import json
import sys
import pymongo
import math
import time
from time import mktime
from datetime import datetime

#python tweet_sentiment.py AFINN-111.txt tweet_file.txt results.txt
#writes results as sentiment rating per line in results.txt
#must differentiate between twitter's live stream and not live stream.

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client['sentStore']
words = db.terms
tweets = db.tweets

def isEnglish(s):
  try:
    s.encode('ascii')
  except UnicodeEncodeError:
    return False
  else:
    return True

#print how many lines are in file
def lines(fp):
    print str(len(fp.readlines()))

def main():
    tweet_file = open(sys.argv[1])
    tweet_file.seek(0)
    analyzeTweets(tweet_file)
    tweet_file.close()

#retrive score from dictionary
def getScore(word):
  term = words.find_one({"term":word})
  if term is not None:
    return term["score"]

#calculates sentiment only for known terms
def analyzeTweets(ifp):
  for line in ifp:
    bundle = json.loads(line)
    if ("delete" in bundle):
      continue

    #twitter streaming format
    if ("text" in bundle): 
      text = bundle["text"]
      text_array = map(lambda y: y.lower(), text.split(' '))
      tot_length = len(text_array)
      text_array = filter(lambda x: len(x) >= 3 and isEnglish(x), text_array)

      #ignore tweets where more than half of words are non English
      if len(text_array) < tot_length/2:
        continue

      #calculate scores
      score_array = filter(lambda y: y is not None, 
		map(lambda x: getScore(x), text_array)) 
      pos_score = reduce(lambda a, b: a + b, 
		map(lambda y: math.log(y, 2), 
		filter(lambda x: x > 0, score_array)), 1.0)
      neg_score = reduce(lambda a, b: a + b, 
		map(lambda y: math.log(-y, 2), 
		filter(lambda x: x < 0, score_array)), 1.0) 

      #insert into db
      post_date = time.strptime(bundle['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
      dt = datetime.fromtimestamp(mktime(post_date))

      #if pos : neg > 1.2 classify as +
      # else if neg : pos > 1.2 classify as -
      # else classify as neutral (undecided)
      classification = 0
      if pos_score/neg_score > 1.2:
       classification = 1
      elif neg_score/pos_score > 1.2:
       classification = -1
 
      #update db 
      post = {"text": bundle["text"], "positive": pos_score, "negative": neg_score, "date": dt, "class": classification}
      tweets.insert_one(post)

    #twitter query format (non streaming): one big fat collection of statuses
    elif ("statuses" in bundle): 
      for status in bundle["statuses"]: 
        if ("text" in status):
          text = status["text"]
          text_array = filter(lambda x: len(x) >= 3 and isEnglish(x), text.split(' '))
 
          #ignore tweets where more than half of words are non English
          if len(text_array) < tot_length/2:
            continue         

          #calculate scores
          score_array = filter(lambda y: y is not None, 
		map(lambda x: getScore(x), text_array))
          pos_score = reduce(lambda a, b: a + b, 
		map(lambda y: math.log(y, 2), 
		filter(lambda x: x > 0, score_array)), 1.0)
          neg_score = reduce(lambda a, b: a + b, 
		map(lambda y: math.log(-y, 2), 
		filter(lambda x: x < 0, score_array)), 1.0) 
 
          #if pos : neg > 1.2 classify as +
          # else if neg : pos > 1.2 classify as -
          # else classify as neutral (undecided)
          classification = 0
          if pos_score/neg_score > 1.2:
           classification = 1
          elif neg_score/pos_score > 1.2:
           classification = -1

          #update db
          post_date = time.strptime(bundle['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
          dt = datetime.fromtimestamp(mktime(post_date))
          post = {"text": bundle["text"], "positive": pos_score, "negative": neg_score, "date": dt, "class": classification}
          tweets.insert_one(post)

if __name__ == '__main__':
    main()
