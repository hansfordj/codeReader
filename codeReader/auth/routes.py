from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from codeReader import db, app
from codeReader.auth import bp
from codeReader.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationForm
from codeReader.models import User, UserRoles
from codeReader.auth.email import send_password_reset_email
from codeReader import role_required

''' INTERNAL SUBDOMAIN BLUEPRINT '''


# Registration page
@bp.route('/register_manager', methods=['GET', 'POST'])
@role_required(roles=['ADMIN'])
def register_manager():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        roles = UserRoles(user_id=user.id, role_id=2)
        db.session.add(roles)
        db.session.commit()
        flash('User has been registered and can log in', 'success')
        return redirect(url_for('index'))

    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/register_tech', methods=['GET', 'POST'])
@role_required(roles=['MANAGER'])
def register_tech():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        roles = UserRoles(user_id=user.id, role_id=3)
        db.session.add(roles)
        db.session.commit()
        flash('User has been registered and can log in', 'success')
        return redirect(url_for('index'))

    return render_template('auth/register.html', title='Register', form=form)

# Login page
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        user.logged_in=True
        db.session.commit()
        flash('You are now logged in', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


# Logout
@bp.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
