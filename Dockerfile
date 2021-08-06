FROM ubuntu:18.04

MAINTAINER FMK <fmk@fmk.com>

#USER root
#WORKDIR /root

EXPOSE 5000
EXPOSE 5432
EXPOSE 6060
EXPOSE 6379
#EXPOSE 8888

ENTRYPOINT [ "/bin/bash", "-c" ]

RUN apt-get -qq -y update && \
    apt-get -qq -y upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        gcc \
        g++ \
        zlibc \
        zlib1g-dev \
        libssl-dev \
        libbz2-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libgdbm-dev \
        libgdbm-compat-dev \
        liblzma-dev \
        libreadline-dev \
        uuid-dev \
        libffi-dev \
        tk-dev \
        wget \
        curl \
        git \
        make \
        sudo \
        bash-completion \
        tree \
        vim \
        nano \
        net-tools \
        htop \
        postgresql-client \
        cron \
        redis-server \
        screen \
        software-properties-common && \
    mv /usr/bin/lsb_release /usr/bin/lsb_release.bak && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt-get/lists/*

ARG PYTHON_VERSION_TAG=3.7.3
ARG LINK_PYTHON_TO_PYTHON3=1

COPY install_python.sh install_python.sh

RUN bash install_python.sh ${PYTHON_VERSION_TAG} ${LINK_PYTHON_TO_PYTHON3} && \
    rm -r install_python.sh Python-${PYTHON_VERSION_TAG}

COPY . $HOME/qtracks
WORKDIR $HOME/qtracks

RUN python3.7 -m pip install -r requirements.txt
RUN ["chmod", "+x", "proc_exec.sh"]
#RUN ["redis-server", "--protected-mode no"]
CMD ["./proc_exec.sh"]