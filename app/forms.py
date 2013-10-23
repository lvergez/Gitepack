#coding: utf-8
from __future__ import unicode_literals
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField,DateField, SelectField
from wtforms.validators import Required, Length

class LoginForm(Form):
    openid = TextField('openid', validators= [Required()])
    remember_me = BooleanField ('remember_me', default=False)

class EditForm(Form):
    nickname = TextField('nickname', validators=[Required()])
    about_me = TextAreaField('about_me', validators=[Length(min = 0, max = 139)])

#TODO: validate
    #def validate(self):
    #    if not Form.validate(self):
    #        return False
    #
    #    user = User.query.filter_by(nickname = self.nickname.data).first()
    #    if user != None:
    #        self.nickname.errors.append('This nickname is already in use. Please choose another one.')
    #        return False
    #    return True

class GiteForm(Form):
    gite = TextField('gite', validators=[Required()])
    capacity = TextField('Capacite', validators=[Required()])

class BookingForm(Form):
    start = DateField ('Début',format='%d-%m-%Y')
    end = DateField ('Fin',format='%d-%m-%Y')
    customer = SelectField (u'Client',coerce=int)

class CustomerForm(Form):
    name = TextField('Nom')