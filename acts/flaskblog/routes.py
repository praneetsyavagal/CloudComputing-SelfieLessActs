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
#import binasci
from multiprocessing import Value
ACTID=0

USER_IP = "http://3.95.51.188"
ACT_IP = "http://54.162.187.144"
USER_PORT = "80"
ACT_PORT = "80"
counter = Value('i', 0)



def save_picture(form_picture):
    print("hihihihi")
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn)
    print('PATH     ',os.path.join(app.root_path))

    #output_size = (125, 125)
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/")
@app.route("/home",methods=['GET', 'POST'])
def home():
    print("came here")
    page = request.args.get('page', 1, type=int)
    cat_names = db.session.query(Category.name)
    l = cat_names.all()
    #print(l[0][0])
    l=[str(x[0]) for x in l]
    print(l)   
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
    #print("TYPEEPEPE : ", type(current_user), "Nam: ", current_user.get_id())
    
    return jsonify({"option_list": l, "curr_user": current_user.get_id()})
    return render_template('file://127.0.0.1/e$/testflask/flaskblog/templates/home.html', posts=post,option_list = l,current_user=current_user)

crash = 0
@app.route("/api/v1/_health", methods = ["GET"])
def health_database_status():
    #is_database_working = True
    #output = 'database is ok'
    global crash
    if crash == 1:
        return '', 500
    try:
        # to check database we will execute raw query
        #session = db.get_database_session()
        db.session.execute('SELECT 1')
    except Exception as e:
        #output = str(e)
        #is_database_working = False
        return 'error happs', 500
    return '', 200

@app.route("/api/v1/_crash", methods = ["POST"])
def _crash():
    global crash
    if crash==1:
        return '', 500
    crash = 1
    return '', 200


@app.route("/api/v1/_count",methods=['GET','DELETE'])
def count():
        global crash
        if crash==1:
                return '', 500
        if request.method == 'GET':
                return jsonify([counter.value]), 200
        elif request.method == 'DELETE':
                counter.value = 0
                return '', 200
        else:
                return '', 405

@app.route("/api/v1/acts/count", methods=['GET'])
def act_count():
    global crash
    if crash==1:
        return '', 500
    r = requests.get(ACT_IP + ':' + ACT_PORT + '/api/v1/categories')
    resp = json.loads(r.text)
    total_acts = 0
    for num in resp.values():
        total_acts = total_acts + num
    return jsonify([total_acts]), 200
     

@app.route("/category/<string:cat>/")
def category(cat):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    print("CURR")
    print(type(cat))
    filtered = Post.query.filter(Post.categoryName == cat).order_by(Post.timestamp.desc()).all()
    #print("isauthornot",current_user.is_authenticated)
    #has_liked = [current_user.has_liked_post(i) for i in filtered]

    #print("this is filtered",filtered[0].image_file)
    image_list=[i.image_file for i in filtered]
    content_list=[i.caption for i in filtered]
    id_list=[i.actId for i in filtered]
    no_upvotes = [i.upvotes for i in filtered]
    #likes_list=[i.upvotes for i in filtered]
    #print(likes_list[0])
    return jsonify({"img_list":image_list,"content_list":content_list,"category":cat, "leng" : len(image_list),"id_list": id_list,"n_upvotes":no_upvotes})
    #return render_template('category.html',current_user= current_user,image_list=image_list,content_list=content_list,category=cat, leng = len(image_list),id_list=id_list , likes_list= likes_list,post =has_liked)

@app.route("/about")
def about():
    with counter.get_lock():
        counter.value += 1
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    with counter.get_lock():
        counter.value += 1
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    with counter.get_lock():
        counter.value += 1
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    with counter.get_lock():
        counter.value += 1
    logout_user()
    return redirect(url_for('home'))




@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



#class UploadForm(Form):
   #file = FileField()
@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    with counter.get_lock():
        counter.value += 1
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)

@app.route("/post/new_cat", methods=['GET', 'POST'])
#@login_required
def new_cat():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    cat = Category(request.form["name"])
    db.session.add(cat)
    db.session.commit()
    return 200

