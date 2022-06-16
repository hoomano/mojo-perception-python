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

import logging
import socketio
from datetime import datetime
import mediapipe as mp
import cv2
import requests

class MojoPerceptionAPI:
    """
     This class is a MojoPerception API client.
     See README for a procedure to generate api_key.
    """
    def __init__(self, api_key, expiration=360):
        """
        Initializes the MojoPerceptionAPI client. Places default callbacks on
        calculation reception for each emotion and load the anonymization model

        :param api_key: String - Valid API Key
        :param expiration: Int - Time in seconds for the object to expire.
        """
        logging.basicConfig(level=logging.DEBUG)
        assert api_key is not None, "Please provide an API key"
        self.initialized = False
        self.api_key = api_key
        self.expiration = expiration
        self.mojo_perception_uri = "https://api.mojo.ai/mojo_perception_api"
        self.auth_token, self.host, self.port, self.user_namespace = self.create_user()
        self.socketIo_uri = "https://{}:{}".format(self.host, self.port)
        self.emotions = ["attention", "confusion", "surprise", "amusement", "pitching", "yawing"]
        self.subscribe_realtime_output = False
        self.api_socket = socketio.Client()
        self.sending = False
        self.attention_callback = self.default_callback
        self.amusement_callback = self.default_callback
        self.confusion_callback = self.default_callback
        self.surprise_callback = self.default_callback
        self.pitching_callback = self.default_callback
        self.yawing_callback = self.default_callback
        self.warmup_done_callback = self.default_callback
        self.warmup_callback_done = False
        self.first_emit_done = False
        self.first_emit_done_callback = self.default_callback
        self.on_error_callback = self.default_callback
        self.video_stream = None
        self.image_width = None
        self.image_height = None

    def set_options(self, options):
        """
        Set options for MojoPerceptionAPI, to change the list of emotions calculated and
        manage subscription to realtime output.
        :param options: dict - Options to set
            - options["emotions"] : list of emotions to be calculated by the API
            - options["subscribe_realtime_output"] : boolean, true to activate the callbacks @see attentionCallback
        """
        try:
            if "emotions" in options:
                self.emotions = options["emotions"]
            if "subscribe_realtime_output" in options:
                self.subscribe_realtime_output = options["subscribe_realtime_output"]
        except Exception as e:
            logging.error("Could not set options: {} : {}".format(options, e))

    def create_user(self):
        try:
            internal_request = requests.put(self.mojo_perception_uri + '/user',
                                            json={"datetime": str(datetime.now()), "expiration": self.expiration},
                                            headers={"Authorization": self.api_key})
            if internal_request.status_code != 200:
                logging.error("error : " + internal_request.text)

            return internal_request.json()["auth_token"], internal_request.json()["host_name"], \
                   internal_request.json()["port"], internal_request.json()["user_namespace"].replace("-", ""),

        except Exception as e:
            logging.error("Could not create user: {}".format(e))

    def __str__(self):
        """
        Returns a string representing the MojoPerceptionAPI object
        :return: String - emotions, socketIo_uri, subscribe_realtime_output, auth_token
        """
        return "emotions={}\nsocketIoURI={}\nsubscribeRealtimeOutput={}\nkey={}".format(
            self.emotions, self.socketIo_uri, self.subscribe_realtime_output, self.auth_token)

    def default_callback(self, message=None):
        """
        Used by default for all callbacks. Does nothing.
        :param message: String - not used
        """
        return

    def _connect_callback(self):
        """
        Called when the socketIO client connects to the Stream SocketIO server.
        Sets initialized value to True
        """
        self.initialized = True

    def _error_handler(self, msg):
        """
        Called when the socketIO client encounters an error.
        Calls on_error_callback with the error message.
        Stops facial expression recognition api.
        :param msg: String - error message returned by socketio
        """
        logging.error("Error: {}".format(msg))
        self.on_error_callback(msg)
        self.stop_facial_expression_recognition_api()

    def message_handler(self, msg):
        """
        Called when "calculation" event is received from the API through socketio.
        Calls the appropriate callbacks depending on the emotions received.
        :param msg: dict - Message received from the API
        """

        if "attention" in msg:
            self.attention_callback(float(msg["attention"]))
        if "amusement" in msg:
            self.amusement_callback(float(msg["amusement"]))
        if "confusion" in msg:
            self.confusion_callback(float(msg["confusion"]))
        if "surprise" in msg:
            self.surprise_callback(float(msg["surprise"]))
        if "pitching" in msg:
            self.pitching_callback(float(msg["pitching"]))
        if "yawing" in msg:
            self.yawing_callback(float(msg["yawing"]))

    def get_image_dimensions(self):
        """
        Get the image dimensions of the video stream
        :return: set images dimensions
        """
        try:
            self.image_width = int(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.image_height = int(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        except Exception as e:
            logging.error("Could not get image dimensions: {}".format(e))

    def read_video_and_connect_api(self, video_path):
        try:
            self.video_stream = cv2.VideoCapture(video_path)
            self.get_image_dimensions()
            self._api_connect()
        except Exception as e:
            logging.error("Error during initialization: {}".format(e))

    def start_camera_and_connect_api(self):
        """
        Starts the camera and connects to the MojoPerceptionAPI through socketio.
        Defines socketio callbacks.
        :param video_path: String - path to the video file to be evaluated by MojoPerceptionAPI. If 0, the camera is used.
        """
        try:
            self.video_stream = cv2.VideoCapture(0)
            self.get_image_dimensions()
            self._api_connect()
        except Exception as e:
            logging.error("Error during initialization: {}".format(e))

    def set_image_dimensions_and_connect_api(self, image_width, image_height):
        """
        Sets image dimensions and connects to the MojoPerceptionAPI through socketio.
        Defines socketio callbacks.
        :param image_width: Width of image
        :param image_height: Height of image
        """
        try:
            self.image_width = image_width
            self.image_height = image_height
            self._api_connect()
        except Exception as e:
            logging.error("Error during initialization: {}".format(e))

    def _api_connect(self):
        """
        Connects to the MojoPerceptionAPI through socketio.
        Defines socketio callbacks.
        """
        try:
            self.api_socket.connect(self.socketIo_uri, namespaces=[f'/{self.user_namespace}'],
                                    transports=['websocket', 'polling'])

            if self.subscribe_realtime_output:
                self.api_socket.on('calculation', self.message_handler, namespace=f'/{self.user_namespace}')

            self.api_socket.on('error', self._error_handler, namespace=f'/{self.user_namespace}')
            self.api_socket.on('connect', self._connect_callback(), namespace=f'/{self.user_namespace}')

        except Exception as e:
            logging.error("Error during connexion: {}".format(e))

    def compute_anonymized_facemesh(self, image):
        """
        Computes the anonymized facemesh of the image and calls the emit function.
        :param image: numpy array - image to be processed (frame from video)
        """
        try:
            if self.first_emit_done and not self.warmup_callback_done:
                self.warmup_done_callback()
                self.warmup_callback_done = True
            with mp.solutions.face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,  # with iris
                    min_detection_confidence=0.9,
                    min_tracking_confidence=0.9) as face_mesh:
                image.flags.writeable = False
                frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(frame)
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    face_mesh = self.face_landmarks_to_json(face_landmarks.landmark, self.image_width, self.image_height )
                    self.emit_facemesh(face_mesh)
                else:
                    self.emit_facemesh([])
        except Exception as e:
            self.on_error_callback(e)
            logging.error("Error during anonymized facemesh computation: {}".format(e))

    def emit_facemesh(self, face_mesh):
        """
        Sends the facemesh to the streaming SocketIO server.
        :param face_mesh: List of lists - Facemesh of the image computed from image input
        """
        try:
            if face_mesh is None:
                return
            if self.auth_token is None:
                return
            self.api_socket.emit('facemesh',
                                 {'facemesh': face_mesh,
                                  'token': self.auth_token,
                                  'timestamp': datetime.now().isoformat(),
                                  'output': self.emotions},
                                 namespace=f'/{self.user_namespace}')
            if not self.first_emit_done:
                self.first_emit_done = True
                self.sending = True
                self.first_emit_done_callback()
        except Exception as e:
            logging.error("Error during emitting facemesh: {}".format(e))

    def face_landmarks_to_json(self, face_landmarks, image_width, image_height):
        """
        Converts the face landmarks to a json format that is compatible with the MojoPerceptionAPI (multiply by image dimensions).
        :param face_landmarks: List of tuples - Face landmarks of the image given by Mediapipe's model
        :param image_width: Int - Width of the image
        :param image_height: Int - Height of the image
        :return: List of lists - Facemesh of the image computed from image input
        """
        face_mesh = []
        for landmark in face_landmarks:
            face_mesh.append([landmark.x * image_width, landmark.y * image_height, landmark.z * image_width])
        # z denormalized from : https://pyup.io/changelogs/mediapipe/ 0.7.6
        return face_mesh

    def release_camera(self):
        """
        Releases the camera.
        """
        self.video_stream.release()

    def stop_facial_expression_recognition_api(self):
        """
        Stops sending to the API, disconnects from the stream SocketIO server and releases the camera.
        """
        try:
            if not self.sending:
                return
            self.sending = False
            self.api_socket.disconnect()
            if self.video_stream is not None:
                self.release_camera()
        except Exception as e:
            self.on_error_callback(e)
            logging.error("Error during stopping facial expression recognition api: {}".format(e))

