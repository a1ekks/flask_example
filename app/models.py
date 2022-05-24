from hashlib import md5 as md5_hash
from .tools.database import db
from sqlalchemy.orm import relation, backref, aliased
from sqlalchemy.dialects.postgres import DOUBLE_PRECISION, INET, BIGINT
from flask_login import UserMixin
from sqlalchemy import Sequence


class Permission:
    ADMINISTER = 0x80
    

class UsersGroups(db.Model):
    __tablename__ = 'users_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):
        return 'UserGroup {}'.format(self.name)


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True)
    pw = db.Column(db.String(255))
    auth = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(1024))
    is_admin = db.Column(db.Integer)
    is_active = db.Column(db.Integer)
    users_group_id = db.Column(db.Integer, db.ForeignKey('users_groups.id'))

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        if not self.users_group_id:
            self.users_group_id = db.session.query(UsersGroups.id).filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pw = md5_hash(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        password_hash = md5_hash(password.encode('utf-8')).hexdigest()
        return self.pw == password_hash

    def can(self, permissions):
        return self.users_group_id is not None and \
            (self.UsersGroups.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return 'User: {}'.format(self.login)

    UsersGroups = db.relationship('UsersGroups')


class UserSessions(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    session = db.Column(db.String(255), unique=True)