@app.route("/post/new", methods=['GET', 'POST'])
#@login_required
def new_post():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    global ACTID
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    content = request.form["content"]
    cat_name = request.form["cat_name"]
    image_file = request.form["image_file"]
    print("content",content)
    print("IMG : ", image_file)
    post = Post(actId = ACTID ,caption=content,timestamp = datetime.utcnow(), user_id = 1,categoryName = cat_name , image_file = image_file, imgb64='defaultb64', username = 'default', upvotes = 0)
    ACTID = ACTID + 1
    db.session.add(post)
    db.session.commit()
    return 200


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.actId))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/api/v1/acts/delete",methods=['POST'])
#@login_required
def delete_post():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    print("deleting")
    post = Post.query.get_or_404(request.form["post_id"])
    #if post.author != current_user:
    #    abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

category_schema = CategorySchema(strict=True)
categories_schema = CategorySchema(many=True, strict=True)

post_schema = PostSchema(strict=True)
posts_schema = PostSchema( many=True,strict=True)

def isBase64(s):
    if(base64.b64encode(base64.b64decode(s)) == s):
        return True
    else:
        return False

def isBase641(sb):
    try:
        if type(sb) == str:
            sb_bytes = bytes(sb, 'ascii')
        elif type(sb) == bytes:
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False
'''
def isBase64(sb):
    try:
        base64.decodestring(sb)
    except binascii.Error:
        print("no correct base64")
'''        
'''def validate(date_text):
    try:
        datetime.strptime(date_text, '%d-%m-%Y:%S-%M-%H')
        return True
    except ValueError:
        return False'''
def is_sha1(maybe_sha1):
    if len(maybe_sha1) != 40:
        return False
    try:
        sha_int = int(maybe_sha1, 16)
    except ValueError:
        return False
    return True

@app.route("/api/v1/categories", methods=['POST'])
def add_category():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    name = request.json
    if len(name[0])== 0:
        return '',400
    new_category = Category(name[0])
    new_category = Category(name[0])
    exist_cat = Category.query.get(name[0])
    if exist_cat is not None:
        return '', 400
    db.session.add(new_category)
    db.session.commit()
   # onreturn category_schema.jsonify(new_category),201
    return jsonify({}),201

'''@app.route("/api/v1/categories", methods=['GET'])
def get_categories():
    all_users = Category.query.all()
    if len(all_users) == 0:
        return '',204
    result = categories_schema.dump(all_users)
    return jsonify(result.data),200'''

@app.route("/api/v1/categories/<category_name>", methods=['DELETE'])
def delete_category(category_name):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    #print(category_name)
    if request.method != 'DELETE':
        return '', 405
    exist_cat = Category.query.get(category_name)
    if exist_cat is None:
        return '', 400
    category = Category.query.get(category_name)
    print(category)
    db.session.delete(category)
    db.session.commit()
    return jsonify({}),200  
      
@app.route("/api/v1/acts", methods=['POST'])
def upload_acts():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    if "upvotes" in request.json.keys():
        print("upv")
        return '', 400
    id1 = request.json['actId']
    exist_id = Post.query.get(id1)
    if exist_id is not None:
        print("IDIDIDID")
        return '', 400
    #userid = request.json['userid']
    username = request.json['username']
    '''user=db.session.query(User).filter_by(username=username).all()
    if user is None:
        print("USERUSERS")
        return '', 400'''
    r = requests.get(USER_IP + ':' + USER_PORT + '/api/v1/users')
    resp = json.loads(r.text)
    print('USERS : ', resp)
    print("USERNAME: ", username)
    if username not in resp:
        return '', 400
    #print("hihihihihi",user)
    imgB64 = request.json['imgB64']
    if not isBase641(imgB64):
        print("HEYMAN")
        return '', 400
    print("HEYBRO")
    #user=User.query.get(username)
    #userid=user[0].id
    content = request.json['caption']
    cat_name = request.json['categoryName']
    if Category.query.get(cat_name) is None:
        return '', 400
    ds = request.json['timestamp']
    print("HHHHHHHHHHHHh",datetime.utcnow())
    date = datetime.strptime(ds, '%d-%m-%Y:%S-%M-%H')
    print("DATE : ", date)
    post=Post(id1,content,date,123,cat_name, 0,username,imgB64, "defaultimg")
    print("POST: ", post)
    db.session.add(post)
    db.session.commit()
    #return posts_schema.jsonify(post)  
    return jsonify({}),200
