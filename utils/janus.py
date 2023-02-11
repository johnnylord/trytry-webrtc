import os
import os.path as osp
import string
import random

import asyncio
import aiohttp
import aiortc

from aiortc.contrib.media import MediaRelay
from aiortc import RTCPeerConnection

def random_trans_id():
    return "".join(random.choice(string.ascii_letters) for x in range(12))

class JanusPlugin:

    def __init__(self, session, url):
        self._queue = asyncio.Queue()
        self._session = session
        self._url = url

    async def send(self, payload):
        msg = { 'janus': 'message', 'transaction': random_trans_id() }
        msg.update(payload)
        async with self._session._http.post(self._url, json=msg) as response:
            data = await response.json()
            assert data['janus'] == 'ack'
        # Wait for the asynchronized response. The polling task in the session
        # will put the response in the queue of the plugin.
        response = await self._queue.get()
        assert response['transaction'] == msg['transaction']
        return response


class JanusSession:

    def __init__(self, url):
        # Janus Information
        self._url = url
        self._http = aiohttp.ClientSession()
        self._session_url = None
        self._poll_task = None
        self._plugins = {}
        # AIORTC Information
        self._pcs = {}
        self._relays = {}
        self._tracks = {}

    def createRTCPeerConnection(self, name):
        pc = RTCPeerConnection()
        self._pcs[name] = pc
        return pc

    def getRTCPeerConnection(self, name):
        return self._pcs.get(name, None)

    def createMediaRelay(self, name):
        relay = MediaRelay()
        self._relays[name] = relay
        return relay

    def getMediaRelay(self, name):
        return self._relays.get(name, None)

    def saveTrack(self, name, track):
        self._tracks[name] = track

    def accessTrack(self, name):
        return self._tracks.get(name, None)

    async def attach(self, plugin_name: str) -> JanusPlugin:
        msg = {
            "janus": "attach",
            "plugin": plugin_name,
            "transaction": random_trans_id()
        }
        async with self._http.post(self._session_url, json=msg) as response:
            data = await response.json()
            assert data['janus'] == 'success'
            plugin_id = data['data']['id']
            plugin = JanusPlugin(self, osp.join(self._session_url, str(plugin_id)))
            self._plugins[plugin_id] = plugin
            return plugin

    async def create(self):
        """Get the available session ID to be used"""
        msg = {
            "janus": "create",
            "transaction": random_trans_id()
        }
        async with self._http.post(self._url, json=msg) as response:
            data = await response.json()
            assert data['janus'] == 'success'
            session_id = data['data']['id']
            self._session_url = osp.join(self._url, str(session_id))

        self._poll_task = asyncio.ensure_future(self._poll())

    async def destroy(self):
        if self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

        if self._session_url:
            msg = { 'janus': 'destroy', 'transaction': random_trans_id() }
            async with self._http.post(self._session_url, json=msg) as response:
                data = await response.json()
                assert data['janus'] == 'success'
            self._session_url = None

        if self._http:
            await self._http.close()
            self._http = None

        for name, pc in self._pcs.items():
            await pc.close()

    async def _poll(self):
        while True:
            params = { "maxev": 1 }
            async with self._http.get(self._session_url, params=params) as response:
                data = await response.json()
                if data['janus'] == 'event':
                    plugin = self._plugins.get(data['sender'], None)
                    if plugin:
                        await plugin._queue.put(data)
