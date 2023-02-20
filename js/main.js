const roomID = 1234;
const janusUrl = 'http://localhost:8088/janus';
const janusPlugin = 'janus.plugin.videoroom';
const containerName = "container";

var sessionUrl = null;
var subsriberID = null;
var handlerID = null;
var peers = {};


function getPluginHandler(pluginUrl) {
  let tokens = pluginUrl.split('/');

  if (pluginUrl.substr(-1) != '/')
    return tokens[tokens.length-1];
  else
    return tokens[tokens.length-2];
}


async function startJanusEventHandler() {

  for (const [publisherID, info] of Object.entries(peers)) {

    let pluginID = info.pluginID;
    let pluginQueue = getPluginQueue(pluginID);

    // Handle Video Room Plugin Events
    if (pluginQueue.length) {
      let event = pluginQueue.shift();

      // Handle Leaving Event
      if ('leaving' in event.plugindata.data) {
        console.log("Publisher leaving");
      } else if ('publishers' in event.plugindata.data) {
        console.log("New publishers");
      }
    }
  }

}

async function main() {

  // Establish connection to Janus Gateway Video Room Pluin
  sessionUrl = await createJanusSession(janusUrl);
  let pluginUrl = await attachJanusPlugin(sessionUrl, janusPlugin);

  // Start event subscriber to keep fetching plugin event data
  subsriberID = setInterval(startJanusEventSubscriber, 1000, sessionUrl);

  // Start event handler to process event data stored in event queues
  handlerID = setInterval(startJanusEventHandler, 500);

  // Join the Video Room of ID 1234
  const data = {
    body: {
      display: 'browser',
      request: 'join',
      ptype: 'publisher',
      room: roomID
    }
  };
  const response = await sendPluginMessage(pluginUrl, data);

  // Show all the current joined attendee
  const container = document.getElementById(`#${containerName}`);
  const publishers = response.plugindata.data.publishers;
  for (let i = 0; i < publishers.length; i++) {
    pub = publishers[i];

    // Create media component for the publisher
    let component = createMediaComponent(pub.id, pub.display);
    container.appendChild(component);

    // Create plugin handler for each publisher
    let pluginUrl = await attachJanusPlugin(sessionUrl, janusPlugin);
    let pluginID = getPluginHandler(pluginUrl);

    // Establish peer connection to the publisher
    let pc = await createMediaPeer(pluginUrl, media, roomID, pub.id);

    // Save the publisher information in targets object
    peers[pub.id] = {
      display: pub.display,
      component: component,
      pluginID: pluginID,
      pc: pc
    };
  }
}

main();
