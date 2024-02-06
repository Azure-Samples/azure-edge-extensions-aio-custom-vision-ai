# Azure IoT Operations (AIO) Camera Capture module

This container is an dapr workload that can read a video stream from a camera or from a video file and optionally send frames to capture camera module for processing. It forwards all processing results to the an MQ broker.
It is a Linux Docker container made for AMD64 and ARM processors written in Python.

## Additional configurations
You can use the current conifguration set in the deployment manifest file or update the configuration of this module as follow:

The camera mount path or the video file must be provided through the VIDEO_PATH environment variable:
- Camera mount:
    - In the deployment manifest:
    ```json
    "createOptions": "{\"Env\":[\"VIDEO_PATH=/dev/video0\"]}"
    ```
- Video file:
    - Make sure to include the video file in the .Dockerfile:
    ```docker
    ADD ./test/ .
    ```
    - In the deployment manifest:
    ```json
    "createOptions": "{\"Env\":[\"VIDEO_PATH=./AppleAndBanana.mp4\"]}"
    ```
    - To share usb camera device over the network
    ```bash
        cd camera-server
        ./usbip_start.sh usb_device_id
    ```    
    - To stop sharing a usb camera device
    ```bash
        cd camera-server
        ./usbip_stop.sh usb_device_id
    ```
    Replace usb_value with your actual usb device ID value.

    - To run as a service and share a usb camera device on the network at boot, edit the usbip.service file with the usb device ID value
    After editing the usb device id in the usbipd.service file, execute the following commands:
    ```bash
        sudo cp usbipd.service /lib/systemd/system/
        sudo systemctl --system daemon-reload
        sudo systemctl enable usbipd.service
        sudo systemctl start usbipd.service
    ```
    - To verify the service is running
    ```bash
        sudo systemctl status usbipd.service   
        usbip port 
    ```

    - Attach to usb camera device on the network
    ```bash
        cd camera-client
        ./usbip_start.sh server_ip_address usb_device_id
    ```    
    - Detach usb camera device
    ```bash
        cd camera-client
        ./usbip_stop.sh usb_device_id
    ```
    Replace usb_value with your actual server ip and usb device ID value.
    
    - To run as a service and attach to usb camera at boot, edit the usbip.service file with the server ip address and usb device ID value
    ```bash
        nano /lib/systemd/system/usbip.service
    ```
    After editing the server ip address and usb device id in the usbip.service file, execute the following commands:
    ```bash
        sudo cp usbip.service /lib/systemd/system/
        sudo systemctl --system daemon-reload
        sudo systemctl enable usbip.service
        sudo systemctl start usbip.service
    ```
    - To verify the service is running
    ```bash
        sudo systemctl status usbip.service   
        usbip port 
    ```
    

## Optional parameters
The following parameters are optional and can be specified via environment variables in the deployment manifest (See 'createOptions' above).

|Environment variable  |Description  |
|---------|---------|
|IMAGE_PROCESSING_ENDPOINT     | Service endpoint to send the frames to for processing. Example: "http://my-ai-service:8580" (where "my-ai-service" is the name of another workload module). Leave empty when no external processing is needed (Default).  |
|IMAGE_PROCESSING_PARAMS     | Query parameters to send to the processing service. Example: "{'returnLabels': 'true'}". Empty by default. |
|SHOW_VIDEO     | Show the video. From a browser, go to "http://YourCameraCaptureIpAdress:5012". Examle: "FALSE". False by default. |
|VERBOSE     |  Show detailed logs and perf timers. Example: "FALSE". False by default.  |
|LOOP_VIDEO     | When reading from a video file, it will loop this video. Example: "TRUE". True by default. |
|CONVERT_TO_GRAY     | Convert to gray before sending to external service for processing. Example: "FALSE". False by default.  |
|RESIZE_WIDTH     | Resize frame width before sending to external service for processing. Example: "256". Does not resize by default (0). |
|RESIZE_HEIGHT     | Resize frame width before sending to external service for processing. Example: "456". Does not resize by default (0). |
