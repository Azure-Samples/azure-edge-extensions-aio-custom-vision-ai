# Copyright (c) Emmanuel Bertrand. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

from flask import Flask, request, jsonify
from cloudevents.http import from_http
from dapr.clients import DaprClient
from distutils.util import strtobool
import os
import random
import time
import sys

import DisplayManager
from DisplayManager import DisplayManager
import MessageParser
from MessageParser import MessageParser
import json

RECEIVE_CALLBACKS = 0

# receive_message_callback is invoked when an incoming message arrives on the specified  input queue
#subscriber using Dapr PubSub
app = Flask(__name__)
app_port = os.getenv('SENSE_HAT_DISPLAY_PORT', '8740')
messageTimeout = 1000
def __convertStringToBool(env):
    try:
        return bool(strtobool(env))
    except ValueError:
        raise ValueError('Could not convert string to bool.')

verbose = __convertStringToBool(os.getenv('VERBOSE', 'False'))

# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'customvisionpubsub',
        'topic': 'camera_capture_topic',
        'route': 'camera_capture_topic_handler'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    print("Sense Hat Module is now waiting for pubsub messages..")
    return jsonify(subscriptions)

# Dapr subscription in /dapr/subscribe sets up this route
@app.route('/camera_capture_topic_handler', methods=['POST'])
def camera_subscriber():
    global RECEIVE_CALLBACKS
    RECEIVE_CALLBACKS += 1   
    print("Camera Subscriber: Received message #: " + str(RECEIVE_CALLBACKS)) 
    event = from_http(request.headers, request.get_data())
    message_buffer = event.data.get_bytearray()
    body = message_buffer[:len(message_buffer)].decode('utf-8')
    allTagsAndProbability = json.loads(body)
    try:
        DISPLAY_MANAGER.displayImage(MESSAGE_PARSER.highestProbabilityTagMeetingThreshold(
            allTagsAndProbability, THRESHOLD))
    except Exception as error:
        print("Message body: " + body)
        print(error)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


class HubManager(object):

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
        print("Module is now waiting for camera messages.")        

def main():
    try:
        print("Starting the SenseHat module...")

        global DISPLAY_MANAGER
        global MESSAGE_PARSER
        DISPLAY_MANAGER = DisplayManager()
        MESSAGE_PARSER = MessageParser()
        hubManager = HubManager(messageTimeout, verbose)

        while True:
            time.sleep(1000)

    except KeyboardInterrupt:
        print("Sense Display sample stopped")


if __name__ == '__main__':
    try:
        global THRESHOLD
        THRESHOLD = float(os.getenv('THRESHOLD', 0))

    except Exception as error:
        print(error)
        sys.exit(1)

    main()
