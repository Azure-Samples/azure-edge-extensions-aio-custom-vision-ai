FROM arm64v8/debian:latest

RUN apt-get update && apt-get install -yq \
  python3 \
  python3-venv \
  git \
  vim \
  wget \
  build-essential \
  python3-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install pillow numpy

# Clone, build and install RTIMULib
RUN git clone https://github.com/RPi-Distro/RTIMULib.git \
    && cd RTIMULib/Linux/python \
    && python3 setup.py build \
    && python3 setup.py install

COPY /build/arm64v8-requirements.txt ./
RUN pip install -r arm64v8-requirements.txt

RUN git clone https://github.com/astro-pi/python-sense-hat.git && \
  cd python-sense-hat && \
  python setup.py install

ADD /app/ .

# Expose the port
EXPOSE 8740

CMD [ "python", "-u", "main.py" ]