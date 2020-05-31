from flask import Flask, render_template, url_for, request, session, redirect,jsonify,make_response
from flask_pymongo import PyMongo
import json
import datetime
import base64
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'api'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/api'
mongo = PyMongo(app)
def isBase64(sb):
	try:
		base64.b64encode(base64.b64decode(sb))==sb
	except Exception:
		return False
	else:
		return True

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y:%S-%M-%H')
        return True
    except ValueError:
        return False
def is_sha1(maybe_sha1):
    if len(maybe_sha1) != 40:
        return False
    try:
        sha_int = int(maybe_sha1, 16)
    except ValueError:
        return False
    return True


@app.route('/api/v1/users',methods=['GET','POST','PUT','DELETE'])
def addusr():
	if request.method == 'POST':
		content=request.get_json()
		if content['username'] and content['password']:
			pwd=content['password'].lower()
			if is_sha1(pwd)==False:
				return jsonify({}), 400
			users=mongo.db.usersapi
			existing_user = users.find_one({'username' : content['username']})
			if existing_user is None:
				users.insert({"username":content['username'],"password":pwd})
				return make_response(jsonify({}),201)
			else:
				return jsonify({}), 400
		else:
			return jsonify({}), 400
	else:
		return jsonify({}), 405
@app.route('/api/v1/users/<string:username>',methods=['GET','POST','PUT','DELETE'])
def remusr(username):
	if request.method == 'DELETE':
		users=mongo.db.usersapi
		existing_user = users.find_one({'username' : username})
		if existing_user is not None:
			users.delete_one({'username':username})
			return make_response(jsonify({}),200)
		else:
			return jsonify({}), 400
	else:
		return jsonify({}), 405
@app.route('/api/v1/categories',methods=['GET','POST','PUT','DELETE'])
def category():
	if request.method == 'GET':
		#check for request type
		cat=mongo.db.categoriesapi			
		if cat.count()==0:
			return make_response(jsonify({}),204)
		catlist=cat.find({})
		d=dict()
		for document in catlist:
			d[document['category']]=document['no_of_acts']
		return make_response(jsonify(d),200)
	
	elif request.method=='POST':
		cat=mongo.db.categoriesapi
		if len(request.json) != 0:
			existing_cat = cat.find_one({'category' : request.json[0]})
			if existing_cat is None:
				cat.insert({'category':request.json[0], 'no_of_acts':0})
				return make_response(jsonify({}),201)
			return jsonify({}), 400
		else:
			return jsonify({}), 400
	else:
		return jsonify({}),405
@app.route('/api/v1/categories/<string:categoryName>',methods=['GET','POST','PUT','DELETE'])
def remcategory(categoryName):
	if request.method == 'DELETE':
		cat=mongo.db.categoriesapi
		existing_cat = cat.find_one({'category' : categoryName})
		if existing_cat is not None:
			cat.delete_one({'category' : categoryName})
			return make_response(jsonify({}),200)
		else:
			return jsonify({}), 400
	else:
		return jsonify({}), 405
@app.route('/api/v1/categories/<string:categoryName>/acts', methods=['GET','POST','PUT','DELETE'])
def getacts(categoryName):
	if request.method=='GET':
		startRange=request.args.get('start',type=int,default=None)
		endRange=request.args.get('end',type=int,default=None)
		if((startRange==None) or (endRange==None)):
			cat=mongo.db.categoriesapi
			existing_cat = cat.find_one({'category' : categoryName})
			if existing_cat is not None:
				actref=mongo.db.actsapi
				if actref.count()==0:
					return jsonify([]), 204
				#dont know if this is required
				if actref.count()>100:
					return jsonify([]),413
				acts=actref.find({'categoryName':categoryName})
				if acts.count()==0:
					return jsonify([]),204
				if acts.count()>100:
					return jsonify([]),413
				actlist=[]
				for i in acts:
					if mongo.db.usersapi.find_one({'username':i['username']}) is None:
						return jsonify([]),204
					del i['categoryName']
					del i['_id']
					actlist.append(dict(i))
				return json.dumps(actlist),200
			else:
				return jsonify([]), 400
		else:
			if int(endRange)-int(startRange)+1 <=100:
				cat=mongo.db.categoriesapi
				existing_cat = cat.find_one({'category' : categoryName})
				if existing_cat is not None:
					actref=mongo.db.actsapi
					if startRange<1 and endRange>actref.count():
						return jsonify([]), 400
					if startRange>endRange:
						return jsonify([]), 400
					if actref.count()==0:
						return jsonify([]),204
					acts=actref.find({'categoryName':categoryName})
					if acts.count()==0:
						return jsonify([]),204
					if acts.count()>100:
						return jsonify([]),413
					if startRange<1:
						return jsonify([]), 400
					if endRange>acts.count():
						return jsonify([]), 400
					actlist=[]
					for i in acts:
						if mongo.db.usersapi.find_one({'username':i['username']}) is None:
							return jsonify([]), 204
						del i['_id']
						del i['categoryName']
						actlist.append(dict(i))
					actrange=actlist[startRange-1:endRange]
					return make_response(jsonify(actrange),200)
				else:
					return jsonify({}),400
			else:
				return jsonify([]), 413
	else:
		return jsonify([]), 405
