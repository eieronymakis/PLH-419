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

    if task_data['mode'] == "map" :

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

        data_dict = {k: v for k, v in mapper_data}

        # Convert to JSON
        json_data = json.dumps(data_dict)

        mapper_output_filename = f"{task}_mapper_results.json"
        output_path=f"results/{mapper_output_filename}"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as outfile:
            outfile.write(json_data)

        query = f"UPDATE tasks SET result_filename = '{mapper_output_filename}', status = 1 WHERE name = '{task}'"
        cursor.execute(query)

    elif task_data['mode'] == "reduce":
        input_file_name = task_data['input_file_name']
        job_file_name = task_data['job_file_name']

        module_name = os.path.splitext(os.path.basename(job_file_name))[0]
        # Import Job Module
        job_module = importlib.import_module("shared."+module_name)
        
        with open('shared/'+input_file_name, 'r') as f:
            data = f.read()

        merged_dict = json.loads(data)

        reducer_data = job_module.reducer(merged_dict)

        reducer_output_filename = f"{task}_reducer_results.json"
        output_path=f"results/{reducer_output_filename}"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as outfile:
            json.dump(reducer_data, outfile)
        
        query = f"UPDATE tasks SET result_filename = '{reducer_output_filename}', status = 1 WHERE name = '{task}'"
        cursor.execute(query)
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
        print(f"Failed to release ongoing task {task}: {e}")
        return False
    
#-----------------------------------
# Remove task from Queue (Task Completed)
#-----------------------------------
def release_task_node(task):

    task_data = get_node_data(task)

    job_name = task_data['job_znode']
    task_mode = task_data['mode']
    job_filename = task_data['job_file_name']

    zk.delete(f'{task_path}/{task}')
    zk.delete(f'{job_path}/{job_name}/{task}')
    job_tasks = zk.get_children(f'{job_path}/{job_name}')
    
    if(task_mode == "map"):
        flag = False
        for job_task in job_tasks:
            job_task_data = get_node_data(job_task)
            if(job_task_data['mode'] == "map" ):
                flag = True
                break
        if flag == False:
            requests.post('http://172.25.0.44:3000/map_done', json={"job_name":job_name, "job_filename": job_filename})
    
    elif(task_mode == "reduce"):
        flag = False
        for job_task in job_tasks:
            job_task_data = get_node_data(job_task)
            if(job_task_data['mode'] == "reduce"):
                flag = True
                break
        if flag == False:
            requests.post('http://172.25.0.44:3000/callback', json={"job_name":job_name})

    return True
    
#-----------------------------------
# Function for adding tasks as ongoing 
#-----------------------------------
def acquire_task(task):
        # Check if the ongoing task znode already exists
        try:
            if zk.exists(f'{ongoing_path}/{task}'):
                # print(f"Task {task} is already ongoing")
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