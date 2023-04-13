import zmq
import pickle
import sys
import json
from os import system

job_file_name = sys.argv[1]
input_file_name = sys.argv[2]

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://172.20.0.3:5555")


request_object = {
        'job_file_name' : job_file_name,
        'input_file_name' : input_file_name,
        'worker_index' : 1
}

serialised_request_object = pickle.dumps(request_object)
socket.send(serialised_request_object)

serialised_response_object = socket.recv()
response_object = pickle.loads(serialised_response_object)

elapsed = response_object['elapsed']
result_file_name = response_object['result_file_name']

print('--------------------------------------')
print('Elapsed : '+elapsed)
print('Result File Name : '+result_file_name)
print('--------------------------------------')


