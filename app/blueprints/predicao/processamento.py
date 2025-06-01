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

# Função de grafic
def gerar_importancia(model, X, nome):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    importances = model.feature_importances_
    feat_importances = pd.DataFrame({
        'feature': X.columns,
        'importance': (importances * 100).round(2)
    }).sort_values(by='importance', ascending=False)

    print("Top 10 features mais importantes (%):")
    print(feat_importances.head(10))

    plt.figure(figsize=(10,6))
    sns.barplot(data=feat_importances.head(10), x='importance', y='feature', palette='viridis')
    plt.title('Top 10 Features mais importantes (%)')
    plt.xlabel('Importância (%)')
    plt.tight_layout()
    fig_path = os.path.join('app', 'static', 'uploads', 'sys', 'graphs', f'{nome}_importante.png')
    plt.savefig(fig_path)
    plt.close()
    

# Função para pré-processar um DataFrame

def padronizar_coluna_alvo(df):
    for col in df.columns:
        if str(col).lower() in ['churn', 'cancelado', 'cancelamento', 'cancelou', 'saida', 'exited']:
            df.rename(columns={col: 'Churn'}, inplace=True)
            df['Churn'] = df['Churn'].apply(lambda x: 1 if str(x).lower() in ['yes','sim','true','1'] else 0)
            return df
    raise ValueError("Coluna alvo (churn) não encontrada.")

def preprocess(df, id_columns=[]):
    # Remover colunas de identificação
    df = df.drop(columns=id_columns, errors='ignore')

    # Padronizar nomes de colunas
    renomear = {
        'idade': 'Age',
        'idade_cliente': 'Age',
        'sexo': 'Gender',
        'genero': 'Gender',
        'salario': 'EstimatedSalary',
        'mensalidade': 'MonthlyCharges',
        'tempo': 'Tenure',
        'churn': 'Churn'
    }
    df.rename(columns={col: renomear.get(col.lower(), col) for col in df.columns}, inplace=True)

    # Converter valores categóricos
    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].apply(lambda x: 1 if x.lower() in ['homem', 'male'] else 0)
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].apply(lambda x: 1 if str(x).lower() in ['sim', 'yes'] else 0)

    # Converter colunas numéricas
    for col in df.columns:
        if col not in ['Gender', 'Churn'] and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remover linhas com muitos valores ausentes
    df = df.dropna(thresh=int(len(df.columns) * 0.7))

    # Adicionar colunas ausentes com valores padrão (se necessário)
    expected_columns = ['Age', 'Balance', 'Contract', 'CreditScore', 'Dependents', 'DeviceProtection',
                        'EstimatedSalary', 'Gender', 'Geography', 'HasCrCard', 'InternetService',
                        'IsActiveMember', 'MonthlyCharges', 'MultipleLines', 'NumOfProducts',
                        'OnlineBackup', 'OnlineSecurity', 'PaperlessBilling', 'Partner', 'PaymentMethod',
                        'PhoneService', 'SeniorCitizen', 'StreamingMovies', 'StreamingTV', 'TechSupport',
                        'Tenure', 'TotalCharges']
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0  # Adicionar colunas ausentes com valor padrão

    # Retornar DataFrame processado
    return df

def processa_modelo(input_df, modelo_path=None):
    if modelo_path is None:
        modelo_path = os.path.join(
            os.path.dirname(__file__),
            'static', 'models', 'modelo_churn_rf_bank_telco.pkl'
        )
    data = joblib.load(modelo_path)
    columns = data['columns']

    if any(str(col).lower() in ['churn', 'cancelado', 'cancelamento', 'cancelou', 'saida', 'exited'] for col in input_df.columns):
        input_df = padronizar_coluna_alvo(input_df)
    
    id_cols = ['CustomerId', 'RowNumber', 'Surname', 'customerID']
    df_proc = preprocess(input_df, id_columns=id_cols)

    if 'Churn' in df_proc.columns:
        df_proc = df_proc.drop(columns=['Churn'])
    
    df_proc = df_proc.reindex(columns=columns, fill_value=0)
    
    return df_proc

def grupos_pred(df_resultado, nome):
    df_resultado['Probabilidade (%)'] = (df_resultado['Probabilidade']*100).round(2)

    # Procurar colunas de gênero (todas as variações)
    possiveis_generos = ['gender', 'sexo', 'genero']
    col_genero = [col for col in df_resultado.columns if any(g in col.lower() for g in possiveis_generos)]

    # Gênero
    if col_genero:
        col = col_genero[0]
        # Se for booleano, 1=Homem, 0=Mulher (ajuste conforme seu padrão)
        if df_resultado[col].dropna().isin([0,1]).all():
            df_resultado['Sexo'] = df_resultado[col].apply(lambda x: 'Homem' if x == 1 else 'Mulher')
        else:
            df_resultado['Sexo'] = df_resultado[col].astype(str).str.capitalize()
    else:
        df_resultado['Sexo'] = 'Indefinido'

    # Idade
    possiveis_idades = ['age', 'idade', 'idade_cliente']
    col_idade = [col for col in df_resultado.columns if any(i in col.lower() for i in possiveis_idades)]
    if col_idade:
        df_resultado['Idade'] = df_resultado[col_idade[0]].astype(float).astype(int)
        df_resultado['Faixa Etaria'] = pd.cut(
            df_resultado['Idade'],
            bins=[17, 30, 45, 60, 120],
            labels=['18 a 30', '31 a 45', '46 a 60', '60+']
        )
    else:
        df_resultado['Faixa Etaria'] = 'Indefinida'

    # Agrupar por perfil
    agrupado = df_resultado.groupby(['Sexo', 'Faixa Etaria', 'Risco'], observed=True).agg({
        'Probabilidade': 'mean',
        'Churn': ['count', 'sum']
    }).reset_index()

    agrupado.columns = ['Sexo', 'Faixa Etaria', 'Risco', 'Probabilidade Media', 'Total Clientes', 'Cancelamentos']
    agrupado = agrupado[agrupado['Total Clientes'] > 0]
    agrupado = agrupado.dropna(subset=['Total Clientes'])
    agrupado['Probabilidade Media (%)'] = (agrupado['Probabilidade Media'] * 100).round(2)
    agrupado = agrupado.drop(columns=['Probabilidade Media'])

    agrupado.to_csv(f'app/static/uploads/sys/pred/{nome}_grupos_risco.csv', index=False, encoding='utf-8')
    return agrupado