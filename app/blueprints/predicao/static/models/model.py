# Importar bibliotecas essenciais
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib  # para salvar o modelo
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df_bank = pd.read_csv(os.path.join(BASE_DIR, 'data', 'churn.csv'))
df_telco = pd.read_csv(os.path.join(BASE_DIR, 'data', 'WA_Fn-UseC_-Telco-Customer-Churn.csv'))

def padronizar_coluna_alvo(df):
    for col in df.columns:
        if str(col).lower() in ['churn', 'cancelado', 'cancelamento', 'cancelou', 'saida', 'exited']:
            df.rename(columns={col: 'Churn'}, inplace=True)
            df['Churn'] = df['Churn'].apply(lambda x: 1 if str(x).lower() in ['yes','sim','true','1'] else 0)
            return df
    raise ValueError("Coluna alvo (churn) não encontrada.")

df_bank = padronizar_coluna_alvo(df_bank)
df_telco = padronizar_coluna_alvo(df_telco)

def preprocess(df, id_columns=[]):
    df = df.drop(columns=id_columns, errors='ignore')

    # Padroniza nomes comuns
    renomear = {
        'idade': 'Age',
        'idade_cliente': 'Age',
        'sexo': 'Gender',
        'genero': 'Gender',
        'salario': 'EstimatedSalary',
        'mensalidade': 'MonthlyCharges',
        'tempo': 'tenure'
    }
    df.rename(columns={col: renomear.get(col.lower(), col) for col in df.columns}, inplace=True)

    # Converte colunas categóricas (erradas como string) para float
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(thresh=int(len(df.columns) * 0.7))
    cat_cols = df.select_dtypes(include='object').columns
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    return df

df_bank_proc = preprocess(df_bank, id_columns=['CustomerId', 'RowNumber', 'Surname'])
df_telco_proc = preprocess(df_telco, id_columns=['customerID'])

target_bank = df_bank_proc['Churn']
target_telco = df_telco_proc['Churn']
df_bank_proc = df_bank_proc.drop(columns=['Churn'])
df_telco_proc = df_telco_proc.drop(columns=['Churn'])

def align_columns(df_list):
    all_cols = sorted(set().union(*(df.columns for df in df_list)))
    return [df.reindex(columns=all_cols, fill_value=0) for df in df_list], all_cols

[df_bank_aligned, df_telco_aligned], expected_columns = align_columns([df_bank_proc, df_telco_proc])

X = pd.concat([df_bank_aligned, df_telco_aligned], axis=0).reset_index(drop=True)
y = pd.concat([target_bank, target_telco], axis=0).reset_index(drop=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Salvar modelo e colunas
joblib.dump({'model': model, 'columns': X.columns.tolist()}, 'modelo_churn_rf_bank_telco.pkl')