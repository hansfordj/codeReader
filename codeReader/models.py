from datetime import datetime, timedelta
from hashlib import md5
from flask import jsonify, url_for
from time import time
from flask_login import UserMixin
from passlib.hash import sha256_crypt
#import jwt  no python 3.5 support
from codeReader import db, login, app
import base64
import os

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {'items': [item.to_dict() for item in resources.items],
                '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
            'next': url_for(endpoint, page=page + 1, per_page=per_page,
                            **kwargs) if resources.has_next else None,
            'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                            **kwargs) if resources.has_prev else None
        }
        }
        return data

# User Model
class User(PaginatedAPIMixin, UserMixin, db.Model):
    '''
    User Model
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # expand for required client info (business contact, tax code, etc)
    info = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary='user_roles')

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }

        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):

        for field in ['username', 'email', 'info']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
   # example of many to many if required later
   # followed = db.relationship('User', secondary=followers,primaryjoin=(followers.c.follower_id == id),secondaryjoin=(followers.c.followed_id == id),backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):
        return 'Username: {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = sha256_crypt.encrypt(password)

    def check_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

   # def avatar(self, size):
   #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
   #     return 'https://www.gravatar.com/avatar/{}?d=mm&s={}'.format(digest, size)
    '''
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.secret_key, algorithm='HS256').decode('utf-8')
    '''
   # def follow(self, user):
   #    if not self.is_following(user):
   #         self.followed.append(user)

   # def unfollow(self, user):
   #     if self.is_following(user):
   #         self.followed.remove(user)

   # def is_following(self, user):
   #     return self.followed.filter(followers.c.followed_id == user.id).count() > 0

   # def followed_posts(self):
   #     followed = Post.query.join(followers, (followers.c.followed_id == Post.userid)).filter(followers.c.follower_id == self.id)
   #     own = Post.query.filter_by(userid=self.id)
   #     return followed.union(own).order_by(Post.timestamp.desc())

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
    '''
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.secret_key, algorithms=[
                            'HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    '''
    def get_roles(self):
            return str(self.roles)

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    def __repr__(self):
        return (self.name)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Code(db.Model):
    __tablename__ = 'code'
    id = db.Column(db.Integer, primary_key=True)
    codeType = db.Column(db.String(24))
    codeData = db.Column(db.String(128))
    description = db.Column(db.String(256))
    selection = db.Column(db.Boolean, default=False)
    logs = db.relationship('Log', backref='code_logs', lazy='dynamic')
    def serialize(self):
        return {
            'id': self.id,
            'codeType': self.codeType, 
            'codeData': self.codeData,
            'description': self.description,
            'selection': self.selection
        }
class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    codeid = db.Column(db.Integer, db.ForeignKey('code.id')) 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    match = db.Column(db.Boolean, default=False)
    def serialize(self):
        return {
            'id': self.id,
            'codeid': self.codeid, 
            'timestamp': self.timestamp,
            'match': self.match
        }
    