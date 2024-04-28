from app import db, login_manager
from datetime import datetime
from  flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    
class Transaction(db.Model):
    id_t = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Float, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('categorie.id_cat'), nullable=False)
    categorie = db.relationship('Categorie', backref='categorie', lazy=True)



    def __repr__(self):
        return f"Transaction('{self.title}', '{self.montant}', '{self.date}')"
    
class Categorie(db.Model):
    id_cat = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Categorie('{self.title}', '{self.nom}')"
