import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import time
from collections import deque

class NoseTracker:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        self.screen_w, self.screen_h = pyautogui.size()

        self.running = False
        self.paused = False
        self.thread = None

        self.smoothing_factor = 0.6
        self.mouse_speed = 2.0
        self.click_threshold = 0.015
        self.click_counter = 0

        self.nose_index = 4
        self.mouth_index = 13
        self.base_nose_pos = None
        self.calibrated = False
        self.pos_history = deque(maxlen=3)

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("Tracking started.")

    def stop(self):
        self.running = False
        self.paused = False
        print("Tracking stopped.")

    def pause(self):
        self.paused = True
        print("Tracking paused.")

    def resume(self):
        self.paused = False
        print("Tracking resumed.")

    def _run(self):
        while self.running:
            if self.paused:
                time.sleep(0.05)
                continue

            ret, frame = self.cam.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                nose = landmarks[self.nose_index]
                mouth = landmarks[self.mouth_index]

                frame_h, frame_w = frame.shape[:2]
                nose_x = int(nose.x * frame_w)
                nose_y = int(nose.y * frame_h)
                mouth_x = int(mouth.x * frame_w)
                mouth_y = int(mouth.y * frame_h)

                if not self.calibrated:
                    self.base_nose_pos = (nose.x, nose.y)
                    self.calibrated = True
                    print("Calibration complete.")
                    continue

                rel_x = (nose.x - self.base_nose_pos[0]) * self.mouse_speed
                rel_y = (nose.y - self.base_nose_pos[1]) * self.mouse_speed

                screen_x = np.interp(rel_x, [-0.3, 0.3], [0, self.screen_w])
                screen_y = np.interp(rel_y, [-0.3, 0.3], [0, self.screen_h])


                if self.pos_history:
                    last_x, last_y = self.pos_history[-1]
                    smooth_x = last_x * self.smoothing_factor + screen_x * (1 - self.smoothing_factor)
                    smooth_y = last_y * self.smoothing_factor + screen_y * (1 - self.smoothing_factor)
                else:
                    smooth_x, smooth_y = screen_x, screen_y

                self.pos_history.append((smooth_x, smooth_y))

                pyautogui.moveTo(smooth_x, smooth_y, _pause=False)

                mouth_dist = np.hypot(mouth_x - nose_x, mouth_y - nose_y) / frame_w
                if mouth_dist < self.click_threshold:
                    self.click_counter += 1
                    if self.click_counter > 5:
                        pyautogui.click()
                        self.click_counter = 0
                else:
                    self.click_counter = 0

                cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)
                cv2.circle(frame, (mouth_x, mouth_y), 5, (0, 0, 255), -1)

            cv2.imshow("SightSync", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()

        self.cam.release()
        cv2.destroyAllWindows()