'''
@app.route("/api/v1/categories/<categoryName>/acts/size", methods=['GET'])
def get_no_of_acts(categoryName):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    if request.method != 'GET':
        return '', 405

    c=db.session.query(Post).filter_by(cat_name=categoryName).all()
    l = len(c)
    return "[" +str(l) + "]"
'''    
@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    if request.method != 'POST':
        return '', 405
    actid = request.json
    up = Post.query.get(actid[0])
    if up is None:
        return '', 400
    up.upvotes = up.upvotes + 1
    db.session.commit()
    return jsonify({}),200

@app.route("/upvote",methods=['POST'])
def upvote_f():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    #if request.method != 'POST':
    #    return '', 405
    #actid = request.json
    print("coming here")
    print("post_id",request.form["post_id"])
    up = Post.query.get(request.form["post_id"])
    if up is None:
        return '', 400
    up.upvotes = up.upvotes + 1
    print(up.upvotes)
    db.session.commit()


@app.route("/api/v1/acts/<actId>",methods=['DELETE'])
def del_act(actId):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    if request.method != 'DELETE':
        return '', 405

    act = Post.query.get(actId)
    if act is None:
        return '', 400
    db.session.delete(act)
    db.session.commit()
    return jsonify({}),200




@app.route("/api/v1/categories", methods=['GET'])
def get_categories():
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    all_users = Category.query.all()
    if len(all_users) == 0:
        return '',204
    result = categories_schema.dump(all_users)
    print(result)
    li=result.data
    d=dict()

    for document in li:
        #print(document)
        c=db.session.query(Post).filter_by(categoryName=document['name']).all()
        l = len(c)
        d[document['name']]=l
    return make_response(jsonify(d),200)
@app.route("/api/v1/categories/<categoryName>/acts/size", methods=['GET'])
def get_no_of_acts(categoryName):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    if request.method != 'GET':
        return '', 405
    exist_cat = Category.query.get(categoryName)
    if exist_cat is None:
        return '', 400
    c=db.session.query(Post).filter_by(categoryName=categoryName).all()
    l = len(c)
    return "[" +str(l) + "]",200


def timestampprocess(t):
    return t.strftime("%d-%m-%Y:%S-%M-%H")


@app.route("/api/v1/categories/<categoryName>/acts", methods=['GET'])
def get_acts(categoryName):
    global crash
    if crash==1:
        return '', 500
    with counter.get_lock():
        counter.value += 1
    #user=User.query.get(username)
    #userid=user.id
    d=dict()
    

    exist_cat = Category.query.get(categoryName)

    if exist_cat is None:
        return '', 400
    st = request.args.get('start',type=int,default = None)
    end=request.args.get('end',type=int,default = None)
    if st is not None and st < 1:
        return '', 400
    if st is not None and st > end:
        return '', 400
    if st is not None:
        if end - st + 1 >= 100:
            return '', 400
    cate=db.session.query(Post).filter_by(categoryName=categoryName).all()
    cate.sort(key=lambda x: x.timestamp, reverse=True)
    size = len(cate)
    if end is not None and end > size:
        return '', 400
    l=[]
    if st is None:
        st = 0
        end = size - 1
    for i in range(st-1, end):
        new_d = dict()
        new_d["actId"] = cate[i].actId
        new_d["username"] = cate[i].username
        new_d["caption"] = cate[i].caption
        new_d["upvotes"] = cate[i].upvotes
        new_d["imgB64"] = cate[i].imgb64
        new_d["timestamp"] = timestampprocess(cate[i].timestamp)
        l.append(new_d)
    return jsonify(l)
    '''
    if st==-1 and end==-1:
        return posts_schema.jsonify(cate)
    else:
        l = len(cate)
        if(st >=1 and end <= l and st<=end):
            return posts_schema.jsonify(cate[st:end+1])'''


