import oauth2 as oauth
import urllib2 as urllib
import datetime
import os
import multiprocessing

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
  url = "https://stream.twitter.com/1/statuses/sample.json"
  parameters = []
  response = twitterreq(url, http_method, parameters)
  for line in response:
    outfile.write(line.strip())

def fetch_timed_samples():
  curdatetime = datetime.datetime.now()
  fileName = str(curdatetime.year) + "_" + str(curdatetime.month) + "_" + str(curdatetime.day) + "_" + str(curdatetime.minute) + "_" + str(curdatetime.second) + "_output.txt"

  outfile = open(fileName, "w+")
  p = multiprocessing.Process(target=fetchsamples, args=(outfile,))
  p.start()

  p.join(10)
  if p.is_alive():
    p.terminate()
    p.join()

  outfile.close()

if __name__ == '__main__':
  fetch_timed_samples()
