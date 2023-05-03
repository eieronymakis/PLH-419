import time, json
from kazoo.client import KazooClient

zk = KazooClient(hosts='172.25.0.40:2181')
zk.start()

task_path = '/tasks'
ongoing_path = '/ongoing'

# Util function to get the task json data
def get_task_data(_task_znode_path):
    bytes, stat = zk.get(f'{task_path}/{_task_znode_path}')
    json_data = json.loads(bytes.decode('utf-8'))
    return json_data

# Do something based on the task data
def process_task(task):
    znode_data = get_task_data(task)
    print(f"Processing task: {task}")
    print(znode_data)
    print(f"Finished task: {task}")
    return True

# Remove a task from on-going
def release_task(task):
    try:
        # Remove the ongoing task znode to release the task
        zk.delete(f'{ongoing_path}/{task}')
        return True
    except Exception as e:
        print(f"Failed to release task {task}: {e}")
        return False
    
# A worker holds the task
def acquire_task(task):
    try:
        # Check if the ongoing task znode already exists
        if zk.exists(f'{ongoing_path}/{task}'):
            print(f"Task {task} is already ongoing")
            return False
        # Create an ephemeral znode to acquire the task
        zk.create(f'{ongoing_path}/{task}', ephemeral=True)
        return True
    except Exception as e:
        print(f"Failed to acquire task {task}: {e}")
        return False

# Task Assignment Logic
def my_callback(event):
    tasks = zk.get_children('/tasks')
    # Get the first child (i.e., task) from the list of children
    for task in tasks:
        if acquire_task(task):
            if not process_task(task):
                # If task processing failed, release the task
                release_task(task)
                print('Worker failed processing the task')
            else:
                print('Done')
                # If task processing succeeded, release the task
                time.sleep(60)
                zk.delete(f"{task_path}/{task}")
                release_task(task)
            return  # Exit the function after processing one task
    # If no tasks were acquired, print a message
    print("No tasks available to acquire")

# Continuously watch for new tasks
while True:
    # Get the available task znodes
    zk.ensure_path(task_path)
    zk.ensure_path(ongoing_path)
    tasks = zk.get_children(task_path, watch=my_callback)
    # Wait for a few seconds before checking for new tasks again
    time.sleep(3)

# Close the connection to ZooKeeper
zk.stop()