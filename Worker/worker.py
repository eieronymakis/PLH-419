import zmq
import time 
import pickle
from os import system
import os
from datetime import datetime
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'jobs'))

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    # Wait for a Python code string from the sender
    serialised_request_object = socket.recv()
    request_object = pickle.loads(serialised_request_object)

    # Save timestamp for job
    timestamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

    job_file_name = request_object['job_file_name']
    input_file_name = request_object['input_file_name']
    worker_index = request_object['worker_index']

    # Import code from job file and input data from input file
    with open('jobs/'+job_file_name, 'r') as f:
        code = f.read()
    exec(code)
    with open('jobs/'+input_file_name, 'r') as f:
        text = f.read()

    # Execute map, reduce save to json and keep track of execution time
    start = time.time()

    mapper_data = mapper(text)
    results = reducer(mapper_data)
    
    sorted_results = dict(sorted(results.items()))
    json_object = json.dumps(sorted_results)

    end = time.time()

    # Save Results 
    output_path="results/"+os.path.splitext(job_file_name)[0]+"_"+timestamp+"/worker_"+str(worker_index)+"_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as outfile:
        outfile.write(json_object)

    path_in_results = os.path.splitext(job_file_name)[0]+"_"+timestamp+"/worker_"+str(worker_index)+"_results.json"
    # Send Response
    response_object = {
        'elapsed' : str(end-start),
        'result_file_name' : path_in_results
    }
    serialised_response_object = pickle.dumps(response_object)
    socket.send(serialised_response_object)