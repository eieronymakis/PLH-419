from kazoo.client import KazooClient,KazooState
from kazoo.exceptions import NoNodeError, NodeExistsError, SessionExpiredError
import json,datetime,time

task_path='/tasks'
ongoing_path='/ongoing'
zk = KazooClient(hosts='172.25.0.40:2181')
zk.start()

def add_task(_data):
    zk.ensure_path(task_path)
    now = datetime.datetime.now()
    timestamp = now.strftime("%H_%M_%S_%d_%m_%Y")
    task_name = f'task_{timestamp}'
    task_path_with_name = f'{task_path}/{task_name}'
    data_bytes = json.dumps(_data).encode('utf-8')
    try:
        zk.create(task_path_with_name, data_bytes)
    except NodeExistsError:
        pass
    return task_name

def get_tasks():
    zk.ensure_path(task_path)
    task_znodes = zk.get_children(task_path)
    print('\ntasks : ',task_znodes)
    zk.ensure_path(ongoing_path)
    ongoing_znodes = zk.get_children(ongoing_path)
    print('ongoing : ',ongoing_znodes)

def delete_task(_task_znode_path):
    zk.delete(f'{task_path}/{_task_znode_path}')

def clear_tasks():
    zk.delete(f'{task_path}', recursive=True)
    zk.delete(f'{ongoing_path}', recursive=True)
    get_tasks()


def main():
    # get_tasks()
    # clear_tasks()
    job = {"job_file_name":"job.py", "input_file_name":"input.txt"}
    add_task(job)
    time.sleep(2)
    add_task(job)    
    time.sleep(2)
    add_task(job)  
    time.sleep(2)
    add_task(job)
    time.sleep(2)
    add_task(job)


if __name__ == "__main__":
    main()



