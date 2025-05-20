from flask import Blueprint, render_template, request, redirect, url_for, Flask
from models import *
from db import db
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager
import hashlib

auth_bp = Blueprint('auth', __name__, template_folder='templates', url_prefix='/auth')

def hash(txt):
    hashTxt = hashlib.sha256(txt.encode('utf-8'))
    return hashTxt.hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = db.session.query(User).filter_by(email=email, senha=hash(senha)).first() # compara as infos com o banco
        if user:
            login_user(user) # logar
            return redirect(url_for('home'))
        else:
            return "Email ou senha invalidos" # tratar com flash
    #GET
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        user = User(nome=nome, email=email, senha=hash(senha))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('cadastro.html')