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
#                   /ROOT
#------------------------------------------------------
@app.route('/', methods=['GET'])
def root():
    return redirect('/login')

#------------------------------------------------------
#                   /LOGIN
#------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']

        response = requests.post('http://172.25.0.41:3000/auth', json={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            response_body = response.json()
            token = response_body['Token']
            jwt_data = jwt.decode(token, "DISTRIBUTEDSYSTEMSPROJECT1", algorithms="HS256")
            session['username']=jwt_data['username']
            return redirect('/workers')
        else:
            return redirect('/login')

#------------------------------------------------------
#                   /LOGOUT
#------------------------------------------------------
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login") 


#------------------------------------------------------
#                   /SIGNUP
#------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['uname']
        password=  request.form['pass']
        email = request.form['email']

        response = requests.post('http://172.25.0.41:3000/register', json = {
            "password": password,
            "email": email,
            "role":"user",
            "username": username
        })

        return redirect("/login")
    else:
        myResponse = make_response('Response')
        myResponse.status_code = 404

        return myResponse


#------------------------------------------------------
#                   /WORKERS
#------------------------------------------------------
@app.route('/workers', methods=['GET'])
def workers():
    if not 'username' in session:
        return redirect("/login")
    return render_template('workers.html')

@app.route('/get_workers', methods=['GET'])
def get_worker_status():
    subprocess.run(['./ClusterIPAdresses.sh'])

    # Read the JSON output file
    with open('WorkerIPs.json', 'r') as f:
        workers = json.load(f)

    # Create a Flask response with the JSON data
    response = jsonify(workers)
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200

    return response

#------------------------------------------------------
#                   /JOBS
#------------------------------------------------------
@app.route('/jobs', methods=['GET'])
def job():
    if not 'username' in session:
        return redirect("/login")
    return render_template('jobs.html')

#------------------------------------------------------
#                   /UPLOAD
#------------------------------------------------------
@app.route('/upload_files', methods=['POST'])
def upload_file():

    input_file = request.files['input_file']
    input_file.save(os.path.join(uploads_dir, input_file.filename))

    job_file = request.files['job_file']
    job_file.save(os.path.join(uploads_dir, job_file.filename))


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

    chunks = split_file(os.path.join(uploads_dir, input_file.filename), worker_count)

    for i in range(len(chunks)):
        task = {"job_file_name": job_file.filename, "input_file_name": chunks[i], "job_znode":job_name}
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


@app.route('/results', methods=['GET'])
def results():
    if not 'username' in session:
        return redirect("/login")
    return render_template('results.html')

@app.route('/results/<job_name>', methods=['GET'])
def job_results(job_name):
    if not 'username' in session:
        return redirect("/login")

    query = f"SELECT * FROM tasks WHERE jobName = '{job_name}'"
    cursor.execute(query)

    rows = cursor.fetchall()

    rows_json = []
    for row in rows:
        row_dict = dict(zip(cursor.column_names, row))
        rows_json.append(row_dict)


    return render_template('result_files.html', data=rows_json)
#------------------------------------------------------
#                   /JOB_STATUS
#------------------------------------------------------
@app.route('/job_status', methods=['GET'])
def job_status():
    query = f"SELECT * FROM jobs"
    cursor.execute(query)

    rows = cursor.fetchall()

    rows_json = []
    for row in rows:
        row_dict = dict(zip(cursor.column_names, row))
        rows_json.append(row_dict)

    response = jsonify(rows_json)
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200

    return response




if __name__ == '__main__':  
    app.run(debug=True)
    