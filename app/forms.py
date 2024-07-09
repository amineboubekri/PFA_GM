from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed   
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, DateTimeField, SelectField, HiddenField, DecimalField
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
    title = StringField('Titre',validators=[DataRequired()])
    content =  TextAreaField('Contenu', validators=[DataRequired()])
    submit = SubmitField('Poster')

class TransactionForm(FlaskForm):
    id = HiddenField('Transaction ID')
    title = StringField('Titre', validators=[DataRequired(), Length(min=2, max=100)])
    montant = FloatField('Montant', validators=[DataRequired(), NumberRange(min=0)])
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()], default=datetime.utcnow)
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    categorie = SelectField('Categorie', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Confirmer')

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
    amount = DecimalField('Montant', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than 0')])
    operation = SelectField('Operation', choices=[('add', 'Ajouter'), ('reduce', 'Reduir')], validators=[DataRequired()])
    submit = SubmitField('Modifier Balance')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class UpdateCommentForm(FlaskForm):
    content = StringField('Contenu', validators=[DataRequired()])
    submit = SubmitField('Modifier')

class DeleteCommentForm(FlaskForm):
    submit = SubmitField('Supprimer')