import os
import os.path as osp
import asyncio
import argparse

from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaRecorder

from utils.processor import get_processor_by_name
from utils.janus import JanusSession


async def record(session, room, feed, path):
    pc = session.createRTCPeerConnection('subscriber')
    sink = MediaRecorder(path, options={ 'fflags': 'nobuffer'})

    @pc.on("track")
    async def on_track(track):
        if track.kind == 'video':
            sink.addTrack(track)
        if track.kind == 'audio':
            sink.addTrack(track)

    plugin = await session.attach('janus.plugin.videoroom')
    response = await plugin.send(
        {
            'body': {
                'ptype': 'subscriber',
                'request': 'join',
                'room': room,
                'feed': feed,
            }
        }
    )

    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=response['jsep']['sdp'], type=response['jsep']['type']
        )
    )

    await pc.setLocalDescription(await pc.createAnswer())
    response = await plugin.send(
        {
            "body": { "request": "start" },
            "jsep": {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
                "trickle": False,
            },
        }
    )
    await sink.start()


async def main(session, room):
    # Create session endpoint at janus side and keep polling the session state
    await session.create()

    # Attach the videroom plugin to the session so that any event generated
    # from the plugin can be polled in the session
    plugin = await session.attach('janus.plugin.videoroom')

    # Join the room with provided user name
    response = await plugin.send(
        {
            'body': {
                'display': 'recorder',
                'ptype': 'publisher',
                'request': 'join',
                'room': room,
            }
        }
    )

    # Record active published streams
    publishers = response['plugindata']['data']['publishers']

    tasks = []
    for pub in publishers:
        print("- Recording stream %(display)s.mp4" % pub)
        task = asyncio.ensure_future(
            record(
                room=room,
                session=session,
                feed=pub['id'],
                path=pub['display']+'.mp4'
            )
        )
    tasks.append(task)

    while True:
        await asyncio.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="janus subscriber")
    parser.add_argument("--url", help="url of janus http server, e.g. http://localhost:8088/janus")
    parser.add_argument("--room", type=int, default=1234, help="ID of video room to join")
    args = vars(parser.parse_args())

    session = JanusSession(args['url'])
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            main(
                session=session,
                room=args['room'],
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(session.destroy())
