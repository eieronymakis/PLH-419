import zmq
import time 
import pickle

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    # Wait for a Python code string from the sender
    serialised_request_object = socket.recv()
    request_object = pickle.loads(serialised_request_object)

    job = request_object['job']
    input = request_object['input']

    # Execute the Python code string
    exec(job)

    start = time.time()

    # Call the function from the Python code string
    intermediate_results = map_function(input)

    print('-------------------------------------------')
    print('Mapper Output')
    print('-------------------------------------------')
    print(intermediate_results)

    final_results = reduce_function(intermediate_results)

    print('-------------------------------------------')
    print('Reducer Output')
    print('-------------------------------------------')
    print(final_results)

    end = time.time()

    response = {'elapsed':end-start,
                'result':final_results}
    
    serialised_response = pickle.dumps(response)

    # Send the result back to the sender
    socket.send(serialised_response)