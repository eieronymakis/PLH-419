from flask import Flask, jsonify, render_template
import subprocess
import json

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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
def x():
    return render_template('workerStatus.html')

if __name__ == '__main__':
    app.run(debug=True)
    