# camera_app.py

import os
import logging
import logging.config
from uuid import uuid4
from camera import Camera
from query_gpt import Prompter
from flask import Flask, jsonify, request
import threading
from flask_cors import CORS

# Configure logging
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
    }
)
logger = logging.getLogger("webcam")

# Create an "episode" folder
episode_id = str(uuid4())
episode_path = f"./episodes/episode_{episode_id}"
os.makedirs(episode_path, exist_ok=True)
logging.basicConfig(
    filename=f"{episode_path}/logfile.txt", filemode="w", level=logging.DEBUG
)
logger.info(f"Episode path: {episode_path}")
print(episode_path)

stack_size = 10
time_per_stack = 2.0  # seconds total to accumulate each stack
interval = time_per_stack / stack_size

app = Flask(__name__)
CORS(app)

@app.route('/analysis', methods=['GET'])
def capture_and_analyze():
    return jsonify(prompter.history[-1])

def run_server():
    app.run(port=5000)

if __name__ == "__main__":
    cam = Camera(logger, stack_size, interval)
    prompter = Prompter(cam, stack_size, logger, episode_path)

    prompter.start()
    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()

    cam.run()
    prompter.running = False
    prompter.join()