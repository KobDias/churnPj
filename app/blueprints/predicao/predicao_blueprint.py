from flask import Blueprint, current_app, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from db import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .processamento import gerar_df_pred, grupos_pred, processa_modelo, preprocess_input, gerar_grafico
import joblib
from models import Documentos
import pandas as pd
import matplotlib.pyplot as plt
import  base64

predicao_bp = Blueprint('predicao', __name__, template_folder='templates', url_prefix='/predicao')

ALLOWED_EXTENSIONS = set(['csv'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        

            upload_folder = os.path.join('app', 'static', 'uploads', 'user', 'original')
            print(upload_folder)
            os.makedirs(upload_folder, exist_ok=True)  # Garante que o diretório existe
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            new_filename = filename.split('.csv', 1)[0]
            
            uploadDoc = Documentos(
                user_id=current_user.id,
                caminho_origem=file_path,
                nome_documento=new_filename
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
    caminho = doc.caminho_origem
    nome = doc.nome_documento.split('.csv', 1)[0]
    if not doc:
        return 'Documentos não encontrado', 404
    predito = doc.caminho_pred
    if request.method == 'POST':
        print("submittaram")
        input_df = pd.read_csv(caminho)
        data = joblib.load('app/blueprints/predicao/modelo_churn_rf_bank_telco.pkl')
        model = data['model']
        columns = data['columns']

        X = preprocess_input(input_df, columns)

        preds = model.predict(X)
        probs = model.predict_proba(X)[:, 1]

        df_pred = gerar_df_pred(X, preds, probs)
        pred_path = os.path.join('app', 'static', 'uploads', 'sys', 'pred', f'{nome}_pred.csv')
        df_pred.to_csv(pred_path, index=False)
        doc.caminho_pred = pred_path        

        agrupado = grupos_pred(df_pred, nome)
        # ... seu código de agrupamento ...
        agrupado.columns = ['Sexo', 'Faixa Etária', 'Risco', 'Probabilidade Média', 'Total Clientes', 'Cancelamentos']
        agrupado['Probabilidade Média (%)'] = (agrupado['Probabilidade Média'] * 100).round(2)
        agrupado = agrupado.drop(columns=['Probabilidade Média'])

        # Salvar para download
        agrupado.to_csv(f'app/static/uploads/sys/pred/{nome}_grupos_risco.csv', index=False)

        db.session.commit()

        gerar_grafico(df_pred, nome, model, columns)
        return redirect(url_for('predicao.views', id=doc.id, df=df_pred)) #redireciona para a view do documento
    #get
    print(caminho)
    fig = url_for('static', filename=f'uploads/sys/graphs/{nome}.png')
    if fig:
        return render_template('view.html', fig=fig, doc=doc, predito=predito, nome=nome, caminho=caminho)
    return render_template('view.html', doc=doc, nome=nome, predito=predito, caminho=caminho)
    