from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# models.py
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    total_transactions = db.Column(db.Float, nullable=False, default=0.0)
    posts = db.relationship('Post', backref='author', lazy=True)
    transactions = db.relationship('Transaction', backref='owner', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    def has_liked_post(self, post):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.post_id == post.id).count() > 0


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.balance}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Float, nullable=False)  
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('categorie.id_cat'), nullable=False)
    categorie = db.relationship('Categorie', backref='transactions', lazy=True)  

    def __repr__(self):
        return f"Transaction('{self.title}', '{self.montant}', '{self.date}')"
    
class Categorie(db.Model):
    id_cat = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Categorie('{self.nom}')"
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_liked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)