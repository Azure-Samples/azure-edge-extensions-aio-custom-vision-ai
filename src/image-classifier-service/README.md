
# Azure IoT Operations (AIO) Image Classifier Service

This container is an dapr workload that runs as a web service over HTTP running locally that takes in images and classifies them based on a custom model built via the [Custom Vision website](https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/). This module has been exported from the Custom Vision website and slightly modified to run on a ARM architecture. You can modify it by updating the model.pb and label.txt files to update the model.

## How to build:
To build the Image Classifier application, select and build the docker file for your appropriate architecture.

```bash
cd src/image-classifier-service
docker build -f <platform>.Dockerfile -t <registry host>/image-classifier-service-<platform>:latest .
```
> **Tip:**Replace <your_server_ip_address> with your actual usb server IP address and <registry host> with your actual registry host or ACR url.

Login your container registry and push the container image to the registry:

For example:

```bash
az acr login --name $ACR_NAME
docker push <registry host>/image-classifier-service-<plaform>:latest
```
docker build -t <your image name> .

## How to run locally
Forward the port on your local machine:
kubectl port-forward deployment/image-classifier-service-web-workload 8580:8580 -n azure-iot-operations

Then use your favorite tool to connect to the end points.

POST http://< external IP >/image with multipart/form-data using the imageData key
e.g
```bash
	curl -X POST http://<external IP>/image -F imageData=@some_file_name.jpg
```
POST http://< external IP >/image with application/octet-stream
e.g.
```bash
	curl -X POST http://<external IP>/image -H "Content-Type: application/octet-stream" --data-binary @some_file_name.jpg
```
POST http://< external IP >/url with a json body of { "Url": "<test url here>" }
e.g.
```bash
    curl -X POST http://<external IP>/url -d "{ \"Url\": \"<test url here>\" }"
```	