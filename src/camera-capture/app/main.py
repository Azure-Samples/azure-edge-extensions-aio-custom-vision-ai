# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

from flask import Flask, request, jsonify
from cloudevents.http import from_http
from dapr.clients import DaprClient
from distutils.util import strtobool
import json
import logging
import os
import random
import sys
import time
import uuid

import camera_capture
from camera_capture import CameraCapture
from kubernetes import client, config
import re


# global counters
SEND_CALLBACKS = 0

# Maintain a dictionary to store pending requests
pending_requests = {}

#subscriber using Dapr PubSub
app = Flask(__name__)
app_port = os.getenv('CAMERA_CAPTURE_PORT', '5012')

# backend
# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'customvisionpubsub',
        'topic': 'camera_capture_topic',
        'route': 'camera_capture_topic_handler'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return jsonify(subscriptions)

def send_to_pubsub_callback(strMessage):
    MessageManager.send_message_to_output(strMessage)

# Callback received when the message that we're forwarding is processed.

class MessageManager(object):

    def __init__(
            self,
            messageTimeout,
            verbose):
        '''
        Communicate with the MQ broker pub/sub

        :param int messageTimeout: the maximum time in milliseconds until a message times out. By default, messages do not expire.
        :param bool verbose: set to true to get detailed logs on messages
        '''
        self.messageTimeout = messageTimeout
        self.client = DaprClient()

    def send_message_to_output(data_json):
        print('Attempting to publish data: ' + json.dumps(data_json))
        #logging.info('Publishing data: ' + json.dumps(data_json))
        with DaprClient() as client:
            result = client.publish_event(
                pubsub_name='customvisionpubsub',
                topic_name='camera_capture_topic',
                data=json.dumps(data_json),
                data_content_type='application/json',
            )
            #logging.info('Published data: ' + json.dumps(data_json))
            time.sleep(1)
            global SEND_CALLBACKS
            SEND_CALLBACKS += 1

def main(
        videoPath,
        videoUrl,
        imageProcessingEndpoint="",
        imageProcessingParams="",
        showVideo=False,
        verbose=False,
        loopVideo=True,
        convertToGray=False,
        resizeWidth=0,
        resizeHeight=0,
        annotate=False
):
    '''
    Capture a camera feed, send it to processing and forward outputs to the MQ broker

    :param int videoPath: camera device path such as /dev/video0 or a test video file such as /TestAssets/myvideo.avi. Mandatory.
    :param str videoUrl: the service url for the grpc endpoint. (Default). Mandatory.
    :param str imageProcessingEndpoint: service endpoint to send the frames to for processing. Example: "http://face-detect-service:8080". Leave empty when no external processing is needed (Default). Optional.
    :param str imageProcessingParams: query parameters to send to the processing service. Example: "'returnLabels': 'true'". Empty by default. Optional.
    :param bool showVideo: show the video in a window. False by default. Optional.
    :param bool verbose: show detailed logs and perf timers. False by default. Optional.
    :param bool loopVideo: when reading from a video file, it will loop this video. True by default. Optional.
    :param bool convertToGray: convert to gray before sending to external service for processing. False by default. Optional.
    :param int resizeWidth: resize frame width before sending to external service for processing. Does not resize by default (0). Optional.
    :param int resizeHeight: resize frame width before sending to external service for processing. Does not resize by default (0). Optional.ion(
    :param bool annotate: when showing the video in a window, it will annotate the frames with rectangles given by the image processing service. False by default. Optional. Rectangles should be passed in a json blob with a key containing the string rectangle, and a top left corner + bottom right corner or top left corner with width and height.
    '''
    try:
        print("\nPython %s\n" % sys.version)
        print("Camera Capture module started. Press Ctrl-C to exit.")
        try:
            global messageManager
            messageManager = MessageManager(
                10000, verbose)
        except Exception as e:
            print("Unexpected error %s from PubSub" % e.message)
            return            
        with CameraCapture(videoPath, videoUrl, imageProcessingEndpoint, imageProcessingParams, showVideo, verbose, loopVideo, convertToGray, resizeWidth, resizeHeight, annotate, send_to_pubsub_callback) as cameraCapture:
            cameraCapture.start()
    except KeyboardInterrupt:
        print("Camera capture module stopped")

# Gets the url of the service the udev monitoring brokers are serving values on
def get_grpc_url(configuration_name, namespace="default"):
    
    config.load_incluster_config()
    coreV1Api = client.CoreV1Api()

    # TODO use labels instead once available
    instance_service_name_regex = re.compile(
        configuration_name + "-[\da-f]{6}-svc")
    url = None
    print("Listing services with their info:\n")
    ret = coreV1Api.list_namespaced_service(namespace=namespace,watch=False)
    for svc in ret.items:
        print("%s\t%s\t%s" %
              (svc.metadata.namespace, svc.metadata.name, svc.spec.cluster_ip))
        if svc.metadata.name == configuration_name + "-svc":
            grpc_ports = list(
                filter(lambda port: port.name == "grpc", svc.spec.ports))
            if (len(grpc_ports) == 1):
                url = "{0}:{1}".format(svc.spec.cluster_ip, grpc_ports[0].port)
        elif instance_service_name_regex.match(svc.metadata.name):
            grpc_ports = list(
                filter(lambda port: port.name == "grpc", svc.spec.ports))
            if (len(grpc_ports) == 1):
                url = "{0}:{1}".format(svc.spec.cluster_ip, grpc_ports[0].port)
    print("CAMERA URL: {0}".format(url))
    return url    

def __convertStringToBool(env):
    try:
        return bool(strtobool(env))
    except ValueError:
        raise ValueError('Could not convert string to bool.')

if __name__ == '__main__':
    try:
        VIDEO_PATH = ""
        VIDEO_URL = ""
        if 'CONFIGURATION_NAME' in os.environ:
            VIDEO_URL = get_grpc_url(os.environ['CONFIGURATION_NAME'],os.environ['NAMESPACE'])            
        elif 'VIDEO_PATH' in os.environ:    
            VIDEO_PATH = os.environ['VIDEO_PATH']            
        else:
            raise Exception("Neither VIDEO_URL nor VIDEO_PATH are set in the environment variables.")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
        IMAGE_PROCESSING_PARAMS = os.getenv('IMAGE_PROCESSING_PARAMS', "")
        SHOW_VIDEO = __convertStringToBool(os.getenv('SHOW_VIDEO', 'False'))
        VERBOSE = __convertStringToBool(os.getenv('VERBOSE', 'False'))
        LOOP_VIDEO = __convertStringToBool(os.getenv('LOOP_VIDEO', 'True'))
        CONVERT_TO_GRAY = __convertStringToBool(
            os.getenv('CONVERT_TO_GRAY', 'False'))
        RESIZE_WIDTH = int(os.getenv('RESIZE_WIDTH', 0))
        RESIZE_HEIGHT = int(os.getenv('RESIZE_HEIGHT', 0))
        ANNOTATE = __convertStringToBool(os.getenv('ANNOTATE', 'False'))

    except ValueError as error:
        print(error)
        sys.exit(1)

    main(VIDEO_PATH, VIDEO_URL, IMAGE_PROCESSING_ENDPOINT, IMAGE_PROCESSING_PARAMS, SHOW_VIDEO,
         VERBOSE, LOOP_VIDEO, CONVERT_TO_GRAY, RESIZE_WIDTH, RESIZE_HEIGHT, ANNOTATE)
