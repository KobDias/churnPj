modelo = joblib.load('app\blueprints\predicao\static\model.pkl')
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
y_pred