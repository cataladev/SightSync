import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import time

class NoseTracker:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        self.screen_w, self.screen_h = pyautogui.size()

        self.running = False
        self.paused = False
        self.thread = None

        self.gain = 450
        self.deadzone = 0.002
        self.smooth_factor = 0.23
        self.prev_dx = 0
        self.prev_dy = 0
        self.calibrated = False
        self.calib_dx = 0
        self.calib_dy = 0

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("🎯 Nose tracking started.")

    def stop(self):
        self.running = False
        self.paused = False
        print("🛑 Nose tracking stopped.")

    def pause(self):
        self.paused = True
        print("⏸️ Nose tracking paused.")

    def resume(self):
        self.paused = False
        print("▶️ Nose tracking resumed.")

    def _run(self):
        frames_for_calibration = 30
        dx_samples = []
        dy_samples = []

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

                nose_tip = landmarks[1]
                left_eye = landmarks[33]
                right_eye = landmarks[263]

                eye_center_x = (left_eye.x + right_eye.x) / 2
                eye_center_y = (left_eye.y + right_eye.y) / 2

                dx = nose_tip.x - eye_center_x
                dy = nose_tip.y - eye_center_y

                # First 30 frames → collect for calibration
                if not self.calibrated:
                    dx_samples.append(dx)
                    dy_samples.append(dy)

                    if len(dx_samples) >= frames_for_calibration:
                        self.calib_dx = np.mean(dx_samples)
                        self.calib_dy = np.mean(dy_samples)
                        self.calibrated = True
                        print("✅ Calibration complete.")
                    else:
                        print(f"📐 Calibrating... {len(dx_samples)}/{frames_for_calibration}")
                        continue

                # Subtract calibration baseline
                dx -= self.calib_dx
                dy -= self.calib_dy

                # Deadzone
                if abs(dx) < self.deadzone:
                    dx = 0
                if abs(dy) < self.deadzone:
                    dy = 0

                # Smooth movement
                dx = self.prev_dx + (dx - self.prev_dx) * self.smooth_factor
                dy = self.prev_dy + (dy - self.prev_dy) * self.smooth_factor
                self.prev_dx = dx
                self.prev_dy = dy

                # Convert to screen coordinates
                move_x = int(dx * self.gain)
                move_y = int(dy * self.gain)
                cur_x, cur_y = pyautogui.position()

                new_x = np.clip(cur_x + move_x, 0, self.screen_w)
                new_y = np.clip(cur_y + move_y, 0, self.screen_h)
                pyautogui.moveTo(new_x, new_y)

        self.cam.release()
        cv2.destroyAllWindows()
