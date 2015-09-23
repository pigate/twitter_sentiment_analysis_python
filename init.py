import pymongo
import sys

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

client.drop_database('sentStore')
db = client['sentStore']
words = db.terms
words.drop_index("term")
words.create_index("term", unique=True)

def prepDict(fp):
  scores = {}
  for line in fp:
    term, score = line.split("\t")
    #insert into db
    post = {"term": term,
		"score": int(score)}
    words.update({"term":term}, post, upsert=True)

def main():
  if (len(sys.argv) > 1):
    fileName = sys.argv[1]
  else:
    fileName = "AFINN-111.txt"
  print "Importing words from " + fileName
  sentiment_fp = open(fileName, "r")
  sentiment_fp.seek(0)
  prepDict(sentiment_fp) 

if __name__ == "__main__":
  main()
