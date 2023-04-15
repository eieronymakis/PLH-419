import zmq
import pickle
import sys
import json
import os
from os import system

# Get the absolute path of the current script directory
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
# Define the absolute path of the jobs directory
JOBS_DIR = os.path.join(SCRIPT_DIR, 'jobs')
# Define the absolute path of the input file
INPUT_FILE = os.path.join(JOBS_DIR, sys.argv[2])


context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://172.25.0.10:5555")

job_file_name = sys.argv[1]
input_file_name = sys.argv[2]


request_object = {
        'job_file_name':  os.path.basename(job_file_name),
        'input_file_name':  os.path.basename(input_file_name),
        'worker_index': 1
    }

serialised_request_object = pickle.dumps(request_object)
socket.send(serialised_request_object)

serialised_response_object = socket.recv()
response_object = pickle.loads(serialised_response_object)

elapsed = response_object['elapsed']
result_file_name = response_object['result_file_name']

# print('--------------------------------------')
# print('Elapsed : '+elapsed)
# print('Result File Name : '+result_file_name)
# print('--------------------------------------')

print(result_file_name)
