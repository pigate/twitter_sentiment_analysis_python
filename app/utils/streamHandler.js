var Tweet = require('../models/Tweet');
module.exports = function(stream, io){
  stream.on('data', function(data){
    var tweet = {
      body: data['text'],
      date: data['created_at'],
      pos: data['pos'],
      neg: data['neg'],
      classification: data['class']
    };

    var tweetEntry = new Tweet(tweet);

    tweetEntry.save(function(err){
      if (!err){
        io.emit('tweet', tweet);
      }
    });
  });
}
