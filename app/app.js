var http = require('http');
var express = require('express');
var bodyParser = require('body-parser');
var redis = require('redis');
var express = require('express');
var app = express();
app.use(express.static('public'));
var http = require('http'),
//mongoose = require('mongoose'),
twitter = require('ntwitter'); //,
//routes = require('./routes'),
//config = require('./config'),
//streamHandler = require('./utils/streamHandler');

var count = 0;
var port = process.env.PORT || 8080;

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
  res.render('index', { title: 'Hi' });
  //res.send('Hello. Showing stats... database tweet count: ' + count);
});

var server = app.listen(80, function(){
  var host = server.address().address;
  var port = server.address().port;
});

var io = require('socket.io').listen(server);

