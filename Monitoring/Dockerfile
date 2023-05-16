# Specify the base image
FROM ubuntu:latest

WORKDIR /monitoring

COPY . .

# Update packages and install Python 3.9
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip jq dnsutils

# Install numpy and pandas packages 
RUN pip3 install -r ./requirements.txt

