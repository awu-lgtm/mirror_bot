import cv2
from collections import deque
import threading
from openai import OpenAI
import time
import base64
import numpy as np
from PIL import Image
import math
import logging
import logging.config
from uuid import uuid4
from prompts import prompt_with_history
import os

# comment out if you want logs from external dependencies
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
    }
)
logger = logging.getLogger("webcam")

# Initialize the webcam
cap = cv2.VideoCapture(0)
episode_id = uuid4()
episode_path = f"./episodes/episode_{episode_id}"
if not os.path.isdir(episode_path):
    os.mkdir(episode_path)
logging.basicConfig(
    filename=f"{episode_path}/logfile.txt", filemode="w", level=logging.DEBUG
)
logger.info(episode_path)
print(episode_path)

stack_size = 10
time_per_stack = 2
interval = time_per_stack / stack_size
frame_stack = deque(maxlen=stack_size)  # Set a maximum length for buffer
prompt = f"This is a frame stack of the last {stack_size} frames in a video. Do those two people have intention to initiate a conversation?"

client = OpenAI(
    api_key="***REMOVED***"
)
processing = True


def create_prompt(history, image_path):
    prompt = prompt_with_history(stack_size)
    messages = [
        {"role": "system", "content": prompt["system"]},
    ]
    messages = [{"role": "assistant", "content": prompt["examples"]}]
    messages += history
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt["user"],
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(image_path)}",
                        "detail": "high",
                    },
                },
            ],
        },
    )
    # messages[-1]["content"] += [
    #     {
    #         "type": "image_url",
    #         "image_url": {
    #             "url": f"data:image/png;base64,{encode_image(image_path)}",
    #             "detail": "high",
    #         },
    #     }
    # ]
    return messages


def log_prompt(prompt, image_path):
    temp = prompt[-1]["content"][-1]["image_url"]["url"]
    prompt[-1]["content"][-1]["image_url"]["url"] = image_path
    logger.info(prompt)
    prompt[-1]["content"][-1]["image_url"]["url"] = temp


def call_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        max_tokens=10000,
        temperature=1.0,
        top_p=1.0,
    )
    return response.choices[0].message


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def stack_frames(frames):
    # Resize and stack frames horizontally
    # resized_frames = [cv2.resize(frame, (200, 150)) for frame in frames]
    stacked_image = np.hstack(frames)
    return Image.fromarray(cv2.cvtColor(stacked_image, cv2.COLOR_BGR2RGB))


def process_frames(prompt):
    i = 0
    history = []
    while processing:
        if frame_stack and len(frame_stack) == stack_size:
            stacked_image = stack_frames(frame_stack)
            # Save or display the stacked image if needed (not displayed here)
            image_path = f"{episode_path}/image_stack_{i}.png"
            stacked_image.save(image_path)

            # Prompt GPT with a description
            logger.info("Prompting...")
            prompt = create_prompt(history, image_path)
            log_prompt(prompt, image_path)
            start_time = time.perf_counter()
            gpt_response = call_gpt(prompt)
            end_time = time.perf_counter()
            logger.info(
                f"GPT-4 Response: {gpt_response}, time_elasped: {'%.3f'%(end_time - start_time)}s"
            )
            history.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": gpt_response.content,
                        }
                    ],
                },
            )
            content = gpt_response.content
            lines = content.strip().split("\n")
            print(lines[2])

            i += 1


# Start the frame processing in a separate thread
processing_thread = threading.Thread(target=lambda: process_frames(prompt))
processing_thread.start()

# Capture frames continuously
last_added_time = time.perf_counter()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to grab frame")
        break

    # Store the frame in the buffer
    current_time = time.perf_counter()
    if current_time - last_added_time >= interval:
        # Add the frame to the buffer
        frame_stack.append(frame)
        last_added_time = current_time

    # Display the original frame
    cv2.imshow("Webcam Feed", frame)

    # Check if 'q' is pressed to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        processing = False
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
processing_thread.join()
