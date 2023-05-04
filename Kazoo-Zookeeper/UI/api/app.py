from flask import Flask, jsonify, render_template, request, redirect, make_response, session
import subprocess, json, os, datetime, requests, jwt
from kazoo.client import KazooClient,KazooState
from kazoo.exceptions import NoNodeError, NodeExistsError, SessionExpiredError

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "session_secret"

# Create a directory in a known location to save files to.
uploads_dir = os.path.join(app.root_path, '../shared')
results_dir = os.path.join(app.root_path, '../results')

# Zookeeper
zk = KazooClient(hosts='172.25.0.40:2181')
zk.start()

task_path='/tasks'

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

@app.route('/', methods=['GET'])
def root():
    return redirect('/login')

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


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login") 

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

@app.route('/workers', methods=['GET'])
def workers():
    if not 'username' in session:
        return redirect("/login")
    return render_template('workers.html')

@app.route('/jobs', methods=['GET'])
def job():
    if not 'username' in session:
        return redirect("/login")
    return render_template('jobs.html')

@app.route('/upload_files', methods=['POST'])
def upload_file():

    input_file = request.files['input_file']
    input_file.save(os.path.join(uploads_dir, input_file.filename))

    job_file = request.files['job_file']
    job_file.save(os.path.join(uploads_dir, job_file.filename))

    task = {"job_file_name": job_file.filename, "input_file_name": input_file.filename}
    add_task(task)

    myResponse = make_response('Response')
    myResponse.status_code = 200

    return myResponse



if __name__ == '__main__':  
    app.run(debug=True)
    