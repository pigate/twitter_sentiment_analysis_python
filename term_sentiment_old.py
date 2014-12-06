#python term_sentiment.py AFINN-111.txt tweet_file
#writes results into results_term_sentiment.txt
#must work for both live stream and not live stream

import sys
import json
import math
class StatData:
  pos, neg = [], []
  def insert(self, value):
    if value < 0:
      self.neg.append(value)
    else:
      self.pos.append(value)

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
   
#    if t in d:
#      known_count += 1
#      dictsay = d[t]
#      if dictsay < 0:
#        score = score - dictsay*dictsay
#      else:
#        score = score + dictsay*dictsay
#      #score = score + d[t]
#  abs_val = math.sqrt(abs(score))
#  if known_count == 0:
#    if score < 0:
#      return abs_val*(-1.0)
#    else:
#      return abs_val
#  else:
#    if score < 0:
#      return abs_val*(-1.0)/known_count
#    else:
#      return abs_val/known_count
    
def mungeTweet(tweet, newDict, defaultDict):
  tokens = [t.lower() for t in tweet.split(' ')]
  derived_score = getScore(tokens, defaultDict)
  for t in tokens:
    if t not in defaultDict:
      newDict[t] = StatData()
      newDict[t].insert(derived_score)

    
#op must be open for writing
#fp pointer must point to beginning of file    
#writes term sentiment(float). separated by a space
def deriveTermSentiment(fp, op, dictp):
  defaultDict = buildDefaultDict(dictp)
  #
  newDict = dict()
  i = 0
  for tweet_line in fp:
    tweet_bundle = json.loads(tweet_line)
    if "statuses" in tweet_bundle:
      for status in tweet_bundle["statuses"]:
        if ("text" in status):
          text = status["text"]
        mungeTweet(text.replace('.','').replace('!','').replace(',','').replace('\n',''), newDict, defaultDict)
    elif "text" in tweet_bundle: #live stream
      print "encounted {0}".format(i)
      i += 1
      text = tweet_bundle["text"].replace('.','').replace('!','').replace(',','').replace('\n','')
      print text
      mungeTweet(text.replace('.','').replace('!','').replace(',','').replace('\n',''), newDict, defaultDict)
  print "********\n***********\n*********\n**********\n*******"
  user_choice = raw_input("Press Enter to continue counting: ")
  i = 0
  #for elem in newDict: WAY TOO SLOW!!!!!! Naive way to go through a dict
  list_key = list(newDict.keys())
  for elem in list_key:  
    total = newDict[elem].pos
    total.extend(newDict[elem].neg)
    avg_score = 5.0*(reduce(lambda x, y: x + y, total)/(1.00*len(total)))
    op.write("{0} {1}\n".format(elem.encode('utf-8').strip(), avg_score))
    i+= 1
    print "{0} words done".format(i)

#Node for string type


#class Binode:
#  left, right, data, value, numTimes = None, None, "", 0, 0
#  def __init__(self, data=None, value=0): 
#    print "created" + data
#    self.left = None
#    self.right = None
#    self.data = data
#    self.value = value
#    self.numTimes = 1
#
#  def insert(self, data, value):
#    if self.data == None: 
#      #is empty. insert here
#      self.data = data
#      self.value = value
#    elif data < self.data: 
#      if self.left is None:
#        self.left = Binode(data)
#      else: 
#        self.left.insert(data)
#    elif data > self.data:
#      if self.right is None:
#        self.right = Binode(data)
#      else:
#        self.right.insert(data)
#    else:
#      self.value = (self.value * self.numTimes + value)/( ++self.numTimes );
#
#  def lookup(self, data):
#    if data < self.data:
#      if self.left is None:
#        return false
#      return self.left.lookup(data)
#    elif data > self.data:
#      if self.right is None:
#        return false
#      return self.right.lookup(data)
#    else:
#      return true
#
#  def printInOrder(self):
#    if self.left is not None:
#      self.left.printInOrder()
#    print self.data
#    if self.right is not None:
#      self.right.printInOrder()
#
#  def printIntoFile(fp):
#    if self.left is not None:
#      self.left.printIntoFile(fp)
#    print self.data + "\t" + self.value
#    if self.right is not None:
#      self.right.printIntoFile(fp)



def main():
    sent_file = open(sys.argv[1]) #AFIN
    tweet_file = open(sys.argv[2]) #output.txt
    output_file = open("results_term_sentiment.txt", "w")
    output_file.truncate
    deriveTermSentiment(tweet_file, output_file, sent_file)
    
if __name__ == '__main__':
    main()

