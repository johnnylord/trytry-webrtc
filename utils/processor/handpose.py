import sys
import traceback
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

import asyncio
from av import VideoFrame

from aiortc import VideoStreamTrack


class HandPoseStreamTrack(VideoStreamTrack):

    def __init__(self, track, *args, **kwargs):
        self.track = track
        self.hand_pose = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        super().__init__(*args, **kwargs)

    async def recv(self):
        frame = await self.track.recv()

        try:
            # Convert VideoFrame to numpy array
            img = frame.to_ndarray(format="bgr24")

            # Detect Face
            results = self.hand_pose.process(img)
            if not results.multi_hand_landmarks:
                return frame

            # Draw face detections of each face.
            annotated_image = img.copy()
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

            new_frame = VideoFrame.from_ndarray(annotated_image, format='bgr24')
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base

            return new_frame

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return frame
