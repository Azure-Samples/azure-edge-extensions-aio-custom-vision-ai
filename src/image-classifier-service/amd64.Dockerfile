# Use a base image for amd64
FROM python:3.7-slim

# Update package index and install dependencies
RUN apt-get update && apt-get install -y \
    protobuf-compiler

# Upgrade pip
RUN pip install -U pip

# Install specific version of protobuf
RUN pip install protobuf==3.20.0

# Install other Python packages
RUN pip install numpy==1.17.3 tensorflow==2.0.0 flask pillow

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Create app directory and copy files
RUN mkdir app
COPY ./app/app-amd64.py ./app/app.py
COPY ./app/predict-amd64.py ./app/predict.py
COPY ./app/labels.txt ./app/model.pb ./app/

# Expose the port
EXPOSE 8580

# Set the working directory
WORKDIR /app

# Run the flask server for the endpoints
CMD ["python", "-u", "app.py"]