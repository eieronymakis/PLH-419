import zmq
import pickle

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://172.24.0.3:5555")

job_code = open('job.py', 'r').read()
with open('input.txt', 'r') as f:
        data = f.readlines()

request_object = {'job':job_code,
                  'input':data}

serialised_request_object = pickle.dumps(request_object)

# Send the Python code as a string over the socket
socket.send(serialised_request_object)

# Wait for the result from the receiver
serialised_results = socket.recv()
final_results = pickle.loads(serialised_results)


print('-----------------------------------------')
print('ELAPSED')
print('-----------------------------------------')
print(final_results['elapsed'],' Seconds')
print('-----------------------------------------')
print('RESULT')
print('-----------------------------------------')
output = open("result", "w")
output.write(str(final_results['result']))
print('Saved in file : result')
print('-----------------------------------------')
