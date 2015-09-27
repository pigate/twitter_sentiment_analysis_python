import json


def munge(line):
"""
given line (json of tweet),
extract tuple ( tweet, location, words) 
criteria for words: exists in tweet, length >= 3, contains only alphas. map to lowercase.
"""  


