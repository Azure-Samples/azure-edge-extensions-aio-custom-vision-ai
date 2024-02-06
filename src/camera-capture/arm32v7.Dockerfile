FROM balenalib/raspberrypi3

RUN echo "BUILD MODULE: CameraCapture"

# Enforces cross-compilation through Quemu
RUN [ "cross-build-start" ]

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install grpcio from the default PyPI repository
RUN python3 -m pip install grpcio>=1.37.0

# Update package index and install dependencies
RUN install_packages \
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
    usbip \
    git

# Rest of your Dockerfile...

# Clone the Linux source code and compile the usbip package
RUN git config --global http.postBuffer 524288000 && \
    git clone https://github.com/torvalds/linux.git /usr/src/linux && \
    cd /usr/src/linux/tools/usb/usbip && \
    make && \
    make install

# Required for OpenCV
RUN install_packages \
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
COPY /build/arm32v7-requirements.txt /tmp/
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install numpy --extra-index-url 'https://www.piwheels.org/simple' --no-deps
RUN pip3 install opencv-contrib-python
RUN pip3 install tornado
RUN pip3 install opencv-python
RUN pip3 install --index-url=https://www.piwheels.org/simple -r /tmp/arm32v7-requirements.txt 

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

RUN [ "cross-build-end" ]  

ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]