from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from db import db
from werkzeug.utils import secure_filename
import os
from .processamento import gerar_df_pred, gerar_importancia, grupos_pred, processa_modelo
import joblib
from models import Documentos
import pandas as pd

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
            filename = f"{current_user.id}_{filename}"

            upload_folder = os.path.join('app', 'static', 'uploads', 'user', 'original')
            os.makedirs(upload_folder, exist_ok=True)  # Garante que o diretório existe
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            new_filename = filename.split('.csv', 1)[0]

            existing_doc = Documentos.query.filter_by(nome_documento=new_filename, user_id=current_user.id).first()
            if existing_doc:
                flash('Arquivo já existe')
                return 'error'
            uploadDoc = Documentos(
                user_id=current_user.id,
                caminho_origem=file_path,
                nome_documento=new_filename
            )
            db.session.add(uploadDoc)
            db.session.commit()

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
    if not doc or doc.user_id != current_user.id:
        return 'Documentos não encontrado ou você não tem autorização para acessa-lo', 404
    predito = doc.caminho_pred
    risco = doc.caminho_grupos
    if request.method == 'POST':

        if predito or risco:
            if os.path.exists(predito):
                os.remove(predito)
            if os.path.exists(risco):
                os.remove(risco)
            nome_base = nome
            grafico_Importancia_path = os.path.join('app', 'static', 'uploads', 'sys', 'graphs', f'{nome_base}_importante.png')
            grafico_Risco_path = os.path.join('app', 'static', 'uploads', 'sys', 'graphs', f'{nome_base}_riscos.png')
            if os.path.exists(grafico_Importancia_path):
                os.remove(grafico_Importancia_path)
            if os.path.exists(grafico_Risco_path):
                os.remove(grafico_Risco_path)

        input_df = pd.read_csv(caminho)
        modelo_path = os.path.join(
        os.path.dirname(__file__),
        'static', 'models', 'modelo_churn_rf_bank_telco.pkl')
        data = joblib.load(modelo_path)
        model = data['model']
        columns = data['columns']

        X = processa_modelo(input_df)

        preds = model.predict(X)
        probs = model.predict_proba(X)[:, 1]

        df_pred = gerar_df_pred(X, preds, probs)
        
        pred_path = os.path.join('app', 'static', 'uploads', 'sys', 'pred', f'{nome}_pred.csv')
        df_pred.to_csv(pred_path, index=False, encoding='utf-8')
        doc.caminho_pred = pred_path

        agrupado = grupos_pred(df_pred, nome)
        
        agrupado.columns = ['Sexo', 'Faixa Etária', 'Risco', 'Probabilidade Média', 'Total Clientes', 'Cancelamentos']
        agrupado['Probabilidade Média (%)'] = (agrupado['Probabilidade Média'] * 100).round(2)
        agrupado = agrupado.drop(columns=['Probabilidade Média'])

        # Salvar para download
        agrupado.to_csv(f'app/static/uploads/sys/pred/{nome}_grupos_risco.csv', index=False, encoding='utf-8')

        riscos_path = os.path.join('app', 'static', 'uploads', 'sys', 'pred', f'{nome}_grupos_risco.csv')
        doc.caminho_grupos = riscos_path

        db.session.commit()

        gerar_importancia(model, X, nome)
        return redirect(url_for('predicao.views', id=doc.id)) #redireciona para a view do documento
    #get
    print(nome)
    fig_importance = url_for('static', filename=f'uploads/sys/graphs/{nome}_importante.png')
    if fig_importance:
        return render_template('view.html', doc=doc, predito=predito, nome=nome, caminho=caminho, fig_importance=fig_importance)
    return render_template('view.html', doc=doc, nome=nome, predito=predito, caminho=caminho)
    