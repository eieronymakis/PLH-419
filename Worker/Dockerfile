# Specify the base image
FROM python:3.9

WORKDIR /worker

# Copy the code into the container
COPY worker.py /worker

# Install any required dependencies
RUN pip install zmq

# Set the entrypoint to the worker script
ENTRYPOINT ["python","-u", "/worker/worker.py"]