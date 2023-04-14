from flask import Flask, jsonify, render_template, request, redirect, make_response
import subprocess
import json
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Create a directory in a known location to save files to.
uploads_dir = os.path.join(app.root_path, '../jobs')

@app.route('/', methods=['GET'])
def root():
    return render_template('login.html')

@app.route('/worker_status', methods=['GET'])
def get_worker_status():
    subprocess.run(['./checkLiveWorkers.sh'])

    # Read the JSON output file
    with open('WorkerStatus.json', 'r') as f:
        worker_status = json.load(f)

    # Create a Flask response with the JSON data
    response = jsonify(worker_status)
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200

    return response

@app.route('/workers', methods=['GET'])
def workers():
    return render_template('workers.html')

@app.route('/jobs', methods=['GET'])
def job():
    return render_template('jobs.html')

@app.route('/upload_files', methods=['POST'])
def upload_file():

    input_file = request.files['input_file']
    input_file.save(os.path.join(uploads_dir, input_file.filename))

    job_file = request.files['job_file']
    job_file.save(os.path.join(uploads_dir, job_file.filename))
    try:
        subprocess.run(['python3', os.path.join(app.root_path, '../sendjob_cluster.py'), os.path.join(uploads_dir, job_file.filename), os.path.join(uploads_dir, input_file.filename)])
    except:
        print('Well shieeet')

    myResponse = make_response('Response')
    myResponse.status_code = 200

    return myResponse

if __name__ == '__main__':
    app.run(debug=True)
    