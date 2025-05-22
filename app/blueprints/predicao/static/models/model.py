import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report, roc_auc_score
import joblib  # para salvar o modelo
import matplotlib.pyplot as plt

df_bank = pd.read_csv('app/blueprints/predicao/static/models/data/churn.csv')
df_telco = pd.read_csv('app/blueprints/predicao/static/models/data/WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Banco: 'Exited' → 'Churn'
df_bank.rename(columns={'Exited': 'Churn'}, inplace=True)
df_bank['Churn'] = df_bank['Churn'].astype(int)

# Telecom: 'Churn' Yes/No → 1/0
df_telco['Churn'] = df_telco['Churn'].apply(lambda x: 1 if str(x).lower() in ['yes', 'sim', 'true', '1'] else 0)

# Função para pré-processar um DataFrame
def preprocess(df):
    # Define um limite para colunas com muitos valores ausentes (mais de 50% de nulos serão removidas)
    limiar_nulos = 0.5
    df = df.loc[:, df.isnull().mean() < limiar_nulos]

    # Preenche valores ausentes nas colunas numéricas com a mediana de cada coluna
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        df[col].fillna(df[col].median(), inplace=True)

    # Preenche valores ausentes nas colunas categóricas com a moda (valor mais frequente)
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

   #pd.get_dummies()	Converte colunas de texto em colunas numéricas binárias
   #drop_first=True	Remove a primeira dummy de cada categoria para evitar redundância
    df = pd.get_dummies(df, drop_first=True)

    return df

# Aplica o pré-processamento aos dois datasets
df_bank_processed = preprocess(df_bank)
df_telco_processed = preprocess(df_telco)

# Função para alinhar colunas
def align_columns(df_list):
    all_cols = set()
    for df in df_list:
        all_cols.update(df.columns)
    all_cols = sorted(all_cols)

    df_aligned = []
    for df in df_list:
        missing = list(set(all_cols) - set(df.columns))
        df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing)], axis=1)
        df = df[all_cols]
        df_aligned.append(df)
    return df_aligned

# Alinhar os dois datasets
df_bank_aligned, df_telco_aligned = align_columns([df_bank_processed, df_telco_processed])

# Concatenar os dois datasets
df_final = pd.concat([df_bank_aligned, df_telco_aligned], axis=0).reset_index(drop=True)

# Separar features e alvo
X = df_final.drop('Churn', axis=1)
y = df_final['Churn']

# Dividir em conjunto de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Criar e treinar o modelo Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Fazer previsões no conjunto de teste
y_pred = model.predict(X_test)

joblib.dump(model, 'model.pkl')  # Salvar o modelo