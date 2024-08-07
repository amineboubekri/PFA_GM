import os
import secrets
from datetime import datetime
from PIL import Image 
from app.models import User, Post, Transaction, Categorie, Comment, Like
from flask import render_template, url_for, flash, redirect, request, abort, send_file
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, TransactionForm, CategoryForm, UpdateBalanceForm, CommentForm, UpdateCommentForm
from app import app, db, bcrypt
from sqlalchemy import extract
from flask_login import login_user, current_user, logout_user, login_required
from io import BytesIO
import csv



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
        flash(f'Votre compte a été créé ! Vous pouvez vous connecter maintenant', 'success')
        return redirect(url_for('login'))
    return render_template('register2.html', title='Register', form=form, logo='true')


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
            flash('Connexion échouée. Veuillez vérifier votre email et mot de passe', 'danger')
    return render_template('login2.html', title='Login',nav='no', form=form,logo='true')

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
        flash('Votre compte est a jour', 'success')
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

    # Calculate spending per category
    category_spending = db.session.query(
        Categorie.nom, db.func.sum(Transaction.montant)
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.date) == selected_year,
        extract('month', Transaction.date) == selected_month
    ).group_by(Categorie.nom).all()

    # Variables for chart
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
        flash('Votre compte est a jour!', 'success')
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
        flash('Votre publication est cree! ', 'success')
        return redirect(url_for('home'))    
    return render_template('create_post.html',nav="yes", title='New Post', form=form, legend="New Post")


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        flash('Post inexistant.', 'danger')
        return redirect(url_for('home'))
        
    form = CommentForm()
    reply_form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Votre commentaire est publie', 'success')
        return redirect(url_for('post', post_id=post.id))

    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).all()
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments, reply_form=reply_form, nav="yes")


@app.route("/comment/<int:comment_id>/reply", methods=['POST'])
@login_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = comment.post
    form = CommentForm()

    if form.validate_on_submit():
        reply = Comment(content=form.content.data, author=current_user, post=post, parent=comment)
        db.session.add(reply)
        db.session.commit()
        flash('Votre reponse est publiee', 'success')
        return redirect(url_for('post', post_id=post.id))

    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).all()
    reply_form = form  # Use the same form for replies
    return render_template('post.html', title=post.title, post=post, form=CommentForm(), comments=comments, reply_form=reply_form, nav="yes")


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
        flash('Votre post est a jour!', 'success')
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
    flash('Votre post est supprime!', 'success')
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
    form.categorie.choices = [(c.id_cat, c.nom) for c in Categorie.query.all()]
    if form.validate_on_submit():
        if float(form.montant.data) > current_user.balance:
            flash('Insuffisant balance pour cette transaction.', 'danger')
        else:
            transaction = Transaction(
                title=form.title.data,
                montant=form.montant.data,
                date=form.date.data,
                description=form.description.data,
                user_id=current_user.id,
                cat_id=form.categorie.data
            )
            db.session.add(transaction)
            current_user.balance -= float(form.montant.data)
            current_user.total_transactions += float(form.montant.data)
            db.session.commit()
            flash('Transaction avec succes', 'success')
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
        flash('Nouvelle categorie!', 'success')
        return redirect(url_for('categories'))
    categories = Categorie.query.all()
    return render_template('categories.html', title='Categories', form=form, categories=categories, nav="yes")

@app.route("/transaction/<int:transaction_id>/delete", methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.owner != current_user:
        abort(403)
    current_user.balance += transaction.montant
    current_user.total_transactions -= transaction.montant
    db.session.delete(transaction)
    db.session.commit()
    flash('Votre transaction est supprimee', 'success')
    return redirect(url_for('account'))

@app.route("/transaction/<int:transaction_id>/update", methods=['GET', 'POST'])
@login_required
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.owner != current_user:
        abort(403)
    
    form = TransactionForm()
    
    if form.validate_on_submit():
        old_amount = transaction.montant
        new_amount = form.montant.data
        amount_diff = new_amount - old_amount
        
        # Update the transaction
        transaction.title = form.title.data
        transaction.montant = new_amount
        transaction.date = form.date.data
        transaction.description = form.description.data
        transaction.cat_id = form.categorie.data

        current_user.balance -= amount_diff
        current_user.total_transactions += amount_diff 

        db.session.commit()
        flash('Votre transaction est a jour', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.id.data = transaction.id
        form.title.data = transaction.title
        form.montant.data = transaction.montant
        form.date.data = transaction.date
        form.description.data = transaction.description
        form.categorie.data = transaction.cat_id
    
    return render_template('transaction.html', title='Update Transaction', form=form, nav="yes")


@app.route("/update_balance", methods=['GET', 'POST'])
@login_required
def update_balance():
    form = UpdateBalanceForm()
    if form.validate_on_submit():
        amount = float(form.amount.data)
        if form.operation.data == 'add':
            current_user.balance += amount
            flash('Votre balance est a jour', 'success')
        elif form.operation.data == 'reduce':
            if float(form.amount.data) > current_user.balance:
                flash('Montant superieur a votre balance.', 'danger')
            else:
                current_user.balance -= amount
                flash('Votre balance est mis a jour', 'success')
        db.session.commit()
        return redirect(url_for('account'))
    return render_template('update_balance.html', title='Update Balance', form=form, nav="yes")


@app.route("/comment/<int:comment_id>/update", methods=['POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Votre commentaire est mis a jour.', 'success')
    return redirect(url_for('post', post_id=comment.post_id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    if comment.author != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Votre commentaire est supprime', 'success')
    return redirect(url_for('post', post_id=post_id))


@app.route("/like_post/<int:post_id>", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.has_liked_post(post):
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
    return redirect(url_for('post', post_id=post.id))

@app.route("/unlike_post/<int:post_id>", methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return redirect(url_for('post', post_id=post.id))

@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Categorie.query.get_or_404(category_id)
    
    transactions = Transaction.query.filter_by(cat_id=category.id_cat).first()
    if transactions:
        flash('On ne peut pas supprimer cette categorie car elle contient des transactions!.', 'danger')
        return redirect(url_for('categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Categorie Supprimee', 'success')
    return redirect(url_for('categories'))


#@app.route("/export_statistics")
#@login_required
#def export_statistics():
#    si = BytesIO()
#    writer = csv.writer(si)
#    
#    writer.writerow(["Title", "Amount", "Date", "Description", "Category"])
#
 #   for transaction in current_user.transactions:
  #      writer.writerow([
   #         transaction.title,
    #        transaction.montant,
     #       transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
      #      transaction.description,
       #     transaction.categorie.nom
        #])
    
    # Move the cursor of the StringIO object to the beginning
    #si.seek(0)
    
    #return send_file(
     #   si,
      #  mimetype='text/csv',
       # as_attachment=True,
        #download_name='statistics.csv'
    #)

    # Move to the beginning of the BytesIO object
    #output.seek(0)

    # Send the CSV file
    #return send_file(output, mimetype='text/csv', as_attachment=True, download_name='statistics.csv')
# @app.route("/login1",methods=['GET', 'POST'])
# def login2():
#     form ="hi"
#     return render_template('login.html', title='css bs',nav='no'form=form)