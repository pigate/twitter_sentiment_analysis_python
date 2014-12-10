import sys
import re
import json

#to run frequency.py tweet_file result.txt
#works for both live stream data and non live data

#init
#@params(element)
#freqCargo.update(element)
#@return True if updated
#@return False if not updated (attempt to update with wrong element)
class FreqNode:
  def __init__(self, value, left=None, right=None):
    self.value = value
    self.count = 1
    self.left = left
    self.right = right
 

#init
#@params (optional) cargo, left and right
#freqTree.inOrderDFS(fun)
#@params fun
#applies fun to each element. Traverses in-order, DFS
#freqTree.search(cargo_key)
#@params cargo_key
#@return best match cargo that fits cargo_key
#	note this cargo may actually not match. 
#	Must check cargo's element
#@insert
 

class FreqTree:
  def __init__(self, value=None):
    if value is None: #make empty tree
      self.root = None
      self.totalCount = 0
    else:
      self.root = FreqNode(value)
      self.totalCount = 1
  def search(self, key):
    if self.root is None:
      return False
    else:
       return self.search_helper(self.root, key)
  def search_helper(self, node, key):
    if node is None:
       return False
    elif node.value == key:
       return True
    elif node.value > key:
       return self.search_helper(node.left, key)
    else:
       return self.search_helper(node.right, key)
  def insert(self, value):
    if self.root is None:
      self.root = FreqNode(value)
    else:
      self.insert_helper(self.root, value)
    self.totalCount += 1
  def insert_helper(self, node, value):
    #assumes node is FreqNode type
    if node is None:
      node = FreqNode(value)
      #should not come across None
      print "ERROR insert_helper on None type"
    elif node.value == value:
      #update node's count
      node.count += 1
    elif node.value > value:
      #go left
      if node.left is not None:
        self.insert_helper(node.left, value)
      else:
        node.left = FreqNode(value)
    else:
      #go right
      if node.right is not None:
        self.insert_helper(node.right, value)
      else:
        node.right = FreqNode(value)
  def inOrderDFS(self, fun):
    if self.root is not None:
      self.inOrderDFS_helper(self.root, fun)
  def inOrderDFS_helper(self, node, fun):
    if node is None:
      print "ERROR inOrderDFS_helper on None type"
    else:
      #go left
      if node.left is not None:
        self.inOrderDFS_helper(node.left, fun)
      #do itself
      fun(node)
      #go right
      if node.right is not None:
        self.inOrderDFS_helper(node.right, fun)

#@param tweets: fp ito file of tweets
#fills tree with unique words from tweetfile of certain structure
#dependent on freqTree() structure
def fillFreqTree(tweetfile):
  tree = FreqTree()
  totalNumWords = 0
  for tweet_line in tweetfile:
    tweet_bundle = json.loads(tweet_line)
    if "statuses" in tweet_bundle:
      for status in tweet_bundle["statuses"]:
        if ("text" in status):
          text = status["text"]
          text = re.sub('\.+|\!+',' ', text)
          text = re.sub('\n|"|,', ' ', text)
          text = re.sub(' +', ' ', text)
          text.strip()
	  tokens = [x for x in text.split(' ') if x != '' and x != '"' and x != '!' ] #split text into tokens
          for t in tokens: 
            totalNumWords += 1
            tree.insert(t) #either insert or update
    elif "text" in tweet_bundle:
      text = tweet_bundle["text"] #.replace('!','').replace(',','').replace('\n','')
      text = re.sub('\.+|\.!+',' ', text)
      text = re.sub('\n|"|,', ' ', text)
      text = re.sub(' +',' ',text)
      text.strip()
      tokens = [x for x in text.split(' ')  if x != '' and x != '"' and x != '!' ]
      for t in tokens:
        totalNumWords += 1
        tree.insert(t) #either insert or update
  return tree

def printOutput(tree, output_fp):
  tree.inOrderDFS(lambda node: output_fp.write("{0} {1}\n".format(node.value.encode('utf-8').strip(), float(node.count)/tree.totalCount)))



def main():
  tweets = open(sys.argv[1])
  resultFile = open(sys.argv[2], 'w')
  resultFile.truncate
  tree = fillFreqTree(tweets)
  printOutput(tree, resultFile)  

if __name__ == '__main__':
    main()

