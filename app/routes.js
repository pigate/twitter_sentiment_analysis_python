var JSX = require('node-jsx').install(),
  React = require('react'),
  TweetsApp = require('./components/TweetsApp.react'),
  Tweet = require('./models/Tweet');

module.exports = {
  index: function(req, res){
    Tweet.getTweets(0, 0, function(tweets, pages){
      var markup = React.renderComponentToString(
        TweetsApp({
          tweets: tweets
        })
      );
      // Render our 'home' template
      res.render('home', {
            markup: markup, // Pass rendered react markup
            state: JSON.stringify(tweets) // Pass current state to client side
      });

    });
  },

  page: function(req, res) {
    // Fetch tweets by page via param
    Tweet.getTweets(req.params.page, req.params.skip, function(tweets) {

      // Render as JSON
      res.send(tweets);

    });
  }
}
