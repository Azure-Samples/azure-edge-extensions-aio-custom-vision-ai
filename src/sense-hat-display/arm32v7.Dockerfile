FROM balenalib/raspberrypi3-debian:bullseye

WORKDIR /app

RUN apt-get update && apt-get install -yq \
  python3 \
  python3-pip \
  python3-sense-hat \
  python3-influxdb \
  vim \
  wget \
  libatomic1 \
  libopenblas-base && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY /build/arm32v7-requirements.txt ./
RUN pip3 install -r arm32v7-requirements.txt

ADD /app/ .

# Expose the port
EXPOSE 8740

CMD [ "python3", "-u", "main.py" ]