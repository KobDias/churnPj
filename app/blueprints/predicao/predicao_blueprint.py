from flask import Blueprint, current_app, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from db import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .processamento import predict, processo
from models import Documentos
import pandas as pd
import matplotlib.pyplot as plt
import  base64

predicao_bp = Blueprint('predicao', __name__, template_folder='templates', url_prefix='/predicao')

ALLOWED_EXTENSIONS = set(['csv'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_grafico(df, nome):

    data = pd.read_csv(df)

    if 'SalePrice' not in data.columns:
        print(f"Coluna 'SalePrice' não encontrada em {df}. Gráfico não será gerado.")
        return

    # Exemplo de gráfico: histograma da coluna 'SalePrice'
    plt.figure(figsize=(10, 6))
    data['SalePrice'].hist(bins=30)
    plt.title('Distribuição do SalePrice')
    plt.xlabel('SalePrice')
    plt.ylabel('Frequência')

    # Salva o gráfico em um buffer
    graph_dir = os.path.join('app', 'static', 'uploads', 'sys', 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    plt.savefig(os.path.join(graph_dir, f'{nome}.png'), format='png')



@predicao_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return 'error'
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "weee"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        

            upload_folder = os.path.abspath(
            os.path.join(current_app.root_path, 'static', 'uploads', 'user', 'original'))
            os.makedirs(upload_folder, exist_ok=True)  # Garante que o diretório existe
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            uploadDoc = Documentos(
                user_id=current_user.id,
                caminho_origem=file_path,
                nome_documento=filename
            )
            db.session.add(uploadDoc)
            db.session.commit()
            print(uploadDoc.id)

            return redirect(url_for('predicao.views', id=uploadDoc.id)) 
        # if not ALLOWED_EXTENSIONS, return 'error'
        return 'error'
    #GET
    return render_template('upload.html')

@predicao_bp.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
def views(id):
    doc = db.session.query(Documentos).filter_by(id=id).first()
    caminho = url_for('static', filename=f'uploads/user/original/{doc.nome_documento}')
    nome = doc.nome_documento.split('_202', 1)[0]
    if not doc:
        return 'Documentos não encontrado', 404
    predito = doc.caminho_pred
    if request.method == 'POST':
        predicao = predict(caminho)

        predito = processo(caminho, predicao, nome)
        db.session.commit()
        # add DATA DE PREDICAO se possivel pra ver a att
        return redirect(url_for('predicao.views', id=doc.id)) #redireciona para a view do documento
    #get
    print(caminho)
    gerar_grafico(doc.caminho_origem, nome)
    fig = url_for('static', filename=f'uploads/sys/graphs/{nome}.png')
    if fig:
        return render_template('view.html', fig=fig, doc=doc, predito=predito, nome=nome, caminho=caminho)
    return render_template('view.html', doc=doc, nome=nome, predito=predito, caminho=caminho)
    