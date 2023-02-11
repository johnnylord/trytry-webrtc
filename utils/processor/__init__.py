from .facedet import FaceDetStreamTrack

_processors = {
    'facedet': FaceDetStreamTrack,
}

def get_processor_by_name(name):
    return _processors[name]
