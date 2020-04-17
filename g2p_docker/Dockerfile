FROM ubuntu:latest

RUN apt-get update 
RUN apt-get install -y locales locales-all
RUN apt-get install -y make
RUN apt install -y gcc
RUN apt-get install -y python3-pip python3-dev
RUN pip3 install langid

ENV LC_ALL en_US.UTF-8
ENV LANG en-US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /home/asr-g2p/g2p_docker/

ENTRYPOINT ["python3", "g2p.py"]