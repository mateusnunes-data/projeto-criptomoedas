import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# ==========================
# SELEÇÃO DOS ARQUIVOS
# ==========================

Tk().withdraw()

print("Selecione o arquivo do Bitcoin")
arquivo_btc = askopenfilename(
    title="Selecione o arquivo do Bitcoin",
    filetypes=[("Excel", "*.xlsx")]
)

print("Selecione o arquivo do Ethereum")
arquivo_eth = askopenfilename(
    title="Selecione o arquivo do Ethereum",
    filetypes=[("Excel", "*.xlsx")]
)

# ==========================
# LEITURA DOS ARQUIVOS
# ==========================

btc = pd.read_excel(arquivo_btc, engine="openpyxl")
eth = pd.read_excel(arquivo_eth, engine="openpyxl")

# ==========================
# PREPARAÇÃO DOS DADOS
# ==========================

btc["Data de abertura"] = pd.to_datetime(btc["Data de abertura"])
eth["open_time"] = pd.to_datetime(eth["open_time"])

btc["Valor de fechamento"] = pd.to_numeric(btc["Valor de fechamento"], errors="coerce")
eth["close"] = pd.to_numeric(eth["close"], errors="coerce")
btc["Quantidade negociada"] = pd.to_numeric(btc["Quantidade negociada"], errors="coerce")
eth["volume"] = pd.to_numeric(eth["volume"], errors="coerce")

btc = btc.dropna(subset=["Valor de fechamento"])
eth = eth.dropna(subset=["close"])

btc = btc.sort_values("Data de abertura")
eth = eth.sort_values("open_time")

btc_fechamento = btc["Valor de fechamento"]
eth_fechamento = eth["close"]
btc_volume = btc["Quantidade negociada"] * btc_fechamento  # convertido para USD
eth_volume = eth["volume"]  # já em USD

# ==========================
# RETORNO PERCENTUAL
# ==========================

btc_ret = btc_fechamento.pct_change().dropna()
eth_ret = eth_fechamento.pct_change().dropna()

# ==========================
# MÉTRICAS
# ==========================

btc_retorno_acumulado = (btc_fechamento.iloc[-1] / btc_fechamento.iloc[0] - 1) * 100
eth_retorno_acumulado = (eth_fechamento.iloc[-1] / eth_fechamento.iloc[0] - 1) * 100

btc_vol = btc_ret.std() * (252 ** 0.5)
eth_vol = eth_ret.std() * (252 ** 0.5)

# ==========================
# ESTATÍSTICAS
# ==========================

estatisticas = pd.DataFrame({
    "Criptomoeda": ["Bitcoin", "Ethereum"],
    "Média": [btc_fechamento.mean(), eth_fechamento.mean()],
    "Mediana": [btc_fechamento.median(), eth_fechamento.median()],
    "Desvio Padrão": [btc_fechamento.std(), eth_fechamento.std()],
    "Máximo": [btc_fechamento.max(), eth_fechamento.max()],
    "Mínimo": [btc_fechamento.min(), eth_fechamento.min()],
    "Retorno Acumulado (%)": [btc_retorno_acumulado, eth_retorno_acumulado],
    "Volatilidade Anual (%)": [btc_vol, eth_vol],
    "Volume Médio Mensal (USD)": [btc_volume.mean(), eth_volume.mean()],
    "Volume Total (USD)": [btc_volume.sum(), eth_volume.sum()]
})

estatisticas.to_excel("tabela_estatisticas.xlsx", index=False)

# ==========================
# TABELA ANUAL BTC
# ==========================

btc_anual = btc.copy()
btc_anual["Ano"] = btc_anual["Data de abertura"].dt.year
btc_anual = btc_anual.groupby("Ano")["Valor de fechamento"].mean().reset_index()
btc_anual.columns = ["Ano", "Fechamento Médio BTC"]
btc_anual.to_excel("tabela_btc_anual.xlsx", index=False)

# ==========================
# TABELA ANUAL ETH
# ==========================

eth_anual = eth.copy()
eth_anual["Ano"] = eth_anual["open_time"].dt.year
eth_anual = eth_anual.groupby("Ano")["close"].mean().reset_index()
eth_anual.columns = ["Ano", "Fechamento Médio ETH"]
eth_anual.to_excel("tabela_eth_anual.xlsx", index=False)

# ==========================
# RANKING DE DESEMPENHO
# ==========================

