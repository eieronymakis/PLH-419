# Specify the base image
FROM python:3.9

WORKDIR /Worker

# Copy the code into the container
COPY worker.py /Worker

# Install any required dependencies
RUN pip install zmq

# Set the entrypoint to the worker script
ENTRYPOINT ["python","-u", "/Worker/worker.py"]