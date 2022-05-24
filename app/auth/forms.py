import re
from wtforms import TextAreaField, StringField, FileField, DateTimeField, \
    IntegerField, ValidationError, PasswordField
from wtforms.fields import BooleanField
from flask_wtf import RecaptchaField, Form
from flask import session
from wtforms.validators import DataRequired, Email, Optional
from ..tools.database import db
from ..models import *
from flask_login import current_user
from sqlalchemy import and_


class LoginForm(Form):
    """
    Форма для входа
    """

    req_msg = 'Поле обязательно к заполнению'
    email_msg = 'Введите email адрес'

    auth_login = StringField(
        'email',
        validators=[DataRequired(message=req_msg), Email(message=email_msg)]
    )
    auth_pw = PasswordField('password', validators=[DataRequired(message=req_msg)])

    def validate_auth_pw(self, field):
        cur_user = Users.query.filter(Users.login == self.auth_login.data).first()
        if cur_user and cur_user.verify_password(field.data) and cur_user.is_active == 1:
            return
        raise ValidationError('Логин или пароль введены неверно')

class RegistrationForm(Form):
    """
    Форма для регистрации пользователя
    """

    req_msg = 'Заполните поле'
    email_msg = 'Введите корректный email адрес'

    reg_name = StringField('name', validators=[DataRequired(message=req_msg)])
    reg_email = StringField('email', validators=[DataRequired(message=req_msg), Email(message=email_msg)])
    reg_phone = StringField(
        'phone', validators=[DataRequired(message=req_msg)],
        render_kw={'placeholder': '+7 (___) ___-__-__'}
    )
    reg_pw = PasswordField('password', validators=[DataRequired(message=req_msg)])
    reg_pw_same = PasswordField('password', validators=[DataRequired(message=req_msg)])
    reg_captcha = StringField('captcha', validators=[DataRequired(message=req_msg)])
    reg_license = BooleanField(default=True)

    def validate_reg_email(self, field):
        exists = db.session.query(Users).filter(Users.login == field.data).first()
        if not exists:
            return
        raise ValidationError('Пользователь с таким адресом эл. почты уже существует.')

    def validate_reg_captcha(self, field):
        captcha_value = db.session.query(UserSessions). \
            filter(UserSessions.session == session.get('sess')).first()
        if captcha_value and field.data == captcha_value.captcha:
            return
        raise ValidationError('Символы с изображения введены неверно')

    def validate_reg_license(self, field):
        if field.data:
            return
        raise ValidationError('Необходимо принять пользовательское соглашение')

    def validate_reg_pw_same(self, field):
        if field.data == self.reg_pw.data:
            return
        raise ValidationError('Введенные пароли не совпадают')

    def validate_reg_phone(self, field):
        phone = ''.join(i for i in field.data if i.isdigit())
        is_valid = re.match(r'\d{11,}', phone)
        if is_valid:
            return
        raise ValidationError('Введите корректный номер телефона')
