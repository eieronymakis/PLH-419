from flask import Flask, jsonify, render_template, request, redirect, make_response, session
import subprocess, json, os, datetime, requests, jwt, pytz
from kazoo.client import KazooClient,KazooState
from kazoo.exceptions import NoNodeError, NodeExistsError, SessionExpiredError
import mysql.connector

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "session_secret"

db = mysql.connector.connect(
    host="authentication_db",
    user="root",
    password="xyz123",
    database="authentication_db"   
)
db.autocommit = True
cursor = db.cursor()


# Create a directory in a known location to save files to.
uploads_dir = os.path.join(app.root_path, '../shared')
results_dir = os.path.join(app.root_path, '../results')

# Zookeeper
zk = KazooClient(hosts='172.25.0.40:2181')
zk.start()

task_path='/tasks'
job_path='/jobs'

#------------------------------------------------------
#                   /UPLOAD
#------------------------------------------------------
@app.route('/job', methods=['POST'])
def upload_file():

    body = request.get_json()
    job_file_name = body['job_file_name']
    input_file_name = body['input_file_name']

    # Get the active worker count
    subprocess.run(['./ClusterIPAdresses.sh'])
    with open('WorkerIPs.json', 'r') as f:
        workers = json.load(f)
    worker_count = len(workers['ips'])

    # Get timestamp
    tz = pytz.timezone('Europe/Athens')
    now = datetime.datetime.now(tz)
    timestamp = now.strftime("%H_%M_%S_%d_%m_%Y")

    # Set Job ZNode name
    job_name = f'job_{timestamp}'
    job_name_with_path = f'{job_path}/{job_name}'

    # Create Job ZNode
    zk.ensure_path(job_path)
    zk.create(job_name_with_path)

    timestamp_mysql = now.strftime('%Y-%m-%d %H:%M:%S')
    query=f"INSERT INTO jobs(name,date) values ('{job_name}','{timestamp_mysql}')"
    cursor.execute(query)

    chunks = split_file(os.path.join(uploads_dir, input_file_name), worker_count)

    for i in range(len(chunks)):
        task = {"job_file_name": job_file_name, "input_file_name": chunks[i], "job_znode":job_name}
        add_task(task, job_name_with_path, i+1, job_name)

    myResponse = make_response('Response')
    myResponse.status_code = 200

    return myResponse

def add_task(_data, _job_path, _index, _job_name):
    zk.ensure_path(task_path)

    tz = pytz.timezone('Europe/Athens')
    now = datetime.datetime.now(tz)
    timestamp = now.strftime("%H_%M_%S_%d_%m_%Y")

    task_name = f'task_{timestamp}_{_index}'
    task_path_with_name = f'{task_path}/{task_name}'
    data_bytes = json.dumps(_data).encode('utf-8')

    try:
        zk.create(task_path_with_name, data_bytes)
        zk.create(f'{_job_path}/{task_name}')

        timestamp_mysql = now.strftime('%Y-%m-%d %H:%M:%S')
        query=f"INSERT INTO tasks(name,jobName) values('{task_name}','{_job_name}')"
        cursor.execute(query)

    except NodeExistsError:
        pass
    return task_name

def split_file(file_path, num_chunks):
    
    tz = pytz.timezone('Europe/Athens')
    now = datetime.datetime.now(tz)
    timestamp = now.strftime("%H_%M_%S_%d_%m_%Y")

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

        with open(os.path.dirname(__file__)+'/../shared/'+timestamp+"_"+prefix+'_chunk_'+str(i+1)+'.txt', 'w')as f:
            f.writelines(chunk)
            files.append(timestamp+"_"+prefix+'_chunk_'+str(i+1)+'.txt')
    
    return files

#------------------------------------------------------
#                   /CALLBACK
#------------------------------------------------------
@app.route('/callback', methods=['POST'])
def callback():
    body = request.get_json()
    job_name  = body['job_name']
    query = f"UPDATE jobs SET status = 1 WHERE name = '{job_name}' "
    cursor.execute(query)

    myResponse = make_response('Response')
    myResponse.status_code = 200
    return myResponse



if __name__ == '__main__':  
    app.run(debug=True)
    