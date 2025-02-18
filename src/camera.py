from collections import deque
import cv2
import time

class Camera():
    def __init__(self, logger, stack_size, interval):
        super(Camera, self).__init__()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam (index 0).")
        self.stack_size = stack_size
        self.interval = interval
        self.logger = logger
        self.reset()
    
    def run(self):
        self.running = True
        self.read_frames()
    
    def reset(self):
        self.frame_stack = deque(maxlen=self.stack_size)
        self.running = False
        self.last_frame = None

    def show_feed(self, frame):
        if frame is not None:
            cv2.imshow("Camera", frame)
    
    def read_frames(self):
        last_added_time = time.perf_counter()
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cleanup()
                self.logger.error("Failed to grab frame")
                break

            current_time = time.perf_counter()
            if current_time - last_added_time >= self.interval:
                self.frame_stack.append(frame)
                self.last_frame = frame
                last_added_time = current_time

            self.show_feed(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()