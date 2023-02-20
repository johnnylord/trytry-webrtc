// Global variables
var eventQueue = [];
var pluginQueues = {};
var pluginID2Name = {};

// Exported functions
function getPluginQueue(name) {
  return pluginQueues[name];
}

function getPluginName(id) {
  return pluginID2Name[id];
}

// Helper functions
function _janus_msleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function _janus_random_trans_id(){
  const chars ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  let result = [];
  for ( let i = 0; i < 12; i++ ) {
    result += chars.charAt(
      Math.floor(Math.random() * chars.length)
    );
  }

  return result;
}

function _janus_join_url(base, token) {
  if (base.substr(-1) != '/')
    let url = base + '/';
  else
    let url = base;

  return url + String(token);
}

function _janus_join_url_params(base, params) {
  if (base.substr(-1) != '/')
    let url = base + '/';
  else
    let url = base;

  let count = 0;
  for (const [key, value] of Object.entries(params)) {
    if (count == 0)
      url += `?${key}=${value}`;
    else
      url += `&${key}=${value}`;
    count += 1;

  return url;
}

// Exported Asynchronized Functions
async function createJanusSession(janusUrl) {
  const msg = {
    'janus': 'create',
    'transaction': _janus_random_trans_id(),
  }

  // Create janus session handle
  let response = await fetch(janusUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  let data = await response.json();

  // Response Check
  if (data['janus'] != 'success') {
    throw new Error("Fail to create janus session");
  }

  // Return janus session url
  const sessionID = data['data']['id']
  const sessionUrl = _janus_join_url(janusUrl, sessionID);

  return sessionUrl
}

async function attachJanusPlugin(sessionUrl, pluginName) {
  const msg = {
    janus: 'attach',
    plugin: pluginName,
    transaction: _janus_random_trans_id()
  };

  // Craet janus plugin handle
  let response = await fetch(sessionUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  let data = await response.json();

  // Response Check
  if (data['janus'] != 'success') {
    throw new Error("Fail to attach to plugin "+pluginName);
  }

  // Extract plugin handle
  const pluginID = data['data']['id'];
  const pluginUrl = _janus_join_url(sessionUrl, pluginID);

  // Create dedicated event queue for each plugin handle
  pluginQueues[pluginID] = [];
  pluginID2Name[pluginID] = pluginName;

  return pluginUrl;
}

async function sendPluginMessage(pluginUrl, data) {
  let msg = {
    janus: 'message',
    transaction: _janus_random_trans_id(),
  };

  // Update message with plugin specific data
  for (const [key, value] of Object.entries(data)) {
    msg[key] = value;

  // Send Message to specified plugin handle
  let response = await fetch(pluginUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  let data = await response.json();

  // Response check
  if (data['janus'] != 'ack') {
    throw new Error("Plugin does not ack your request");
  }

  // Wait for polled event data matched with the requested transaction ID
  let elapsed = 0;
  while (elapsed < 500) {
    // Check for recently got event data
    let event = eventQueue.shift();
    if (
      'transaction' in event
      && event.transaction == msg.transaction
    )
      return event;

    // Push back the event data into the event queue
    eventQueue.push(event);
    await _janus_msleep(100);
    elapsed += 100;
  }

  throw new Error("Fail to get responed event data within 500 msec");
}

async function janusEventSubscriber(sessionUrl) {

  const params = { maxev: '1' };
  const pollUrl = _janus_join_url_params(sessionUrl, params);

  response = await fetch(pollUrl, { method: 'GET' });
  data = await response.json();

  if (data['janus'] == 'event') {
    if (data['sender'] in pluginQueues) {
      queue = pluginQueues[String(data['sender'])];
      queue.push(data);
      eventQueue.push(data);
    }
  }

}


async function createMediaClient(pluginUrl, media) {
  const config = {
    sdpSemantics: 'unified-plan',
    iceServers: [{urls: ['stun:stun.l.google.com:19302']}]
  };

  let pc = new RTCPeerConnection(config);

  // Attach event listener for available tracks (audio/video)
  pc.addEventListener('track', function(evt) {
    if (evt.track.kind == 'video') {
      console.log(evt);
      let video = document.getElementById(`${media.id}_video`);
      console.log(video);
      video.srcObject = evt.streams[0];
    } else {
      console.log(evt);
      let audio = document.getElementById(`${media.id}_audio`);
      audio.srcObject = evt.streams[0];
    }
  });

  pc.addTransceiver('video', {direction: 'recvonly'});
  pc.addTransceiver('audio', {direction: 'recvonly'});

  // Request for SDP information of the publisher (feed)
  body = {
    ptype: 'subscriber',
    request: 'join',
    room: roomID,
    feed: pub.id,
  };
  data = await sendPluginMessage(pluginUrl, body);
  description = new RTCSessionDescription(data['jsep']);

  await pc.setRemoteDescription(description);
  await pc.setLocalDescription(await pc.createAnswer())

  console.log(pc.localDescription);
  body = { request: 'start' }
  jsep = { sdp: pc.localDescription.sdp, type: pc.localDescription.type };
  data = await sendPluginMessage(pluginUrl, body, jsep);

  console.log(data);
}

function createMediaComponent(id, name) {
  let div = document.createElement('div');
  div.setAttribute('id', id);

  let h2 = document.createElement('h2');
  h2.setAttribute('id', `${id}_name`);
  h2.innerHTML = name;

  let audio = document.createElement('audio');
  audio.setAttribute('id', `${id}_audio`);
  audio.setAttribute('autoplay', 'true');

  let video = document.createElement('video');
  video.setAttribute('id', `${id}_video`);
  video.setAttribute('autoplay', 'true');
  video.setAttribute('playsinline', 'true');

  div.appendChild(h2);
  div.appendChild(audio);
  div.appendChild(video);

  return div;
}
