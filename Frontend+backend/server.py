from flask import Flask, render_template, url_for, request, session, redirect,make_response,send_file
from flask_pymongo import PyMongo
import bcrypt
import json
import requests
from werkzeug import secure_filename
import os,io
import time
import base64
import hashlib
app = Flask(__name__)


@app.route('/')
def index():
	if session.get('username') != None:
		return render_template('index_in.html')
	return render_template('index.html')


@app.route('/homepage')
def homepage():	
	if session.get('username') != None:
		return render_template('index_in.html')
	app.logger.warning(session.get('username'))
	return render_template('index.html')

@app.route('/categoriespage')
def categoriespage():
	return render_template('categories.html')

@app.route('/uploadpage')
def uploadpage():
	return render_template('upload.html')

@app.route('/logout')
def logout():
	session.pop('username')
	return render_template('index.html')

@app.route('/loginpage')
def loginpage():
	return render_template('login.html')

@app.route('/signuppage')
def signuppage():
	return render_template('signup.html')

@app.route('/imgdisp/<category>')
def imgdisp(category):
	print(category)
	url = 'http://localhost:5775/api/v1/categories/'+category+'/acts'
	r = requests.get(url)
	reply=[]
	for i in r.json():
		reply.append(i)
	return render_template('imgdisp.html',reply=reply)

@app.route('/contact')
def contact():
	return render_template('contact.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.route('/upload',methods=['POST','GET'])
def upload():
	if request.method=='POST':
		if 'fileToUpload' not in request.files:
			return 'No image selected. <h3><a href="/uploadpage">Click here to go back to upload.</a></h3>'
		file = request.files['fileToUpload']
		if file.filename == '':
			return 'No selected file'
		if file and allowed_file(file.filename):
			print(file.filename)
			filename = secure_filename(file.filename)
			image_string = base64.b64encode(file.read())
			url = 'http://localhost:5775/api/v1/acts'
			category=request.form['category']
			description=request.form['description']
			payload = {'username':session['username']}
			payload['actId']=time.strftime('%d-%m-%Y:%S-%M-%H')
			payload['timestamp']=time.strftime('%d-%m-%Y:%S-%M-%H')
			payload['upvotes']=0
			payload['categoryName']=category
			payload['caption']=description
			payload['imgB64']=image_string
			headers = {'content-type': 'application/json'}
			r = requests.post(url, json=json.loads(json.dumps(payload)), headers=headers)
			print(r)
			if(r.status_code==201):
				return render_template('index_in.html')
			else:
				return 'Error occured during upload <h3><a href="/uploadpage">Click here to upload again</a></h3>'
		return 'Wrong file type. Please pick among png, jpeg, gif <h3><a href="/uploadpage">Click here to go back to upload.</a></h3>'
	return 'invalid'
	


@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		session['username']=request.form['username']
		return render_template('index_in.html')
		url = 'http://localhost:5775/login'
		user=request.form['username']
		password=request.form['pass']
		payload = {user:password}
		headers = {'content-type': 'application/json'}
		r = requests.post(url, json=json.dumps(payload), headers=headers)
		reply=r.json()
		if(reply['status']=='success'):
			session['username']=reply['username']
			return render_template('index_in.html')
		else:
			return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
		url = 'http://localhost:5775/api/v1/users'
		user=request.form['username']
		password=request.form['pass']
		cpassword=request.form['cpass']
		mail=request.form['mail']
		if(password==cpassword):
			payload = {'username':user}
			payload['password']=hashlib.sha1(password.encode()).hexdigest()
			payload['mail']=mail
			headers = {'content-type': 'application/json'}
			r = requests.post(url, json=json.loads(json.dumps(payload)), headers=headers)
			print(r.status_code)
			if(r.status_code==201):
				session['username']=reply['username']
				return render_template('index_in.html')
			else:
				return 'Username already exists. Please use another name. <h3><a href="/signuppage">Click here to go back to signup.</a></h3>'
		else:
			return 'Passwords don\'t match <h3><a href="/signuppage">Click here to go back to signup.</a></h3>'

@app.route('/upvote/<myid>',methods=['POST','GET'])
def upvote(myid):
	url = 'http://localhost:5775/api/v1/acts/upvote'
	payload=[]
	actId=myid
	payload.append(actId)
	headers = {'content-type': 'application/json'}
	r = requests.post(url, json=json.loads(json.dumps(payload)), headers=headers)
	return '1'
@app.route('/delete',methods=['POST','GET'])
def delete():
	print(request.form['deleteid'])
	if request.method == 'POST':
		myid=request.form['deleteid']
		user=request.form['user']
		if(user==session['username']):
			url = 'http://localhost:5775/api/v1/acts/'+str(myid)
			print(url)
			headers = {'content-type': 'application/json'}
			r = requests.delete(url, headers=headers)
	return render_template('categories.html')

if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.run(debug=True)
