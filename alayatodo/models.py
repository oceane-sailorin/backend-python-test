from . import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.id) 

class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.String(255)) 
    completed = db.Column(db.Integer, nullable=False, default=0) 

    def __init__(self, user_id, description,completed):
        self.user_id = user_id 
        self.description = description 
        self.completed = completed 

    def __repr__(self):
        return '<Todo %r>' % (self.description) 