#python term_sentiment.py AFINN-111.txt tweet_file
#writes results into results_term_sentiment.txt
#must work for both live stream and not live stream

import sys
import json
import math
class StatData:
  def __init__(self, key, value=0):
    self.pos = []
    self.neg = []
    self.key = key
    self.left = None
    self.right = None  
    self.insert(key, value)
  def insert(self, key, value=0):
    if self.key == key:
      if value < 0:
        self.neg.append(value)
      elif value > 0:
        self.pos.append(value)
    elif self.key > key:
      if self.left is None:
        self.left = StatData(key, value)
      else:
        self.left.insert(key, value) 
    else:
      if self.right is None:
        self.right = StatData(key, value)
      else:
        self.right.insert(key, value)
  def inOrderDFS(self, fun):
    if self.left is not None:
      self.left.inOrderDFS(fun)
    fun(self)
    if self.right is not None:
      self.right.inOrderDFS(fun)
  def avg_score(self):
    length = len(self.pos) + len(self.neg)
    if length == 0:
      return 0
    else:
      return (reduce(lambda x, y: x + y, self.pos, 0) + reduce(lambda x, y: x+ y, self.neg, 0))/(1.00*length)
  
class StatTree:
  def __init__(self, key=None, left=None, right=None):
    if key is None:
      self.root = None
    else:
      self.root = StatData(key)
    
  def insert(self, key, value):   
    #TODO: implement
    if self.root is None:
      self.root = StatData(key, value)
    else:
      self.root.insert(key, value)
  def inOrderDFS(self, fun):
    if (self.root is not None):
      self.root.inOrderDFS(fun)

def hw():
    print 'Hello, world!'

def lines(fp):
    print str(len(fp.readlines()))
#NOTE: the normalizing is not good enough. Need to map values to between [-5, 5]

def buildDefaultDict(fp):
  d = dict()
  for line in fp:
    token = line.strip().split('\t')
    d[token[0]]= int(token[1])
  return d

def getScore(tokens, d):
  score = 0
  pos = 0
  neg = 0
  known_count = 0
  for t in tokens:
    if t in d:
      known_count += 1
      if d[t] > 0:
        pos += d[t]
      else:
        neg += d[t]
  if known_count == 0:
    return 0
  blown_up_score = pos*pos - neg*neg #weighted by grouping and squaring
  if blown_up_score == 0:
    return 0
  weighted_square = math.sqrt(abs(blown_up_score))
  normalized_square = weighted_square/math.sqrt(known_count)
  weighted_score = normalized_square*(blown_up_score/abs(blown_up_score)) #sign it +/-
  return weighted_score
   
def mungeTweet(tweet, dTree, defaultDict):
  tokens = [t.lower() for t in tweet.split(' ')]
  derived_score = getScore(tokens, defaultDict)
  for t in tokens:
    if t not in defaultDict:
      dTree.insert(t,derived_score)

    
#op must be open for writing
#fp pointer must point to beginning of file    
#writes term sentiment(float). separated by a space
def deriveTermSentiment(fp, op, dictp):
  defaultDict = buildDefaultDict(dictp)
  dTree = StatTree()
  for tweet_line in fp:
    tweet_bundle = json.loads(tweet_line)
    if "statuses" in tweet_bundle:
      for status in tweet_bundle["statuses"]:
        if ("text" in status):
          text = status["text"]
        mungeTweet(text.replace('.','').replace('!','').replace(',','').replace('\n',''), dTree, defaultDict)
    elif "text" in tweet_bundle: #live stream
      text = tweet_bundle["text"].replace('.','').replace('!','').replace(',','').replace('\n','')
      mungeTweet(text.replace('.','').replace('!','').replace(',','').replace('\n',''), dTree, defaultDict)
  #for elem in dTree: WAY TOO SLOW!!!!!! Naive way to go through a dict
  #  list_key = list(dTree.keys())
  #  for elem in list_key:  
  #    total = dTree[elem].pos
  #    total.extend(dTree[elem].neg)
  #    avg_score = 5.0*(reduce(lambda x, y: x + y, total)/(1.00*len(total)))
  #    op.write("{0} {1}\n".format(elem.encode('utf-8').strip(), avg_score))
  #    i+= 1
  #    print "{0} words done".format(i)
  dTree.inOrderDFS(lambda node: op.write("{0} {1}\n".format(node.key.encode('utf-8').strip(), node.avg_score())))

def main():
    sent_file = open(sys.argv[1]) #AFIN
    tweet_file = open(sys.argv[2]) #output.txt
    output_file = open("results_term_sentiment.txt", "w")
    output_file.truncate
    deriveTermSentiment(tweet_file, output_file, sent_file)
    
if __name__ == '__main__':
    main()