ranking = pd.DataFrame({
    "Criptomoeda": ["Bitcoin", "Ethereum"],
    "Retorno (%)": [btc_retorno_acumulado, eth_retorno_acumulado],
    "Volatilidade (%)": [btc_vol, eth_vol],
    "Volume Total (USD)": [btc_volume.sum(), eth_volume.sum()]
})

ranking = ranking.sort_values("Retorno (%)", ascending=False)
ranking["Posição"] = range(1, len(ranking) + 1)

ranking.to_excel("ranking_cripto.xlsx", index=False)

# ==========================
# FUNÇÃO AUXILIAR: exibir tabela como janela visual
# ==========================

def exibir_tabela(df, titulo, nota=None):
    df_fmt = df.copy()
    for col in df_fmt.select_dtypes(include="number").columns:
        if col.lower() == "ano":
            df_fmt[col] = df_fmt[col].apply(lambda x: str(int(x)))
        else:
            df_fmt[col] = df_fmt[col].apply(lambda x: f"{x:,.2f}")

    fig, ax = plt.subplots(figsize=(max(8, len(df_fmt.columns) * 1.8), max(2, len(df_fmt) * 0.6 + 1.2)))
    ax.axis("off")
    tabela = ax.table(
        cellText=df_fmt.values,
        colLabels=df_fmt.columns,
        cellLoc="center",
        loc="center"
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.auto_set_column_width(col=list(range(len(df_fmt.columns))))

    # Estilo do cabeçalho
    for (row, col), cell in tabela.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#ecf0f1")
        else:
            cell.set_facecolor("white")
        cell.set_edgecolor("#bdc3c7")

    fig.suptitle(titulo, fontsize=13, fontweight="bold", y=0.98)

    if nota:
        fig.text(0.5, 0.01, f"⚠️ {nota}", ha="center", fontsize=8, color="#7f8c8d", style="italic")

    plt.tight_layout()
    plt.show()

# ==========================
# EXIBIR TABELAS COMO JANELAS VISUAIS
# ==========================

nota_volume = (
    "Volume do BTC estimado (Quantidade negociada × Preço de fechamento). "
    "Volume do ETH já em USD (fonte original). Comparação aproximada."
)
exibir_tabela(estatisticas, "Estatísticas - Bitcoin e Ethereum", nota=nota_volume)
exibir_tabela(btc_anual, "Fechamento Médio Anual - Bitcoin")
exibir_tabela(eth_anual, "Fechamento Médio Anual - Ethereum")
exibir_tabela(ranking, "Ranking Final de Desempenho", nota=nota_volume)

# ==========================
# GRÁFICO BTC
# ==========================

plt.figure(figsize=(12, 6))
plt.plot(btc["Data de abertura"], btc["Valor de fechamento"])
plt.title("Bitcoin - Fechamento Mensal")
plt.xlabel("Ano")
plt.ylabel("Preço (USD)")
plt.grid(True)
plt.savefig("grafico_bitcoin.png", bbox_inches="tight")
plt.show()

# ==========================
# GRÁFICO ETH
# ==========================

plt.figure(figsize=(12, 6))
plt.plot(eth["open_time"], eth["close"])
plt.title("Ethereum - Fechamento Mensal")
plt.xlabel("Ano")
plt.ylabel("Preço (USD)")
plt.grid(True)
plt.savefig("grafico_ethereum.png", bbox_inches="tight")
plt.show()

# ==========================
# COMPARAÇÃO BTC vs ETH  ← LEGENDA CORRIGIDA
# ==========================

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel("Ano")
ax1.set_ylabel("Bitcoin (USD)", color="orange")
line1, = ax1.plot(btc["Data de abertura"], btc["Valor de fechamento"], label="Bitcoin", color="orange")
ax1.tick_params(axis="y", labelcolor="orange")

ax2 = ax1.twinx()
ax2.set_ylabel("Ethereum (USD)", color="blue")
line2, = ax2.plot(eth["open_time"], eth["close"], label="Ethereum", color="blue")
ax2.tick_params(axis="y", labelcolor="blue")

# Combina as duas legendas em uma só
lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper left")

fig.suptitle("Comparação BTC vs ETH")
plt.grid(True)
plt.savefig("comparacao_btc_eth.png", bbox_inches="tight")
plt.show()

# ==========================
# FINAL
# ==========================

print("\nArquivos gerados com sucesso:")
print("- tabela_estatisticas.xlsx")
print("- tabela_btc_anual.xlsx")
print("- tabela_eth_anual.xlsx")
print("- grafico_bitcoin.png")
print("- grafico_ethereum.png")
print("- comparacao_btc_eth.png")
print("- ranking_cripto.xlsx")