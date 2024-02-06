# Set a default value for the argument
# ARG SERVER_IP_ADDRESS=127.0.0.1
# ARG USB_ID1: 0000:0001
# ARG USB_ID2: 0000:0002
FROM debian:latest

RUN echo "BUILD MODULE: CameraCapture"

WORKDIR /app

# Update and install packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        libcurl4-openssl-dev \
        libboost-python-dev \
        libgtk2.0-dev \
        build-essential \
        git \
        libudev-dev \
        autoconf \
        automake \
        libtool \
        kmod \
        flex \
        bison \
        bc \
        libelf-dev 
        #git

# Clone the Linux source code and compile the usbip package
RUN git config --global http.postBuffer 524288000 && \
    git clone --depth 1 https://github.com/torvalds/linux.git /usr/src/linux && \
    cd /usr/src/linux && \
    echo "CONFIG_MODULES=y" >> .config && \
    echo "CONFIG_USBIP_CORE=m" >> .config && \
    echo "CONFIG_USBIP_VHCI_HCD=m" >> .config && \
    make oldconfig && make prepare && \
    make && \
    cd tools/usb/usbip && \
    apt-get install -y autoconf automake libtool && \
    apt-get install -y libudev-dev && \    
    ./autogen.sh && \
    ./configure && \
    make && \
    make install

# # Clone the vhci_hcd repository
# RUN git clone https://github.com/linuxbuh/vhci_hcd.git

# # Create the kernel-tools directory and copy the vhci_hcd repository into it
# RUN mkdir -p kernel-tools && cp -r vhci_hcd kernel-tools/

# # Copy the already cloned linux repository into the kernel-tools directory
# RUN cp -r /usr/src/linux kernel-tools/


# # Compile the vhci driver
# RUN apt-get install -y linux-headers-$(uname -r) && \
#     cd /usr/src/linux && \
#     make M=drivers/usb/usbip && \
#     mkdir -p /dist && \
#     (test -f drivers/usb/usbip/usbip-core.ko && test -f drivers/usb/usbip/vhci-hcd.ko) || (echo "Error: Kernel modules not found" && exit 1) && \
#     cp drivers/usb/usbip/usbip-core.ko drivers/usb/usbip/vhci-hcd.ko /dist 
#RUN apt-get update && apt-get install -y linux-headers-$(uname -r)
# RUN apt-get update && apt-get install -y linux-headers-amd64 git && \
#     KERNEL_VERSION="6.1.0-17" && \
#     git clone --depth 1 https://github.com/linuxbuh/vhci_hcd.git && \
#     cd vhci_hcd && \
#     mkdir -p linux/"$KERNEL_VERSION"/drivers/usb/core && \
#     find /usr/src/ -name "linux-headers-*" -type d && \
#     cp /usr/src/linux-headers-$KERNEL_VERSION-common/include/linux/usb/hcd.h linux/"$KERNEL_VERSION"/drivers/usb/core/ && \
#     make KVERSION="$KERNEL_VERSION" KSRC=/usr/src/linux-headers-$KERNEL_VERSION-common

WORKDIR /app
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Install usbip package
RUN apt-get update && \
    apt-get install -y usbip 

# Install OpenCV dependencies
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0 

# Install venv module
RUN apt-get install -y python3-venv

# Create a virtual environment
RUN python3 -m venv /app/venv

# Use venv for the following commands
ENV PATH="/app/venv/bin:$PATH"

# Now you can install Python packages
RUN pip install python-dotenv

# Install Python packages
COPY /build/amd64-requirements.txt ./
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r amd64-requirements.txt

# Copy all files in the camera-client folder
COPY camera-client/ .

# Make the *.sh files executable
RUN sed -i 's/\r$//' *.sh
RUN chmod +x *.sh

#RUN modprobe usb-vhci-hcd && modprobe usb-vhci-iocifc

# Copy and run the install.sh script
COPY install.sh .
RUN chmod +x install.sh
#RUN ./install.sh $SERVER_IP_ADDRESS USB_ID1 USB_ID2 && sleep 2

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]