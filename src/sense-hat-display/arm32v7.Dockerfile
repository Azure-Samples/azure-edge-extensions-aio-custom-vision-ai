FROM balenalib/raspberrypi3-debian:bullseye

RUN apt-get update && apt-get install -yq \
  python3 \
  python3-sense-hat \
  python3-influxdb \
  vim \
  wget && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /usr/src/app
WORKDIR /usr/src/app

# Expose the port
EXPOSE 8740

CMD [ "python3", "-u", "./main.py" ]