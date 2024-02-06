# Set a default value for the argument
ARG SERVER_IP_ADDRESS=127.0.0.1
FROM ubuntu:20.04

RUN echo "BUILD MODULE: CameraCapture"

WORKDIR /app

# Enable the universe repository before installing packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.8 \
        python3-pip \
        python3.8-dev \
        libcurl4-openssl-dev \
        libboost-python-dev \
        libgtk2.0-dev \
        build-essential \
        git \
        libudev-dev \
        autoconf \
        automake \
        libtool

RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Clone the Linux source code and compile the usbip package
RUN git config --global http.postBuffer 524288000 && \
    git clone --depth 1 https://github.com/torvalds/linux.git /usr/src/linux && \
    cd /usr/src/linux/tools/usb/usbip && \
    apt-get install -y autoconf automake libtool && \
    apt-get install -y libudev-dev && \    
    ./autogen.sh && \
    ./configure && \
    make M=drivers/usb/usbip && \
    make install

RUN ls /usr/src/linux/drivers/usb/usbip

# Compile the vhci driver
RUN cd /usr/src/linux/drivers/usb/usbip && \
    make M=drivers/usb/usbip && \
    mkdir -p /dist && \
    cp usbip-core.ko vhci-hcd.ko /dist

#RUN mkdir -p /app/dist
# RUN apt-get install -y linux-image-extra-virtual && \
#     mkdir -p /dist && \
#     find /usr/ -iname "*.ko" -exec cp {} /dist \; && \
#     cd /dist 
#     #insmod vhci-hcd.ko && \
#     #insmod usbip-core.ko

# Install usbip client packages
RUN apt-get update && \
    apt install -y linux-tools-generic hwdata usbutils

RUN update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
RUN update-alternatives --install /usr/local/bin/usbip usbip $(command -v ls /usr/lib/linux-tools/*/usbip | tail -n1) 20
RUN apt-get install -y kmod

# Install OpenCV dependencies
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0 

# Install Python packages
RUN pip3 install python-dotenv    

# Install Python packages
COPY /build/amd64-requirements.txt ./
#COPY /dist/* ./
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --upgrade setuptools
RUN python3.8 -m pip install -r amd64-requirements.txt

# Copy all files in the camera-client folder
COPY camera-client/ .

# Make the *.sh files executable
RUN sed -i 's/\r$//' *.sh
RUN chmod +x *.sh

# Copy and run the install.sh script
COPY install.sh .
RUN chmod +x install.sh
RUN ./install.sh $SERVER_IP_ADDRESS

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]