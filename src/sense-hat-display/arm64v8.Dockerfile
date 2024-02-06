FROM arm64v8/debian:latest

RUN apt-get update && apt-get install -yq \
  python3 \
  python3-venv \
  git \
  vim \
  wget && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install pillow numpy

RUN git clone https://github.com/astro-pi/python-sense-hat.git && \
  cd python-sense-hat && \
  python setup.py install

COPY . /usr/src/app
WORKDIR /usr/src/app

# Expose the port
EXPOSE 8740

CMD [ "python", "-u", "./main.py" ]