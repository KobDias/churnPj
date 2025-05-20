from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from db import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
# from .processamento import predict, processo
from models import Documentos
import pandas as pd
import matplotlib.pyplot as plt
import  base64

predicao_bp = Blueprint('pred', __name__, template_folder='templates', url_prefix='/pred')

ALLOWED_EXTENSIONS = set(['csv'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_grafico(df, nome):

    data = pd.read_csv(df)
    # Exemplo de gráfico: histograma da coluna 'SalePrice'
    plt.figure(figsize=(10, 6))
    data['SalePrice'].hist(bins=30)
    plt.title('Distribuição do SalePrice')
    plt.xlabel('SalePrice')
    plt.ylabel('Frequência')

    # Salva o gráfico em um buffer
    plt.savefig(f'app/static/uploads/graficos/{nome}.png', format='png')



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
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f'{filename.rsplit(".", 1)[0]}_{timestamp}.csv'

            file_path = os.path.join('app/static/uploads/original', new_filename)
            file.save(file_path)
            
            uploadDoc = Documentos(
                user_id=current_user.id,
                caminhoOriginal=file_path,
                nome_doc=new_filename
            )
            db.session.add(uploadDoc)
            db.session.commit()
            print(uploadDoc.doc_id)

            return redirect(url_for('pred.views', id=uploadDoc.doc_id)) 
        # if not ALLOWED_EXTENSIONS, return 'error'
        return 'error'
    #GET
    return render_template('upload.html')

@predicao_bp.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
def views(id):
    pass
    # doc = db.session.query(Documentos).filter_by(doc_id=id).first()
    # nome = doc.nome_doc.split('_202', 1)[0]
    # if not doc:
    #     return 'Documentos não encontrado', 404
    # if request.method == 'POST':
    #     caminho = doc.caminhoOriginal
    #     predicao = predict(caminho)

    #     predito = processo(caminho, predicao, nome)

    #     doc.caminhoPredito = predito
    #     db.session.commit()
    #     # add DATA DE PREDICAO se possivel pra ver a att
    #     return redirect(url_for('pred.views', id=doc.doc_id)) #redireciona para a view do documento
    # #get
    # gerar_grafico(doc.caminhoOriginal, nome)
    # fig = url_for('static', filename=f'uploads/graficos/{nome}.png')
    # predito = doc.caminhoPredito

    # return render_template('view.html', doc=doc, nome=nome, predito=predito, fig=fig)
    