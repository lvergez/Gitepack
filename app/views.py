#coding: utf-8
from __future__ import unicode_literals
from app import app
from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm, oid
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import LoginForm, EditForm, GiteForm, BookingForm, CustomerForm
from models import User,Gite, ROLE_USER, ROLE_ADMIN, Booking,Customer
from datetime import datetime


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/')
@app.route('/index')
def home():
    return render_template('home.html')

@app.route('/app')
@app.route('/app/index')
@login_required
def index():
    user = g.user
    gites = g.user.gites.all()

    return render_template ("index.html",
                            title = "Gitepack",
                            user = user,
                            gites = gites)


@app.route('/app/user/<nickname>')
@login_required
def user (nickname):
    user = User.query.filter_by(nickname = nickname).first()

    if user == None:
        flash('Utilisateur ' + nickname + ' introuvable')
        return redirect(url_for('index'))

    return render_template('user.html',
                           user = user,
                          )


@app.route('/app/login',methods= ['GET', 'POST'])
@oid.loginhandler
def login():
    form = LoginForm()

    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
        return redirect(url_for('index'))

    return render_template('login.html',
                           title = "Please Login",
                           form = form,
                           providers = app.config['OPENID_PROVIDERS'])

@app.route('/app/edit', methods=['GET','POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Changements sauve')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
                           form = form)

@app.route('/app/gite/add', methods=['GET','POST'])
@login_required
def giteadd():
    form = GiteForm ()
    if form.validate_on_submit():
        gite = Gite(nickname = form.gite.data,
                    owner = g.user,
                    capacity = form.capacity.data )
        db.session.add(gite)
        db.session.commit()
        flash("Gite rajoute")
        return redirect(url_for('index'))


    return render_template('editgite.html', form = form)

@app.route('/app/gite/delete/<id>')
@login_required
def gitedelete(id):
    gite = Gite.query.filter_by(id = id).first()
    bookings = Booking.query.filter_by(gite_id = id).all()
    if g.user.id == gite.user_id:
        db.session.delete(gite)
        for booking in bookings:
            db.session.delete(booking)
        db.session.commit()
        flash("Gite efface!")
        return redirect(url_for('index'))
    else:
        flash("pas ton gite")
        return redirect(url_for('index'))


@app.route('/app/gite/<id>')
@login_required
def giteview(id):

    gite = Gite.query.filter_by(id = id).first()
    if gite != None and gite.user_id == g.user.id:
        allbookings = []
        if gite.bookings.all() != None:
            allbookings = gite.bookings.all()
        customername = Customer.query.filter_by(id = Booking.customer_id).first()
        return render_template('giteview.html',
                               gite = gite,
                               user = g.user,
                               bookings = allbookings,
                               customer = customername.name)
    else:
        flash("Erreur: gite inconnu ou pas a vous")
        return redirect(url_for('giteview' ))

@app.route('/app/booking/add/<id>', methods=['GET','POST'])
@login_required
def addbooking(id):
    #TODO: check that gite id belongs to user

    form = BookingForm ()
    uid = g.user.id
    form.customer.choices = [(c.id, c.name)for c in Customer.query.filter_by(user = uid).all()]
    if form.validate_on_submit():
        booking = Booking(start = form.start.data,
                          end = form.end.data,
                          gite_id = id,
                          customer_id = form.customer.data)
        db.session.add(booking)
        db.session.commit()
        flash("booking  rajoute!")
        return redirect(url_for('index'))

    return render_template('editbooking.html', form = form)

@app.route('/app/customer/add', methods=['GET', 'POST'])
@login_required
def addcustomer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name = form.name.data,
                            user = g.user.id)
        db.session.add(customer)
        db.session.commit()
        flash('customer rajoute')
        return redirect(url_for('addcustomer'))
    return render_template('customer.html',form = form)

@app.route('/app/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'),500

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

