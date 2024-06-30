import os
import secrets
from datetime import datetime
from PIL import Image 
from app.models import User, Post, Transaction, Categorie
from flask import render_template, url_for, flash, redirect, request, abort
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, TransactionForm, CategoryForm, UpdateBalanceForm
from app import app, db, bcrypt
from sqlalchemy import extract
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
@app.route("/home")
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('home.html',nav="yes", posts=posts)


@app.route("/about")
def about():
    return render_template('about.html',nav="yes", title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can Log In now', 'success')
        return redirect(url_for('login'))
    return render_template('register2.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
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
    return render_template('login2.html', title='Login',nav='no', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125) 
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path) 
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit() and form.submit.data:
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

    now = datetime.now()
    selected_year = request.args.get('year', now.year, type=int)
    selected_month = request.args.get('month', now.month, type=int)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.date) == selected_year,
        extract('month', Transaction.date) == selected_month
    ).all()

    # calculer spending per category
    category_spending = db.session.query(
        Categorie.nom, db.func.sum(Transaction.montant)
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.date) == selected_year,
        extract('month', Transaction.date) == selected_month
    ).group_by(Categorie.nom).all()

    # variables de chart
    categories = [category for category, _ in category_spending]
    amounts = [amount for _, amount in category_spending]

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, transactions=transactions, balance=current_user.balance, nav="yes", selected_year=selected_year, selected_month=selected_month, now=now, categories=categories, amounts=amounts)


@app.route("/account/update", methods=['GET', 'POST'])
@login_required
def update_account():
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
    return render_template('update_account.html', title='Update Account', image_file=image_file, form=form, nav="yes")

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm() 
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created ', 'success')
        return redirect(url_for('home'))    
    return render_template('create_post.html',nav="yes", title='New Post', form=form, legend="New Post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, nav="yes")

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
        flash('The post has been updated!', 'success')
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',nav="yes", title='Update Post', form=form, legend="Update Post")

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_posts.html',nav="yes", posts=posts, user=user)

@app.route("/transaction/new", methods=['GET', 'POST'])
@login_required
def new_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            title=form.title.data,
            montant=form.montant.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id,
            cat_id=form.categorie.data
        )
        db.session.add(transaction)
        
        current_user.balance += transaction.montant 
        db.session.commit()
        
        flash('Your transaction has been added!', 'success')
        return redirect(url_for('account'))
    return render_template('transaction.html', title='New Transaction', form=form, nav="yes")

@app.route("/categories", methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Categorie(nom=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category has been created!', 'success')
        return redirect(url_for('categories'))
    categories = Categorie.query.all()
    return render_template('categories.html', title='Categories', form=form, categories=categories, nav="yes")

@app.route("/transaction/<int:transaction_id>/delete", methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.owner != current_user:
        abort(403)
    current_user.balance -= transaction.montant
    db.session.delete(transaction)
    db.session.commit()
    flash('Your transaction has been deleted!', 'success')
    return redirect(url_for('account'))

@app.route("/transaction/<int:transaction_id>/update", methods=['GET', 'POST'])
@login_required
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.owner != current_user:
        abort(403)
    
    form = TransactionForm()
    
    if form.validate_on_submit():
        transaction.title = form.title.data
        transaction.montant = form.montant.data
        transaction.date = form.date.data
        transaction.description = form.description.data
        transaction.cat_id = form.categorie.data
        db.session.commit()
        flash('Your transaction has been updated!', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.id.data = transaction.id
        form.title.data = transaction.title
        form.montant.data = transaction.montant
        form.date.data = transaction.date
        form.description.data = transaction.description
        form.categorie.data = transaction.cat_id
    
    return render_template('transaction.html', title='Update Transaction', form=form, nav="yes")



# @app.route("/login1",methods=['GET', 'POST'])
# def login2():
#     form ="hi"
#     return render_template('login.html', title='css bs',nav='no'form=form)