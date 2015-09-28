var http = require('http');
var express = require('express');
var bodyParser = require('body-parser');
var app = express();
var redis = require('redis');

var count = 0;

var client = redis.createClient();
client.on('connect', function(){
  console.log('redis- connected');
});
client.keys("*", function(err, replies){
  console.log("MULTI got " + replies.length + " replies");
  count = replies.length;
  replies.forEach(function(reply, index){
    console.log("reply " + index + ": " + reply);
  });
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
  extended: true
}));

app.get('/', function(req, res){
  res.send('Hello. Showing stats... database tweet count: ' + count);
});

var server = app.listen(80, function(){
  var host = server.address().address;
  var port = server.address().port;
});



