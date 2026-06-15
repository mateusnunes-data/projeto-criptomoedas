import requests
import pandas as pd

# Configurações da API
url = "https://data-api.binance.vision/api/v3/klines"

params = {
    "symbol": "BTCUSDT",
    "interval": "1M",  
    "limit": 120        
}

# Requisição
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()

colunas = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "num_trades",
    "taker_buy_base", "taker_buy_quote", "ignore"
]

# Criar DataFrame
df = pd.DataFrame(data, columns=colunas)

# Converter datas
df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

# Converter colunas numéricas
for c in ["open", "high", "low", "close", "volume"]:
    df[c] = df[c].astype(float)

# Manter apenas as colunas principais
df = df[["open_time", "open", "high", "low", "close", "volume"]]

# Variação percentual mensal
df["variacao_percentual"] = df["close"].pct_change() * 100

# Médias móveis do fechamento
df["mm_3"] = df["close"].rolling(window=3).mean()
df["mm_6"] = df["close"].rolling(window=6).mean()
df["mm_12"] = df["close"].rolling(window=12).mean()

# Exibir dados
print("\nPrimeiras linhas:")
print(df.head())

print("\nÚltimas linhas:")
print(df.tail())

# Salvar para o trabalho
df.to_csv("btc_10_anos_mensal.csv", index=False)

print(f"\nArquivo salvo com {len(df)} meses.")