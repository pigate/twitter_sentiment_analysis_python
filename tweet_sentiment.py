import json
import sys
import pymongo

#python tweet_sentiment.py AFINN-111.txt tweet_file.txt results.txt
#writes results as sentiment rating per line in results.txt
#must differentiate between twitter's live stream and not live stream.

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

client.drop_database('sentStore')
db = client['sentStore']
words = db['word-collection']

#print how many lines are in file
def lines(fp):
    print str(len(fp.readlines()))

def main():
    sent_file = open(sys.argv[1])
    tweet_file = open(sys.argv[2])
    sent_file.seek(0)
    tweet_file.seek(0)
    results_file = open(sys.argv[3], "w")
    analyzeTweets(sent_file, tweet_file, results_file)
    sent_file.close()
    tweet_file.close()
    results_file.close()

#retrive score from dictionary
def getScore(word, affinDict):
  if word in affinDict:
    return affinDict[word]
  else:
    return 0

#creates dictionary from AFINN text document.
def prepDict(fp):
  scores = {}
  for line in fp:
    term, score = line.split("\t") #word and sentiment score delimited by tab
    scores[term] = int(score)
  return scores

#calculates sentiment only for known terms
def analyzeTweets(afp, ifp, ofp):
  affinDict = prepDict(afp)
  ofp.truncate
  for line in ifp:
    #get text. split text into tokens
    bundle = json.loads(line)
    if ("text" in bundle): #live stream data. line by line
      text = bundle["text"]
      text_array = text.split(' ')
      #acc score for tokens
      score_array = map(lambda x: getScore(x, affinDict), text_array)
      final_score = reduce(lambda x, y: x + y, score_array)
      #write score into ofp
      ofp.write(str(final_score)+'\n')
    elif ("statuses" in bundle): #query data. one big fat collection of statuses
      for status in bundle["statuses"]: #tweet is actually a collection of statuses
        if ("text" in status):
          text = status["text"]
          text_array = text.split(' ')
          score_array = map(lambda x: getScore(x, affinDict), text_array)
          final_score = reduce(lambda x, y: x + y, score_array)
          ofp.write(str(final_score)+'\n')

        

if __name__ == '__main__':
    main()
