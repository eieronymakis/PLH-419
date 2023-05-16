import time, json, os, importlib, requests
from kazoo.client import KazooClient

import mysql.connector

db = mysql.connector.connect(
    host="authentication_db",
    user="root",
    password="xyz123",
    database="authentication_db"   
)
db.autocommit = True
cursor = db.cursor()

#-----------------------------------
# Connect to Zookeeper
#-----------------------------------
zk = KazooClient(hosts='172.25.0.40:2181')
zk.start()

#-----------------------------------
# Queue paths
#-----------------------------------
task_path = '/tasks'
ongoing_path = '/ongoing'
job_path = '/jobs'

#-----------------------------------
# Read task data from znode
#-----------------------------------
def get_node_data(node_path):
    bytes, stat = zk.get(f'{task_path}/{node_path}')
    return json.loads(bytes.decode('utf-8'))

#-----------------------------------
# Function we run based on the job (task) data
#-----------------------------------
def process_task(task):
    task_data = get_node_data(task)
    #-----------------------------------
    #   MapReduce Code Functionality
    #-----------------------------------
    input_file_name = task_data['input_file_name']
    job_file_name = task_data['job_file_name']

    module_name = os.path.splitext(os.path.basename(job_file_name))[0]

    # Import Job Module
    job_module = importlib.import_module("shared."+module_name)

    # Read Input File
    with open('shared/'+input_file_name, 'r') as f:
        text = f.read()

    mapper_data = job_module.mapper(text)
    results = job_module.reducer(mapper_data)

    sorted_results = dict(sorted(results.items()))
    json_object = json.dumps(sorted_results)

    # Save Results 

    result_filename = f"{task}_results.json"
    output_path=f"results/{result_filename}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as outfile:
        outfile.write(json_object)


    query = f"UPDATE tasks SET result_filename = '{result_filename}', status = 1 WHERE name = '{task}'"
    cursor.execute(query)

    print ('Task ',task,' Done')
    return True

#-----------------------------------
# Remove task from ongoing Queue (Task Completed/Failed)
#-----------------------------------
def release_ongoing_node(task):
    try:
        # Remove the ongoing task znode to release the task
        zk.delete(f'{ongoing_path}/{task}')
        return True
    except Exception as e:
        print(f"Failed to release task {task}: {e}")
        return False
    
#-----------------------------------
# Remove task from Queue (Task Completed)
#-----------------------------------
def release_task_node(task):
    try:
        task_data = get_node_data(task)
        job_name = task_data['job_znode']

        zk.delete(f'{job_path}/{job_name}/{task}')

        job_tasks = zk.get_children(f'{job_path}/{job_name}')

        if(len(job_tasks) == 0):
            requests.post('http://172.25.0.44:3000/callback', json={"job_name" : job_name})

        # Remove the task znode, task is complete
        zk.delete(f'{task_path}/{task}')
        return True
    except Exception as e:
        print(f"Failed to release task {task}: {e}")
        return False
    
#-----------------------------------
# Function for adding tasks as ongoing 
#-----------------------------------
def acquire_task(task):
        # Check if the ongoing task znode already exists
        try:
            if zk.exists(f'{ongoing_path}/{task}'):
                print(f"Task {task} is already ongoing")
                return False
            # Create an ephemeral znode to acquire the task
            zk.create(f'{ongoing_path}/{task}', ephemeral=True)
            return True
        except Exception as e :
            return False

#-----------------------------------
# Watcher function
#-----------------------------------
def watcher():
    # Get the new children task znodes
    tasks = zk.get_children('/tasks')
    for task in tasks:
        # Try to get one of the tasks
        if acquire_task(task):
            #-----------------------------------
            # Processing Failed
            #-----------------------------------
            if not process_task(task):
                #-----------------------------------
                # If processing failed we have to remove the ongoing znode in order
                # for some other worker to get hold of the task
                #-----------------------------------
                release_ongoing_node(task)
                print('Worker failed processing the task')

            #-----------------------------------
            # Processing Completed  
            #-----------------------------------
            else:
                #-----------------------------------
                # Task is complete that means that task znode needs to be deleted
                # Also we have to remove the task from ongoing
                #-----------------------------------
                release_task_node(task)
                release_ongoing_node(task)

            return  # Exit the function after processing one task
        
    # If no tasks were acquired, print a message
    #print("No tasks available to acquire")

# Continuously watch for new tasks
while True:
    
    # Ensure task and ongoing znode queues exist
    zk.ensure_path(task_path)
    zk.ensure_path(ongoing_path)

    watcher()

    # Search every 3 seconds
    time.sleep(3)

# Close the connection to ZooKeeper
zk.stop()