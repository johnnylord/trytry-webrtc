import cv2
import mediapipe as mp
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

import asyncio
from av import VideoFrame

from aiortc import VideoStreamTrack


class FaceDetStreamTrack(VideoStreamTrack):

    def __init__(self, track, *args, **kwargs):
        self.track = track
        self.face_detection = mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        super().__init__(*args, **kwargs)

    async def recv(self):
        frame = await self.track.recv()

        # Convert VideoFrame to numpy array
        img = frame.to_ndarray(format="bgr24")

        # Detect Face
        results = self.face_detection.process(img)
        if not results.detections:
            return frame

        # Draw face detections of each face.
        annotated_image = img.copy()
        for detection in results.detections:
            mp_drawing.draw_detection(annotated_image, detection)

        new_frame = VideoFrame.from_ndarray(annotated_image, format='bgr24')
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame
