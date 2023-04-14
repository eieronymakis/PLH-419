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
# Define the absolute path of the IPAddresses.json file
IP_ADDRESSES_FILE = os.path.join(SCRIPT_DIR, 'IPAddresses.json')
# Define the absolute path of the split.py file
SPLIT_FILE = os.path.join(SCRIPT_DIR, 'utils', 'split.py')
# Define the absolute path of the input file
INPUT_FILE = os.path.join(JOBS_DIR, sys.argv[2])

def split_file(file_path, num_chunks):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    num_lines = len(lines)
    lines_per_chunk = num_lines // num_chunks

    files = []

    basename = os.path.basename(file_path)
    prefix = os.path.splitext(basename)[0]

    for i in range(num_chunks):
        start_idx = i * lines_per_chunk
        end_idx = (i+1) * lines_per_chunk if i < num_chunks-1 else num_lines
        chunk = lines[start_idx:end_idx]

        with open(os.path.join(JOBS_DIR, prefix+'_chunk_'+str(i+1)+'.txt'), 'w') as f:
            f.writelines(chunk)
            files.append(prefix+'_chunk_'+str(i+1)+'.txt')

    return files

job_file_name = sys.argv[1]
input_file_name = sys.argv[2]

sockets = []

with open(IP_ADDRESSES_FILE, 'r') as f:
    IPAddresses = json.load(f)

for x in IPAddresses['containers']:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+x['ip']+":5555")
    sockets.append(socket)

worker_index = 1
chunk_index = 0

chunk_file_names = split_file(INPUT_FILE, len(IPAddresses['containers']))

for s in sockets:
    request_object = {
        'job_file_name':  os.path.basename(job_file_name),
        'input_file_name':  os.path.basename(chunk_file_names[chunk_index]),
        'worker_index': worker_index
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

    worker_index += 1
    chunk_index += 1

for chunk_name in chunk_file_names:
    os.remove(os.path.join(JOBS_DIR, chunk_name))