var express = require('express'),
    dgram = require('dgram');

var app = module.exports = express.createServer();

var io = require('socket.io')(app);

// Configuration

// var PORT = 5670;
// var HOST = '0.0.0.0';
// var client = dgram.createSocket('udp4');
//
// client.on('listening', function () {
//     var address = client.address();
//     console.log('UDP Client listening on ' + address.address + ":" + address.port);
//     client.setBroadcast(true);
//     client.setMulticastTTL(128);
//     client.addMembership('224.0.0.1');
// });
//
// client.on('message', function (message, remote) {
//     receivedMessage = message;
//     console.log(JSON.parse(message));
// });
//
// client.bind(PORT, HOST);

var nodes = function() {
  function c() {
    return Math.floor(50 + Math.random() * 150).toString(16)
  }

  var result = {
    'Kostya': {
      angle: Math.random() * 2 - 1,
      color: '#' + c() + c() + c()
    },
    'Sergey': {
      angle: Math.random() * 2 - 1,
      color: '#' + c() + c() + c()
    },
    'Almir': {
      angle: Math.random() * 2 - 1,
      color: '#' + c() + c() + c()
    }
  };

  if ((Math.random() * 10) > 3) {
    result[Math.random().toString()] = {
      angle: Math.random() * 2 - 1,
      color: '#' + c() + c() + c()
    }
  }

  return result;
}

var socket2 = null;

io.on('connection', function (socket) {
  socket2 = socket;
  //setInterval(function () {
  //  socket.emit('fuck you pidor', nodes());
  //}, 1000);
});

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(express.static(__dirname + '/views/game/'));
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function(){
  app.use(express.errorHandler());
});

app.post("/endpoint", function (req, res) {
  res.status(200).send({status: 200});
  console.log(req.body);
  if (socket2 != null) socket2.emit('fuck you pidor', req.body);
});

app.listen(3000, function(){
  console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
});
