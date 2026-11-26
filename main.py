import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OfficeIA Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def analisar_financas(df: pd.DataFrame, comando: str):
    col_texto = df.select_dtypes(include=["object"]).columns
    col_valor = df.select_dtypes(include=[np.number]).columns

    if len(col_texto) == 0 or len(col_valor) == 0:
        return df.describe().to_string(), None

    cat_col = col_texto[0]
    val_col = col_valor[0]

    entradas_kw = ["receita", "venda", "faturamento", "ganho", "a receber", "entrada"]
    saidas_kw = ["despesa", "custo", "folha", "imposto", "a pagar", "gasto", "saída"]
    ignorar_kw = ["lucro", "saldo", "total", "subtotal", "resultado", "balanço"]

    entradas, saidas = 0.0, 0.0
    itens_validos = []

    for _, row in df.iterrows():
        nome = str(row[cat_col]).strip()
        nome_low = nome.lower()
        try:
            val = float(row[val_col])
        except ValueError:
            continue

        if any(k in nome_low for k in ignorar_kw):
            continue
        elif any(k in nome_low for k in entradas_kw):
            entradas += val
            itens_validos.append((nome, val))
        elif any(k in nome_low for k in saidas_kw):
            saidas += val
            itens_validos.append((nome, -val))

    balanco = entradas - saidas

    relatorio = (
        f"RELATÓRIO EXECUTIVO DE ANÁLISE FINANCEIRA\n"
        f"--------------------------------------------------\n"
        f"• Total de Entradas Operacionais: R$ {entradas:,.2f}\n"
        f"• Total de Saídas Operacionais: R$ {saidas:,.2f}\n"
        f"• Balanço Líquido Apurado: R$ {balanco:,.2f}\n"
        f"--------------------------------------------------\n"
        f"Solicitação processada: {comando}\n"
    )

    img_base64 = None
    if itens_validos:
        fig, ax = plt.subplots(figsize=(6, 3))
        nomes = [x[0] for x in itens_validos]
        valores = [abs(x[1]) for x in itens_validos]
        cores = ["#107c41" if x[1] > 0 else "#d13438" for x in itens_validos]
        
        ax.barh(nomes, valores, color=cores)
        ax.set_title("Composição Financeira (Verde: Entrada | Vermelho: Saída)")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

    return relatorio, img_base64

@app.post("/api/analisar-planilha")
async def endpoint_planilha(comando: str = Form(...), arquivo: UploadFile = File(...)):
    conteudo = await arquivo.read()
    df = pd.read_csv(io.BytesIO(conteudo)) if arquivo.filename.endswith(".csv") else pd.read_excel(io.BytesIO(conteudo))
    texto, grafico = analisar_financas(df, comando)
    return {"relatorio": texto, "grafico_base64": grafico}

@app.post("/api/analisar-dados-diretos")
async def endpoint_direto(payload: dict):
    dados = payload.get("dados", [])
    comando = payload.get("comando", "Análise Geral")
    df = pd.DataFrame(dados)
    texto, grafico = analisar_financas(df, comando)
    return {"relatorio": texto, "grafico_base64": grafico}
