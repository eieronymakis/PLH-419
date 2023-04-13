# Specify the base image
FROM arm64v8/ubuntu:latest

# Update packages and install Python 3.9
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip &&\
    apt-get install -y iputils-ping &&\
    apt-get install -y jq

WORKDIR /Manager

# Install numpy and pandas packages 
RUN pip3 install zmq flask