import joblib
import pandas as pd
import os

def processo(csv_path, y_pred, nome):
    df = pd.read_csv(csv_path)
    df['SalePrice'] = y_pred

    output_dir = os.path.join('app', 'static', 'uploads', 'preditos')
    os.makedirs(output_dir, exist_ok=True)

    # Usa o nome base do arquivo original para criar o novo nome
    output_name = f"{nome}_predito.csv"
    caminhoPredito = os.path.join(output_dir, output_name)
    df.to_csv(caminhoPredito, index=False)
    return caminhoPredito


def predict(csv_path):
    modelo = joblib.load('app/blueprints/pred/model/knn_model.pkl')
    scaler = joblib.load('app/blueprints/pred/model/scaler.pkl')
    df = pd.read_csv(csv_path)
    
    # Seleciona as colunas usadas no treinamento
    features = ["OverallQual", "GrLivArea", "GarageCars", "SaleCondition"]
    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no CSV: {', '.join(missing)}")
    
    X = df[features].copy()
    sale_condition_map = {
        'Normal': 0,
        'Abnorml': 1,
        'AdjLand': 2,
        'Alloca': 3,
        'Family': 4,
        'Partial': 5
    }
    X["SaleCondition"] = X["SaleCondition"].map(sale_condition_map)
    X["SaleCondition"] = X["SaleCondition"].fillna(-1)  # ou .dropna() se preferir remover
    xEscalado = scaler.transform(X)

    y_pred = modelo.predict(xEscalado)
    return y_pred

