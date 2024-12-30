import cv2
from openai import OpenAI
import threading
import time
import base64
import numpy as np
from PIL import Image
from prompts import prompt_with_history

class Prompter(threading.Thread):
    def __init__(self, cam, stack_size, logger, episode_path):
        super(Prompter, self).__init__()
        self.logger = logger
        self.stack_size = stack_size
        self.history = []
        self.episode_path = episode_path
        self.client = OpenAI(
            api_key="***REMOVED***"
        )
        self.running = False
        self.cam = cam
    
    def run(self):
        self.running = True
        self.query_gpt(self.cam)

    def create_prompt(self, image_path):
        prompt = prompt_with_history(self.stack_size)
        messages = [
            {"role": "system", "content": prompt["system"]},
        ]
        # messages += [{"role": "assistant", "content": prompt["examples"]}]
        messages += self.history
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
                            "url": f"data:image/png;base64,{self.encode_image(image_path)}",
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


    def log_prompt(self, prompt, image_path):
        temp = prompt[-1]["content"][-1]["image_url"]["url"]
        prompt[-1]["content"][-1]["image_url"]["url"] = image_path
        self.logger.info(prompt)
        prompt[-1]["content"][-1]["image_url"]["url"] = temp


    def call_gpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=prompt,
            max_tokens=10000,
            temperature=1.0,
            top_p=1.0,
        )
        return response.choices[0].message


    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    def stack_frames(self, frames):
        # Resize and stack frames horizontally
        # resized_frames = [cv2.resize(frame, (200, 150)) for frame in frames]
        stacked_image = np.hstack(frames)
        return Image.fromarray(cv2.cvtColor(stacked_image, cv2.COLOR_BGR2RGB))

    def query_gpt_once(self, frame_stack, i):
        if frame_stack and len(frame_stack) == self.stack_size:
            stacked_image = self.stack_frames(frame_stack)
            # Save or display the stacked image if needed (not displayed here)
            image_path = f"{self.episode_path}/image_stack_{i}.png"
            stacked_image.save(image_path)

            # Prompt GPT with a description
            self.logger.info("Prompting...")
            prompt = self.create_prompt(image_path)
            self.log_prompt(prompt, image_path)
            start_time = time.perf_counter()
            gpt_response = self.call_gpt(prompt)
            end_time = time.perf_counter()
            self.logger.info(
                f"GPT-4 Response: {gpt_response}, time_elasped: {'%.3f'%(end_time - start_time)}s"
            )
            response = {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": gpt_response.content,
                        }
                    ],
                }
            self.history.append(response)
            return response

    def query_gpt(self, cam):
        i = 0
        while self.running:
            response = self.query_gpt_once(cam.frame_stack, i)
            if response is not None:
                i += 1