# trytry-webrtc

## Environment
```
- Linux pc 5.4.0-137-generic #154~18.04.1-Ubuntu SMP Tue Jan 10 16:58:20 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux
- ffmpeg 4.3.2
- Python 3.7 (Important for using aiortc)
```

## Setup Environment
- Install Janus webrtc server
```bash
$ ./install.sh
```
- Upgrade ffmpeg
```bash
$ sudo add-apt-repository ppa:jonathonf/ffmpeg-4
$ sudo apt update
$ sudo apt upgrade ffmpeg
```
- Upgrade libavcodec-dev
```bash
$ sudo apt upgrade libavcodec-dev
```
- Install Python packages
```bash
$ python3 -m pip install -r requirements.txt
```

## Video Streaming Example
1. Start the janus webrtc server
```bash
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64 /opt/janus/bin/janus
```
2. WebRTC media publisher
```bash
$ python3 janus.py http://localhost:8088/janus
```
3. WebRTC media subscriber
```bash
$ python3 janus.py http://localhost:8088/janus --record-to test.mp4
```
