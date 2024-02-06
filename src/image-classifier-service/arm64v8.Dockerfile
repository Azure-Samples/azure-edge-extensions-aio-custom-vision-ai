# Use a base image for 64-bit Raspberry Pi running Debian
FROM balenalib/raspberrypi4-64-debian:bullseye

RUN [ "cross-build-start" ]

# Update package index and install python
RUN install_packages \
    python3 \
    python3-pip \
    python3-dev

RUN apt update && apt install -y libjpeg62-turbo libopenjp2-7 libtiff5 libatlas-base-dev libxcb1

# Install specific version of protobuf
RUN pip3 install protobuf==3.20.0

# Install protoc compiler
RUN apt install -y protobuf-compiler

RUN pip3 install absl-py six wrapt gast astor termcolor keras_applications keras_preprocessing --no-deps
RUN pip3 install numpy tensorflow --extra-index-url 'https://www.piwheels.org/simple' --no-deps
#RUN pip3 install flask --index-url 'https://www.piwheels.org/simple'
RUN pip3 install MarkupSafe
RUN pip3 install flask==2.0.1 --index-url 'https://www.piwheels.org/simple'
RUN pip3 install Pillow

COPY app /app

# Expose the port
EXPOSE 8580

# Set the working directory
WORKDIR /app

RUN [ "cross-build-end" ]

# Run the flask server for the endpoints
CMD python3 -u app.py