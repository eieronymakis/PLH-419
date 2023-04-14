import zmq
import pickle
import sys
import json
from os import system

sys.path.append('utils')
from split import split_file

job_file_name = sys.argv[1]
input_file_name = sys.argv[2]

sockets = []

with open('IPAddresses.json', 'r') as f:
    IPAddresses = json.load(f)

for x in IPAddresses['containers'] :
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+x['ip']+":5555")
    sockets.append(socket)

worker_index = 1
chunk_index = 0

chunk_file_names = split_file('jobs/'+input_file_name, len(IPAddresses['containers']))

for s in sockets :

    request_object = {
        'job_file_name' : job_file_name,
        'input_file_name' : chunk_file_names[chunk_index],
        'worker_index' : worker_index
    }

    serialised_request_object = pickle.dumps(request_object)
    s.send(serialised_request_object)

    serialised_response_object = s.recv()
    response_object = pickle.loads(serialised_response_object)

    elapsed = response_object['elapsed']
    result_file_name = response_object['result_file_name']

    print('--------------------------------------')
    print('Elapsed : '+elapsed)
    print('Result File Name : '+result_file_name)
    print('--------------------------------------')

    worker_index+=1
    chunk_index+=1

for chunk_name in chunk_file_names:
    system('rm -rf ./jobs/'+chunk_name)


