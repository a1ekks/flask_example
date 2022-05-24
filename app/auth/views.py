from datetime import datetime
import hashlib
import random
from flask import current_app, url_for, render_template, request, abort, \
    url_for, make_response, session, g, redirect
from flask_login import login_user, logout_user, current_user
from . import auth
from ..models import *
from ..tools.database import db
from .forms import LoginForm


def before_request():
    """
    Проверка(создание) пользовательской сесссии 
    :return: 
    """

    if request.endpoint != 'static':
        check_sess = db.session.query(UserSessions).filter(UserSessions.session == session.get('sess')).first()
        if not check_sess:
            session_hash = hashlib.md5(
                (request.remote_addr + ''.join([chr(int(random.random() * 26) + 97) for i in range(1, 7)])).encode('utf8')
                ).hexdigest()
            sess = UserSessions(session=session_hash, date=datetime.now())
            db.session.add(sess)
            db.session.commit()
            session['sess'] = session_hash


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Страница с формой для авторизации
    :return: 
    """

    next = request.args.get('next', '')
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = Users.query.filter(Users.login == form.auth_login.data).first()
        login_user(user, False)
        return redirect(request.args.get('next', '/'))
    return render_template('auth/login.html', page=None, form=form, next=next)


@auth.route('/logout')
def logout():
    """
    Выход из системы
    :return: 
    """

    logout_user()
    return redirect('/')