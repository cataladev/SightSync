import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Open the webcam (add cv2.CAP_DSHOW if needed on Windows)
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Webcam could not be opened.")
    exit()

# Initialize Mediapipe Face Mesh with iris refinement enabled.
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
screen_w, screen_h = pyautogui.size()

# Gain factor to amplify cursor movement.
gain = 1.5

while True:
    ret, frame = cam.read()
    if not ret:
        break

    # Flip frame horizontally for a mirror-like view.
    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape

    # Convert the frame to RGB.
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # We expect 478 landmarks with refine_landmarks=True.
        if len(landmarks) < 478:
            cv2.putText(frame, "Not enough landmarks", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("SightSync", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # For left eye: indices 468 to 472 (5 points)
        left_iris = np.array([[int(landmarks[i].x * frame_w), int(landmarks[i].y * frame_h)]
                                for i in range(468, 473)])
        # For right eye: indices 473 to 477 (5 points)
        right_iris = np.array([[int(landmarks[i].x * frame_w), int(landmarks[i].y * frame_h)]
                                 for i in range(473, 478)])

        # Compute key points for each eye
        def compute_keypoints(points):
            center = np.mean(points, axis=0).astype(int)
            top = points[np.argmin(points[:,1])]
            bottom = points[np.argmax(points[:,1])]
            left = points[np.argmin(points[:,0])]
            right = points[np.argmax(points[:,0])]
            return center, top, bottom, left, right

        left_center, left_top, left_bottom, left_left, left_right = compute_keypoints(left_iris)
        right_center, right_top, right_bottom, right_left, right_right = compute_keypoints(right_iris)

        # Draw key points for left eye (blue for center, yellow for boundaries)
        cv2.circle(frame, tuple(left_center), 3, (255, 0, 0), -1)
        cv2.circle(frame, tuple(left_top), 3, (0, 255, 255), -1)
        cv2.circle(frame, tuple(left_bottom), 3, (0, 255, 255), -1)
        cv2.circle(frame, tuple(left_left), 3, (0, 255, 255), -1)
        cv2.circle(frame, tuple(left_right), 3, (0, 255, 255), -1)

        # Draw key points for right eye (green for center, cyan for boundaries)
        cv2.circle(frame, tuple(right_center), 3, (0, 255, 0), -1)
        cv2.circle(frame, tuple(right_top), 3, (255, 255, 0), -1)
        cv2.circle(frame, tuple(right_bottom), 3, (255, 255, 0), -1)
        cv2.circle(frame, tuple(right_left), 3, (255, 255, 0), -1)
        cv2.circle(frame, tuple(right_right), 3, (255, 255, 0), -1)

        # Combine the two centers for a single gaze point.
        combined_center = ((left_center + right_center) / 2).astype(int)
        cv2.circle(frame, tuple(combined_center), 5, (0, 0, 255), -1)

        # Convert the combined center from frame to screen coordinates.
        raw_screen_x = int(combined_center[0] * screen_w / frame_w)
        raw_screen_y = int(combined_center[1] * screen_h / frame_h)
        # Apply gain factor.
        screen_x = int(np.clip(raw_screen_x * gain, 0, screen_w))
        screen_y = int(np.clip(raw_screen_y * gain, 0, screen_h))

        # Move the cursor.
        pyautogui.moveTo(screen_x, screen_y)

        cv2.putText(frame, f"Screen: ({screen_x}, {screen_y})", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    else:
        cv2.putText(frame, "No face detected", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("SightSync", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
