# Docker file for heudiconv ChRIS plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-heudiconv .
#
# In the case of a proxy (located at 192.168.13.14:3128), do:
#
#    docker build --build-arg http_proxy=http://192.168.13.14:3128 --build-arg UID=$UID -t local/pl-heudiconv .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pl-heudiconv
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-heudiconv
#

FROM python:3.9.1-slim-buster
LABEL org.opencontainers.image.authors="grdryn <gerard@ryan.lt>" \
      org.opencontainers.image.title="heudiconv ChRIS Plugin" \
      org.opencontainers.image.description="A ChRIS plugin that..."

ADD https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20220720/dcm2niix_lnx.zip /tmp/dcm2niix_lnx.zip
RUN apt-get -y update && \
    apt-get install -y unzip git git-annex && \
    unzip /tmp/dcm2niix_lnx.zip -d /usr/local/bin/

WORKDIR /usr/local/src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["pl-heudiconv", "--help"]
