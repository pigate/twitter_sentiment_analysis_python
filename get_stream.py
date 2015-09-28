# -*- coding: utf-8 -*-
import oauth2 as oauth
import urllib2 as urllib
import datetime
import os
import multiprocessing
import json
import sys
import pymongo
import math
import time
from time import mktime
from datetime import datetime
from pymongo import MongoClient
import tw_utils
import redis

r = redis.StrictRedis(host='localhost', port = 6379, db=0)
pipe = r.pipeline()

client = MongoClient('localhost', 27017)
db = client['sentStore']
words = db.terms
tweets = db.tweets

api_key = os.environ["TWITTER_API_KEY"]
api_secret = os.environ["TWITTER_API_SECRET"]
access_token_key = os.environ["TWITTER_ACCESS_TOKEN_KEY"]
access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

oauth_token = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"

_debug = 0

http_handler = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using hard-coded credentials above.
'''

def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
  					token=oauth_token,
  					http_method=http_method,
  					http_url=url,
  					parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response

def fetchsamples(outfile): 
  #url = "https://api.twitter.com/1.1/search/tweets.json?q=kanye&count=100" 
  url = "https://stream.twitter.com/1/statuses/sample.json"
  parameters = []
  response = twitterreq(url, http_method, parameters)
  for line in response:
    outfile.write(line.strip() + "\n")

#fetches tweets from twitter api stream and writes to a new file
#returns file name
def fetch_timed_samples():
  curdatetime = datetime.now()
  fileName = str(curdatetime.year) + "_" + str(curdatetime.month) + "_" +  \
	str(curdatetime.day) + "_" + str(curdatetime.minute) + "_" + \
	str(curdatetime.second) + "_output.txt"

  outfile = open(fileName, "w+")
  p = multiprocessing.Process(target=fetchsamples, args=(outfile,))
  p.start()

  if _debug:
    p.join(5)
  else:
    p.join(30)

  if p.is_alive():
    p.terminate()
    p.join()

  #remove last line (usually is incompletely written)
  #move pointer to end
  outfile.seek(0, os.SEEK_END)
  #skip last char in file. if last line is null, delete it and the one before
  pos = outfile.tell() - 1
  while pos > 0 and outfile.read(1) != "\n":
    pos -= 1
    outfile.seek(pos, os.SEEK_SET)

  #as long as not at start of file, delete all chars ahead
  if pos > 0:
    outfile.seek(pos, os.SEEK_SET)
    outfile.truncate()
  outfile.write("\n")
  outfile.close()
  return fileName

def runAnalyzeTweets(fileName):
  tweet_file = open(fileName, 'r')  
  tweet_file.seek(0)
  analyzeTweets(tweet_file)
  tweet_file.close()

#retrieve score from dictionary
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
      text_array = filter(lambda x: len(x) >= 3 and tw_utils.isEnglish(x), 
	text_array)

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

      #record
      post_date = time.strptime(bundle['created_at'], 
	"%a %b %d %H:%M:%S +0000 %Y")
      dt = datetime.fromtimestamp(mktime(post_date))

      #if pos : neg > 1.2 classify as +
      # else if neg : pos > 1.2 classify as -
      # else classify as neutral (undecided)
      classification = 0
      if pos_score/neg_score > 1.2:
       classification = 1
      elif neg_score/pos_score > 1.2:
       classification = -1

      post = {"text": bundle["text"], "positive": pos_score, 
	"negative": neg_score, "date": str(dt), "class": classification}

      #update redis
      str_post = json.dumps(post)
      parent_key = str(dt) + ' ' + str(classification)  
      if r.exists(parent_key): 
        r.rpush(parent_key, str_post)
      else:
        r.rpush(parent_key, str_post) 
        r.expire(parent_key, 4800)
 
      #update mongodb
      tweets.insert_one(post)
      
  pipe.execute()

if __name__ == '__main__':
  fileName = fetch_timed_samples()
  runAnalyzeTweets(fileName) 
