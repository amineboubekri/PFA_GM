from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed   
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, DateTimeField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models  import User, Transaction, Categorie
from flask_login import current_user
from datetime import datetime


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken, choose another one")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already taken, choose another one")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if not username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is already taken, choose another one")
    
    def validate_email(self, email):
        if not email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is already taken, choose another one")

class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content =  TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class TransactionForm(FlaskForm):
    id = HiddenField('Transaction ID')
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    montant = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()], default=datetime.utcnow)
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    categorie = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.categorie.choices = [(c.id_cat, c.nom) for c in Categorie.query.all()]


class CategoryForm(FlaskForm):
    name = StringField('Titre', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('ajouter categorie')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    balance = 0
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is already taken, choose another one")
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is already taken, choose another one")

class UpdateBalanceForm(FlaskForm):
    balance = FloatField('Set New Balance', validators=[DataRequired()])
    montant = FloatField('Add Amount', validators=[DataRequired()])
    submit = SubmitField('Update Balance')