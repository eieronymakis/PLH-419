import zmq
import time 
import pickle
from os import system
import os
from datetime import datetime
import json
from functools import reduce
import sys

sys.path.append('jobs')

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    # Wait for a Python code string from the sender
    serialised_request_object = socket.recv()
    request_object = pickle.loads(serialised_request_object)

    timestamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

    job_file_name = request_object['job_file_name']
    input_file_name = request_object['input_file_name']
    worker_index = request_object['worker_index']

    import_mapper = 'from '+job_file_name.rsplit( ".", 1 )[ 0 ]+' import mapper'
    import_reducer = 'from '+job_file_name.rsplit( ".", 1 )[ 0 ]+' import reducer'
    exec(import_mapper)
    exec(import_reducer)

    start = time.time()

    with open('jobs/'+input_file_name, 'r') as f:
        text = f.read()

    mapper_data = mapper(text)
    results = reducer(mapper_data)
    
    sorted_results = dict(sorted(results.items()))
    json_object = json.dumps(sorted_results)

    end = time.time()

    output_path="results/"+os.path.splitext(job_file_name)[0]+"_"+timestamp+"/worker_"+str(worker_index)+"_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as outfile:
        outfile.write(json_object)

    system('rm -rf __pycache__')

    response_object = {
        'elapsed' : str(end-start),
        'result_file_name' : 'results_'+timestamp
    }

    serialised_response_object = pickle.dumps(response_object)

    socket.send(serialised_response_object)