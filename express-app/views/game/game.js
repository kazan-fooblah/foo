// constants

window.ball = null;
window.rocker = null;
window.rockerWidth = 400;
window.rockerHeight = 20;
window.rendererWidth = 1280;
window.rendererHeight = window.innerHeight;
window.meshNodeRadius = 25;
window.meshNodes = [];
window.meshUids = [];
window.meshAnimationStack = [];
window.averageAngle = 0;

// helpers

var socket = io.connect('http://localhost:3000');
socket.on('fuck you pidor', function (nodeData) {
  averageAngle = nodeData.average_angle || 0
  var newMeshUids = [];
  for (var uid in nodeData.angles) {
    var uidIndex = meshUids.indexOf(uid);
    if (uidIndex != -1) {
      updateAngle(uid, nodeData.angles[uid]);
      meshUids.splice(uidIndex, 1);
    } else {
      addNode(uid, {
        color: '#' + c() + c() + c()
      });
      updateAngle(uid, nodeData.angles[uid]);
    }
    newMeshUids.push(uid);
  }

  for (var deadUid of meshUids) {
    removeNode(deadUid);
  }

  meshUids = newMeshUids;
  // countAngleAverage();
});

function c() {
  return Math.floor(50 + Math.random() * 150).toString(16)
}

function updateAngle(uid, angle) {
  getMeshNode(uid).node.state.angular.pos = angle;
}

function getMeshNode(uid) {
  var i = 0;
  for (var meshNode of meshNodes) {
    if (meshNode.uid == uid) {
      return {
        node: meshNode.node,
        uid: uid,
        index: i
      };
    }
    i++;
  }
  return null;
}

function moveWithAnimation(uid, x) {
  meshAnimationStack.push({
    uid: uid,
    x: x
  });
}

function countAngleAverage() {
  var sum = 0;
  for (var meshNode of meshNodes) {
    sum += meshNode.node.state.angular.pos;
  }
  averageAngle = meshNodes.length > 0 ? (sum / meshNodes.length) : 0;
}

function moveNodesLeft(fromIndex) {
  for (var i = fromIndex; i < meshNodes.length; i++) {
    var meshNode = meshNodes[i];
    // moveWithAnimation(meshNode.uid, meshNode.node.state.pos._[0] - meshNodeRadius * 2 * 1.2);
    meshNode.node.state.pos._[0] -= meshNodeRadius * 2 * 1.2;
  }
}

function removeNode (uid) {
  for (var i = 0; i < meshNodes.length; i++) {
    var meshNode = meshNodes[i];
    if (meshNode.uid == uid) {
      moveNodesLeft(i+1);
      meshNodes.splice(i, 1);
      world.remove(meshNode.node);
    }
  }
}

function addNode(uid, options) {
  var index = meshNodes.length;

  var node = Physics.body('circle', {
    x: 35 + index * meshNodeRadius * 2 * 1.2,
    y: 35,
    radius: meshNodeRadius,
    mass: 1,
    treatment: 'static',
    styles: {
      fillStyle: options.color || '#fff',
      angleIndicator: 'black'
    }
  });

  world.add(node);
  meshNodes.push({
    uid: uid,
    node: node
  });
}

// main scene

Physics(function (world) {
  window.world = world;ball, rocker
  var viewportBounds = Physics.aabb(0, 0, rendererWidth, rendererHeight), edgeBounce, renderer;

  renderer = Physics.renderer('canvas', {
    el: 'viewport',
    width: rendererWidth,
    height: rendererHeight
  });

  world.on('step', function () {
    world.render();
    rocker.state.angular.pos += (averageAngle - rocker.state.angular.pos) / 2;

    var animationIndex = 0;
    for (var animationData of meshAnimationStack) {
      var meshNode = getMeshNode(animationData.uid);
      // meshNode.node.state.pos._[0] += (animationData.x - meshNode.node.state.pos._[0]) / 2;
      meshNode.node.state.pos._[0] = animationData.x;
      if (Math.abs(animationData.x - meshNode.node.state.pos._[0]) < 5) {
        meshNode.node.state.pos._[0] = animationData.x;
        meshAnimationStack.splice(animationIndex, 1);
      } else {
        animationIndex++;
      }
    }
  });

  world.on('collisions:detected', function( data ){
    var c;
    for (var i = 0, l = data.collisions.length; i < l; i++){
      c = data.collisions[ i ];
      if (c.bodyB.uid == 1) {
        var x = 650, y = 100;
        ball.state.pos._ = [x, y];
        ball.state.vel._ = [0, 0, 0, 0, 0];
      }
    }
  });

  // subscribe to ticker to advance the simulation
  Physics.util.ticker.on(function(time) {
    world.step(time);
  });

  window.addEventListener('resize', function () {
    viewportBounds = Physics.aabb(0, 0, renderer.width, renderer.height);
    edgeBounce.setAABB(viewportBounds);
  }, true);

  edgeBounce = Physics.behavior('edge-collision-detection', {
    aabb: viewportBounds,
    restitution: 0.99,
    cof: 0.8
  });

  ball = Physics.body('circle', {
    x: 500,
    y: 100,
    radius: 40,
    mass: 5,
    restitution: 0.1,
    styles: {
      fillStyle: '#eee'
    }
  });

  rocker = Physics.body('rectangle', {
    x: 650,
    y: 450,
    width: rockerWidth,
    height: rockerHeight,
    treatment: 'static',
    styles: {
      fillStyle: '#80C77C'
    }
  });

  world.add(renderer);
  world.add(rocker);
  world.add(ball);
  world.add([
    Physics.behavior('constant-acceleration'),
    Physics.behavior('body-impulse-response'),
    Physics.behavior('body-collision-detection'),
    Physics.behavior('sweep-prune'),
    edgeBounce
  ]);
});
