var janusQueue = [];

function random_trans_id(){
  // declare all characters
  const characters ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;

  // Get 12 random ascii characters
  result = [];
  for ( let i = 0; i < 12; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }

  return result;
}

function joinUrl(base, token) {
  if (base.substr(-1) != '/') {
    url = base + '/';
  } else {
    url = base;
  }
  return url + String(token);
}

async function createSession(janusUrl) {
  msg = {
    'janus': 'create',
    'transaction': random_trans_id(),
  }

  // Create janus session
  response = await fetch(janusUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  data = await response.json();

  // Response Check
  if (data['janus'] != 'success') {
    throw new Error("Fail to create janus session");
  }

  // Return janus session url
  session_id = data['data']['id']
  session_url = joinUrl(janusUrl, session_id);

  return session_url
}

async function attachPlugin(sessionUrl, name) {
  msg = {
    janus: 'attach',
    plugin: name,
    transaction: random_trans_id()
  };

  response = await fetch(sessionUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  data = await response.json();

  if (data['janus'] != 'success') {
    throw new Error("Fail to attach to plugin "+name);
  }

  plugin_id = data['data']['id'];
  plugin_url = joinUrl(sessionUrl, plugin_id);

  return plugin_url;
}

async function sendPluginPOST(pluginUrl, body) {
  msg = {
    janus: 'message',
    transaction: random_trans_id(),
    body: body
  };

  response = await fetch(pluginUrl, {
    method: 'POST',
    body: JSON.stringify(msg)
  });
  data = await response.json();

  if (data['janus'] != 'ack') {
    throw new Error("Plugin does not ack your request");
  }

  janusQueue.push(data);

  return data;
}

async function debugPoll() {
  
