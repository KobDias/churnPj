# Importar bibliotecas essenciais
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib  # para salvar o modelo

df_bank = pd.read_csv('app/blueprints/predicao/static/models/data/churn.csv')
df_telco = pd.read_csv('app/blueprints/predicao/static/models/data/WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Banco: 'Exited' → 'Churn'
df_bank.rename(columns={'Exited': 'Churn'}, inplace=True)
df_bank['Churn'] = df_bank['Churn'].astype(int)
df_telco['Churn'] = df_telco['Churn'].apply(lambda x: 1 if str(x).lower() in ['yes', 'sim', 'true', '1'] else 0)

# Função para pré-processar um DataFrame
def preprocess(df, id_columns=[]):
    df = df.drop(columns=id_columns, errors='ignore')
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(thresh=int(len(df.columns) * 0.7))
    cat_cols = df.select_dtypes(include='object').columns
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    return df

# Aplica o pré-processamento aos dois datasets
df_bank_processed = preprocess(df_bank, id_columns=['CustomerId', 'Surname'])
df_telco_processed = preprocess(df_telco, id_columns=['customerID'])

# Função para alinhar colunas
def align_columns(df_list):
    all_cols = sorted(set().union(*(df.columns for df in df_list)))
    df_aligned = [df.reindex(columns=all_cols, fill_value=0) for df in df_list]
    return df_aligned

# Alinhar os dois datasets
df_bank_aligned, df_telco_aligned = align_columns([df_bank_processed, df_telco_processed])
df_final = pd.concat([df_bank_aligned, df_telco_aligned], axis=0).reset_index(drop=True)

# Separar features e alvo
X = df_final.drop('Churn', axis=1)
y = df_final['Churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Acurácia: {acc:.2%}")
print("Relatório de classificação:")
print(classification_report(y_test, y_pred))

# Salvar modelo e colunas
joblib.dump({'model': model, 'columns': X.columns.tolist()}, 'modelo_churn_rf_bank_telco.pkl')