@app.route('/api/v1/categories/<string:categoryName>/acts/size', methods=['GET','POST','PUT','DELETE'])
def list_no_of_acts(categoryName):
	#doubt if cat is empty or no acts in cat must return 204
	if request.method=='GET':
		cat=mongo.db.categoriesapi
		if cat.count()==0:
			return jsonify([]),204
		existing_cat = cat.find_one({'category' : categoryName})
		if existing_cat is not None:
			num=existing_cat['no_of_acts']
			return make_response(jsonify([int(num)]),200)
		else:
			return jsonify([]), 204
	else:
		return jsonify([]), 405
@app.route('/api/v1/acts/upvote',methods=['GET','POST','PUT','DELETE'])
def upvote():
	if request.method=='POST':
		actref=mongo.db.actsapi
		existing_act = actref.find_one({'actId' : request.json[0]})
		if existing_act is not None:
			actref.update({'actId':request.json[0]},{'$inc':{'upvotes':1}})
			return make_response(jsonify({}),200)
		return jsonify({}), 400
	else:
		return jsonify({}), 405
@app.route('/api/v1/acts/<actId>',methods=['GET','POST','PUT','DELETE'])
def delact(actId):
	if request.method=='DELETE':
		actref=mongo.db.actsapi
		existing_act = actref.find_one({'actId':actId})
		if existing_act is not None:
			cat=mongo.db.categoriesapi
			cat.update({'category' : existing_act['categoryName']},{'$inc':{'no_of_acts':-1}})
			actref.delete_one({'actId':actId});
			return make_response(jsonify({}),200)
		return jsonify({}), 400
	else:
		return jsonify({}), 405
@app.route('/api/v1/acts',methods=['GET','POST','PUT','DELETE'])
def insertact():
	if request.method=='POST':
		if(request.is_json):
			actId=request.json.get('actId')
			username=request.json.get('username')
			category=request.json.get('categoryName')
			caption=request.json.get('caption')
			timestamp=request.json.get('timestamp')
			imgB64=request.json.get('imgB64')
			upvotes=request.json.get('upvotes')
		else:
			received=json.loads(request.data)
			username=received['username']
			actId=received['actId']
			category=received['categoryName']
			caption=received['caption']
			timestamp=received['timestamp']
			imgB64=received['imgB64']
		if(not(actId) or not(username) or not(caption) or not(timestamp) or (validate(timestamp)==False) or not(isBase64(imgB64)) ):
			if(request.is_json):
				return jsonify({}),400
			else:
				return jsonify(status="Fields empty or wrong format"),400
		users=mongo.db.usersapi
		existing_user = users.find_one({'username' : request.json['username']})
		if existing_user is None:
			return jsonify({}), 400
		cat=mongo.db.categoriesapi
		existing_cat = cat.find_one({'category' : request.json['categoryName']})
		if existing_cat is None:
			return jsonify({}), 400
		actref=mongo.db.actsapi
		existing_act = actref.find_one({'actId':request.json['actId']})
		if existing_act is None:			
			cat.update({'category' : request.json['categoryName']},{'$inc':{'no_of_acts':1}},upsert=True)
			jsondata=request.json
			jsondata['upvotes']=0
			actref.insert(jsondata)
			return make_response(jsonify({}),201)
		return jsonify({}), 400
	else:
		return jsonify({}), 405

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5775,debug=True)
