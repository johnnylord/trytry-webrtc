from .facedet import FaceDetStreamTrack
from .handpose import HandPoseStreamTrack

_processors = {
    'facedet': FaceDetStreamTrack,
    'handpose': HandPoseStreamTrack,
}

def get_processer_names():
    return list(_processors.keys())

def get_processor_by_name(name):
    return _processors[name]
