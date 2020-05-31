from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog import ma


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, default = 123)
    username = db.Column(db.String(20), unique=True, nullable=True, primary_key=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    #image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    liked = db.relationship('PostLike',foreign_keys='PostLike.user_id',backref='user', lazy='dynamic')
    #def __repr__(self):
    #   return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')

class Category(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False,primary_key=True)
    num_acts = db.Column(db.Integer, nullable=True)
    posts = db.relationship('Post', backref='cat', lazy=True)
    def __init__(self, name):
        self.name = name

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('name',)

    #def __repr__(self):
    #   return f"Category('{self.name}', '{self.num_acts}')"

class PostLike(db.Model):
    __tablename__ = 'post_like'
    actId = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.actId'))

class Post(db.Model):
    actId = db.Column(db.Integer, primary_key=True)
    #title = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    caption = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('user.username'),nullable = False)
    categoryName = db.Column(db.Integer, db.ForeignKey('category.name'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    imgb64 = db.Column(db.String(500), nullable=False, default='defaultb64')
    upvotes = db.relationship('PostLike', backref='post', lazy='dynamic')
    upvotes = db.Column(db.Integer, nullable=True, default = 0)
    def __repr__(self):
        return "Post('{self.timestamp}','{self.caption}','{self.image_file}')"

    def __init__(self,actId,caption,timestamp,user_id, categoryName, upvotes,username,imgb64, image_file):
        self.actId = actId
        self.caption = caption
        self.timestamp = timestamp
        self.user_id = user_id
        self.categoryName = categoryName
        self.upvotes = upvotes
        self.username = username
        self.imgb64 = imgb64
        self.image_file = image_file
        

class PostSchema(ma.Schema):
    class Meta:
        fields = ('actId','username','timestamp', 'caption','upvotes', 'imgb64')

