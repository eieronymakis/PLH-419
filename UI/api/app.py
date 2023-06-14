from flask import Flask, jsonify, render_template, request, redirect, make_response, session, send_file
import subprocess, json, os, datetime, requests, jwt, pytz
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


    response = requests.post("http://172.25.0.44:3000/job",json={
        "job_file_name":job_file.filename, 
        "input_file_name": input_file.filename
    })

    myResponse = make_response('Response')
    myResponse.status_code = 200

    return myResponse

#------------------------------------------------------
#                   RESULTS
#------------------------------------------------------
@app.route('/results', methods=['GET'])
def results():
    if not 'username' in session:
        return redirect("/login")
    return render_template('results.html')

@app.route('/results/<job_name>', methods=['GET'])
def job_results(job_name):
    if not 'username' in session:
        return redirect("/login")

    query = f"SELECT * FROM tasks WHERE jobName = '{job_name}' AND mode='reduce' "
    cursor.execute(query)

    rows = cursor.fetchall()

    rows_json = []

    for row in rows:
        row_dict = dict(zip(cursor.column_names, row))
        rows_json.append(row_dict)

    
    result_dict = {}
    for item in rows_json:
        with open(f"{results_dir}/{item.get('result_filename')}") as f:
            data = json.loads(f.read())
            for key,value in data.items():
                    result_dict[key] = value

    file_name = f"{job_name}_result.json"
    output_path=f"{results_dir}/{file_name}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as outfile:
        outfile.write(json.dumps(result_dict))


    return render_template('result_files.html', data=rows_json, filename=file_name)

#------------------------------------------------------
#                   /DOWNLOAD
#------------------------------------------------------
@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    output_path=f"{results_dir}/{filename}"
    return send_file(output_path, as_attachment=True)



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
    