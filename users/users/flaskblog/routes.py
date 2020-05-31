import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort ,jsonify,make_response
from flaskblog import app, db, bcrypt, ma
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm ,CategoryForm
from flaskblog.models import User, Post, Category, UserSchema ,CategorySchema,PostSchema
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename
from sqlalchemy import select, func
from datetime import datetime
from dateutil import parser
import pytz
import re
import base64
import requests
import json

request_count=0

def is_sha1(maybe_sha1):
    if len(maybe_sha1) != 40:
        return False
    try:
        sha_int = int(maybe_sha1, 16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/_count',methods=['GET','DELETE'])
def get_count():
    global request_count
    if(request.method=='GET'):
        message=[]
        print("call to request_count",request_count)
        message.append(request_count)
        resp=jsonify(message)
        resp.status_code=200
        return resp
    elif(request.method=='DELETE'):
        request_count=0
        print("reset request_count",request_count)
        message={}
        resp=jsonify(message)
        resp.status_code=200
        return resp
    else:
        message={}
        resp=jsonify(message)
        resp.status_code=405
        return resp

@app.route("/api/v1/users", methods=['POST'])
def add_user():
    global request_count
    request_count+=1
    if request.method != 'POST':
        return '', 405
    username = request.json['username']
    user = User.query.get(username)
    if user is not None:
        return '', 400
    password = request.json['password']
    #email = request.json['email']
    if(not username or not password):
        return '', 400
    if(is_sha1(password)==False):
        return '', 400    
    email = "default@default.com"
    #print('user is = ' , username)
    new_user = User(username,email,password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({}),201



@app.route('/api/v1/users', methods=['GET'])
def get_users():
    global request_count
    request_count+=1
    all_users = User.query.all()
    usernames = [user.username for user in all_users]
    return jsonify(usernames)
 

@app.route('/api/v1/users/<username>', methods=['DELETE'])
def delete_user(username):
    global request_count
    request_count+=1
    if request.method != 'DELETE':
        return '', 405
      
    user = User.query.get(username)
    print("hihihihihihi",user)
    if user is None:
        return '', 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({}),200
