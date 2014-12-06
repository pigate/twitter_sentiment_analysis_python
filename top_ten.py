import sys
import json

def fillHashtagDict(tweetfile):
  d = dict()
  totalNumWords = 0
  for tweet_line in tweetfile:
    tweet_bundle = json.loads(tweet_line)
    if "statuses" in tweet_bundle: #not live stream data
      for status in tweet_bundle["statuses"]:
        if ("entities" in status):
          if ("hashtags" in status["entities"]):
            hash_array = status["entities"]["hashtags"] #array of hashes
            for element in hash_array:
              actual_tag = element["text"]
              if actual_tag in d:
                d[actual_tag] += 1
              else:
                d[actual_tag] = 1
              totalNumWords += 1
    elif "entities" in tweet_bundle: #live stream data
      if "hashtags" in tweet_bundle["entities"]:
        hash_array = tweet_bundle["entities"]["hashtags"]
        for element in hash_array:
          actual_tag = element["text"]
          if actual_tag in d:
            d[actual_tag] += 1
          else:
            d[actual_tag] = 1
          totalNumWords += 1

  return (d, totalNumWords)


#returns freqDict = { c1: [w1, w2], c2: [w3, w4]... }
def reverseDict(hashDict):
  freqDict = dict() #{ count: [word1, word2], count: [w3, w4] ... }
  for word in hashDict:
    if hashDict[word] in freqDict:
      freqDict[hashDict[word]].append(word)
    else:
      freqDict[hashDict[word]] = [word]
  return freqDict

def printTop10HashTags(tweetfile):
  (d, totalNumWords) = fillHashtagDict(tweetfile)
  reverse_d = reverseDict(d)
  list_keys = list(reverse_d.keys())
  top_10 = list_keys[-10:]
  length = len(top_10)
  i = 0
  count = 0
  top_10.reverse()
  for keyindex in top_10:
    if (i >= length or count >= 10):
      break;
    i += 1
    for token in reverse_d[keyindex]:
      if count >= 10:
        break;
      print "{0}: {1}".format(token.encode('utf-8').strip(), float(keyindex)/totalNumWords)
      count += 1


def main():
  tweet_file = open(sys.argv[1])
  printTop10HashTags(tweet_file)

if __name__ == '__main__':
    main()


 


