from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from db import db
from models import User, Documentos, Graficos
from blueprints.auth.auth_blueprint import auth_blueprint
from blueprints.user.user_blueprint import user_blueprint
from blueprints.predicao.predicao_blueprint import predicao_blueprint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fideliza.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
lm = LoginManager(app)
lm.login_view = 'login'
lm.login_message = 'Por favor, faça login para acessar esta página.'
app.secret_key = 'fideliza-secret-key'
lm.init_app(app)
db.init_app(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(predicao_blueprint)

@lm.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        documento = db.session.query(Documentos).filter_by(user_id=current_user.id).all()
        return render_template('index.html', documentos=documento)
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)