ARG SERVER_IP_ADDRESS=127.0.0.1
FROM arm64v8/debian:latest

RUN echo "BUILD MODULE: CameraCapture"

RUN apt-get update && apt-get install -y python3 python3-pip python3.11-venv

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# Update package index and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenjp2-7-dev \
    zlib1g-dev \
    libatlas-base-dev \
    wget \
    libboost-python-dev \
    curl \
    libcurl4-openssl-dev \
    libldap2-dev \
    libgtkmm-3.0-dev \
    libarchive-dev \
    libcurl4-openssl-dev \
    intltool \
    git \
    libtool \
    autoconf2.69 \
    libudev-dev

# Clone the Linux source code and compile the usbip package
RUN git config --global http.postBuffer 524288000 && \
    git clone --depth 1 https://github.com/torvalds/linux.git /usr/src/linux && \
    cd /usr/src/linux/tools/usb/usbip && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install
    
# Install usbip client packages
RUN apt-get update && \
    apt install -y hwdata

RUN apt-get install -y kmod    

# Required for OpenCV
RUN apt-get install -y \
    libhdf5-dev libhdf5-serial-dev \
    libjpeg-dev libtiff5-dev \
    libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    libgtk2.0-dev \
    libilmbase-dev libopenexr-dev

# Install Python packages
COPY /build/arm64v8-requirements.txt ./
RUN python -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install numpy
RUN pip3 install opencv-contrib-python
RUN pip3 install tornado
RUN pip3 install opencv-python
RUN pip3 install -r arm64v8-requirements.txt  # You might need to change this file to match arm64 requirements

# Copy all files in the camera-client folder
COPY camera-client/ .

# Make the *.sh files executable
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