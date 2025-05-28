import joblib
import pandas as pd
import os

# Defs de dataset

def classificar_risco(prob):
    if prob >= 0.7:
        return 'Alto'
    elif prob >= 0.4:
        return 'Medio'
    else:
        return 'Baixo'
def gerar_df_pred(X, preds, probs):
    """
    X_input: DataFrame com as colunas usadas no treinamento (após preprocessamento e alinhamento)
    preds: array ou lista com as predições (0/1)
    probs: array ou lista com as probabilidades de churn (float)
    """
    df_pred = X.copy()
    df_pred['Churn'] = preds
    df_pred['Probabilidade'] = probs
    df_pred['Risco'] = df_pred['Probabilidade'].apply(classificar_risco)
    return df_pred

# Função de grafico
def gerar_grafico(df_pred, nome, model, columns):
    import matplotlib.pyplot as plt
    import seaborn as sns

    importance = model.feature_importances_
    feat_importances = pd.DataFrame({
        'feature': columns,
        'importance': (importance*100).round(2)
    })

    feat_importances = feat_importances[feat_importances['importance'] > 0]
    feat_importances = feat_importances.sort_values(by='importance', ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='importance', y='feature', data=feat_importances)
    plt.title('Importancia das Features')
    plt.xlabel('Importancia (%)')
    plt.ylabel('Features')
    plt.tight_layout()
    fig_path_Importance = os.path.join('app', 'static', 'uploads', 'sys', 'graphs', f'{nome}_importante.png')
    plt.savefig(fig_path_Importance)
    plt.close()

    if 'Risco' in df_pred.columns:
        plt.figure(figsize=(8, 5))
        sns.countplot(x='Risco', data=df_pred, palette='viridis')
        plt.title('Distribuição dos Grupos de Risco')
        plt.xlabel('Risco')
        plt.ylabel('Quantidade')
        plt.tight_layout()
        fig_path2 = os.path.join('app', 'static', 'uploads', 'sys', 'graphs', f'{nome}_riscos.png')
        plt.savefig(fig_path2)
        plt.close()
    

# Função para pré-processar um DataFrame

def preprocess_input(df, columns):
    numeric_cols = [col for col in columns if any(df.columns.str.fullmatch(col))]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    cat_cols = df.select_dtypes(include='object').columns
    df[cat_cols] = df[cat_cols].astype(str)
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    df = df.reindex(columns=columns, fill_value=0)
    return df

def processa_modelo(input_df):
    data = joblib.load('app/blueprints/predicao/modelo_churn_rf_bank_telco.pkl')
    model = data['model']
    columns = data['columns']
    X = preprocess_input(input_df, columns)
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]
    return preds, probs

def grupos_pred(df_resultado, nome):
    df_resultado['Risco'] = df_resultado['Probabilidade'].apply(classificar_risco)

    # Detectar colunas de sexo e idade (robusto)
    col_genero = [col for col in df_resultado.columns if 'gender' in col.lower()]
    col_idade = [col for col in df_resultado.columns if 'age' in col.lower()]

    if col_genero:
        df_resultado['Sexo'] = df_resultado[col_genero[0]].apply(lambda x: 'Homem' if x == 1 else 'Mulher')
    else:
        df_resultado['Sexo'] = 'Indefinido'

    if col_idade:
        df_resultado['Idade'] = df_resultado[col_idade[0]].astype(int)
        df_resultado['Faixa Etária'] = pd.cut(df_resultado['Idade'], bins=[17, 30, 45, 60, 120],
                                            labels=['18–30', '31–45', '46–60', '60+'])
    else:
        df_resultado['Faixa Etária'] = 'Indefinida'

    # Agrupar por perfil
    agrupado = df_resultado.groupby(['Sexo', 'Faixa Etária', 'Risco']).agg({
        'Probabilidade': 'mean',
        'Churn': ['count', 'sum']
    }).reset_index()

    agrupado.columns = ['Sexo', 'Faixa Etária', 'Risco', 'Probabilidade Média', 'Total Clientes', 'Cancelamentos']
    agrupado['Probabilidade Média (%)'] = (agrupado['Probabilidade Média'] * 100).round(2)
    agrupado = agrupado.drop(columns=['Probabilidade Média'])

    # Salvar para download
    agrupado.to_csv(f'app/static/uploads/sys/pred/{nome}_grupos_risco.csv', index=False, encoding='utf-8')
    return agrupado