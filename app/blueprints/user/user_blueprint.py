from flask import Blueprint, render_template, redirect, request, url_for
from models import User
from db import db
from flask_login import current_user, login_required
import hashlib

user_blueprint = Blueprint('user', __name__, template_folder='templates', url_prefix='/user')

def hash(txt):
    hashTxt = hashlib.sha256(txt.encode('utf-8'))
    return hashTxt.hexdigest()

@user_blueprint.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha_atual = request.form['senha_atual']
        print(current_user.senha)
        print(hash(senha_atual))
        if current_user.senha == hash(senha_atual):
            altUser = db.session.query(User).filter_by(id=current_user.id).first()
            altUser.nome = nome
            altUser.email = email
            
            nova_senha = request.form['nova_senha']
            if nova_senha:
                altUser.senha = hash(nova_senha)

            db.session.commit()
            return redirect(url_for('user.perfil'))
        else:
            return "Senha atual incorreta"
    # GET
    id = current_user.id
    user = db.session.query(User).filter_by(id=id).first()
    
    return render_template('perfil.html', user=user)