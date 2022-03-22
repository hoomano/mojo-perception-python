"""
@license
Copyright 2022 Hoomano SAS. All Rights Reserved.
Licensed under the MIT License, (the "License");
you may not use this file except in compliance with the License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

=============================================================================
"""

import cv2

# todo : change by import mojo-perception-python
import sys
sys.path.append('../src')
from mojo_perception_api import MojoPerceptionAPI

# We initialize MojoPerceptionAPI here
# Use your secured token and namespace to load the API.
# See the README to generate one using your Mojo Perception API Key.
mojo_perception = MojoPerceptionAPI("<your_api_key>")

# We set options
mojo_perception.set_options({
    # Which emotions will be calculated by the API
    "emotions": ["attention"],
    # Set subscribeRealtimeOutput to true to activate callbacks
    "subscribe_realtime_output": True})

# Prepares MojoPerceptionAPI callbacks
mojo_perception.attention_callback = lambda value: print(value)
mojo_perception.warmup_done_callback = lambda: print("Warmup done !")
mojo_perception.on_error_callback = lambda message: print(message)

# Starts MojoPerceptionAPI
mojo_perception.start_camera_and_connect_api()
# mojo_perception.read_video_and_connect_api(video_path=<my_video.mp4>)

# Recursively call compute on each frame
while mojo_perception.video_stream.isOpened():
    if mojo_perception.initialized:
        success, image = mojo_perception.video_stream.read()
        if success:
            cv2.imshow('Frame', image)
            mojo_perception.compute_anonymized_facemesh(image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
        else:
            # We stop the API when the video is over
            mojo_perception.stop_facial_expression_recognition_api()
