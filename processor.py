import os
import os.path as osp
import asyncio
import argparse

from aiortc import RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole

from utils.processor import get_processor_by_name, get_processer_names
from utils.janus import JanusSession


async def subscribe(session, room, feed, processor):
    pc = session.createRTCPeerConnection('subscriber')
    video_relay = session.createMediaRelay('video')
    audio_relay = session.createMediaRelay('audio')

    @pc.on("track")
    async def on_track(track):
        if track.kind == 'video':
            video_track = video_relay.subscribe(processor(track))
            session.saveTrack('video', video_track)
        if track.kind == 'audio':
            audio_track = audio_relay.subscribe(track)
            session.saveTrack('audio', audio_track)

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


async def publish(session, plugin):
    pc = session.createRTCPeerConnection('publisher')

    video_track = session.accessTrack('video')
    if video_track:
        pc.addTrack(video_track)

    audio_track = session.accessTrack('audio')
    if audio_track:
        pc.addTrack(audio_track)

    await pc.setLocalDescription(await pc.createOffer())
    request = {
        "request": "configure",
        "audio": False,
        "video": True,
    }
    response = await plugin.send(
        {
            "body": request,
            "jsep": {
                "sdp": pc.localDescription.sdp,
                "trickle": False,
                "type": pc.localDescription.type,
            }
        }
    )

    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=response['jsep']['sdp'], type=response['jsep']['type']
        )
    )


async def main(session, room, name):
    # Create session endpoint at janus side and keep polling the session state
    await session.create()

    # Attach the videroom plugin to the session so that any event generated
    # from the plugin can be polled in the session
    plugin = await session.attach('janus.plugin.videoroom')

    # Join the room with provided user name
    response = await plugin.send(
        {
            'body': {
                'display': name,
                'ptype': 'publisher',
                'request': 'join',
                'room': room,
            }
        }
    )

    # Show active publishers (performing streaming)
    publishers = response['plugindata']['data']['publishers']
    print("Active publishers in the room:")
    for pub in publishers:
        print("- id: %(id)s, display: %(display)s" % pub)

    processor = get_processor_by_name(name)
    await subscribe(
        room=room,
        session=session,
        processor=processor,
        feed=publishers[0]['id'],
    )

    await publish(session, plugin)

    while True:
        await asyncio.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="janus subscriber")
    parser.add_argument("--url", help="url of janus http server, e.g. http://localhost:8088/janus")
    parser.add_argument("--name", type=str, choices=get_processer_names(), default='facedet', help="name of processor")
    parser.add_argument("--room", type=int, default=1234, help="ID of video room to join")
    args = vars(parser.parse_args())

    session = JanusSession(args['url'])
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            main(
                session=session,
                room=args['room'],
                name=args['name'],
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(session.destroy())
