import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="OfficeIA Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_SITE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OfficeIA Pro - Assistente Executivo</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: white; max-width: 650px; width: 100%; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        h1 { color: #107c41; margin-top: 0; font-size: 24px; }
        p.sub { color: #605e5c; font-size: 14px; margin-bottom: 20px; }
        label { font-weight: 600; display: block; margin-top: 15px; color: #323130; font-size: 14px; }
        input[type="text"], input[type="file"], textarea { width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #c8c6c4; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .row { display: flex; gap: 12px; }
        .row div { flex: 1; }
        button { width: 100%; padding: 14px; margin-top: 22px; background: #107c41; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0b5a2f; }
        #resultadoBox { margin-top: 25px; display: none; border-top: 2px solid #edebe9; padding-top: 20px; }
        pre { background: #faf9f8; padding: 15px; border-radius: 6px; border: 1px solid #edebe9; white-space: pre-wrap; font-family: 'Consolas', monospace; font-size: 13px; }
        img { max-width: 100%; border-radius: 6px; margin-top: 15px; border: 1px solid #edebe9; }
        .assinatura { margin-top: 25px; padding-top: 10px; border-top: 1px solid #323130; width: 260px; font-size: 13px; }
        .btn-print { background: #0078d4; margin-top: 12px; }
        .btn-print:hover { background: #106ebe; }
    </style>
</head>
<body>
<div class="container">
    <h1>📊 OfficeIA Pro — Inteligência de Escritório</h1>
    <p class="sub">Envie sua planilha (Excel ou CSV), dê a ordem e gere o relatório financeiro assinado.</p>

    <label>1. Selecione a Planilha (.xlsx, .xls, .csv)</label>
    <input type="file" id="arquivo" accept=".xlsx,.xls,.csv">

    <label>2. O que você deseja analisar?</label>
    <textarea id="comando" rows="3" placeholder="Ex: Calcule o balanço financeiro, entradas, saídas e gere o gráfico..."></textarea>

    <div class="row">
        <div>
            <label>3. Nome do Responsável (Assinatura)</label>
            <input type="text" id="responsavel" placeholder="Ex: Maria Silva">
        </div>
        <div>
            <label>4. Cargo / Setor</label>
            <input type="text" id="cargo" placeholder="Ex: Diretora Financeira">
        </div>
    </div>

    <button onclick="processar()">✨ Gerar Relatório Oficial</button>

    <div id="resultadoBox">
        <h3>📄 Relatório Gerado</h3>
        <pre id="textoRelatorio"></pre>
        <img id="imgGrafico" style="display:none;">
        <div class="assinatura" id="blocoAssinatura"></div>
        <button class="btn-print" onclick="window.print()">🖨️ Salvar em PDF / Imprimir</button>
    </div>
</div>

<script>
    async function processar() {
        const fileInput = document.getElementById("arquivo");
        const comando = document.getElementById("comando").value || "Análise Financeira Completa";
        const respNome = document.getElementById("responsavel").value || "Responsável Técnico";
        const respCargo = document.getElementById("cargo").value || "Setor Administrativo";

        if (!fileInput.files.length) return alert("Selecione uma planilha primeiro!");

        const formData = new FormData();
        formData.append("arquivo", fileInput.files);
        formData.append("comando", comando);

        const btn = document.querySelector("button");
        btn.innerText = "⏳ Analisando dados...";
        btn.disabled = true;

        try {
            const req = await fetch("/api/analisar-planilha", { method: "POST", body: formData });
            const res = await req.json();

            document.getElementById("textoRelatorio").innerText = res.relatorio;
            const img = document.getElementById("imgGrafico");
            if (res.grafico_base64) {
                img.src = "data:image/png;base64," + res.grafico_base64;
                img.style.display = "block";
            } else {
                img.style.display = "none";
            }
            document.getElementById("blocoAssinatura").innerHTML = `<strong>${respNome}</strong><br>${respCargo}`;
            document.getElementById("resultadoBox").style.display = "block";
        } catch (e) {
            alert("Erro ao processar planilha. Verifique o formato do arquivo.");
        } finally {
            btn.innerText = "✨ Gerar Relatório Oficial";
            btn.disabled = false;
        }
    }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial():
    return HTML_SITE

def analisar_financas(df: pd.DataFrame, comando: str):
    col_texto = df.select_dtypes(include=["object"]).columns
    col_valor = df.select_dtypes(include=[np.number]).columns

    if len(col_texto) == 0 or len(col_valor) == 0:
        return df.describe().to_string(), None

    cat_col = col_texto
    val_col = col_valor

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
        f"RELATÓRIO EXECUTIVO DE ANÁLISE FINANCEIRA\\n"
        f"--------------------------------------------------\\n"
        f"• Total de Entradas Operacionais: R$ {entradas:,.2f}\\n"
        f"• Total de Saídas Operacionais: R$ {saidas:,.2f}\\n"
        f"• Balanço Líquido Apurado: R$ {balanco:,.2f}\\n"
        f"--------------------------------------------------\\n"
        f"Solicitação processada: {comando}\\n"
    )

    img_base64 = None
    if itens_validos:
        fig, ax = plt.subplots(figsize=(6, 3))
        nomes = [x for x in itens_validos]
        valores = [abs(x) for x in itens_validos]
        cores = ["#107c41" if x > 0 else "#d13438" for x in itens_validos]
        
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


3. Clique em **Commit changes** no GitHub.
4. O Render vai atualizar sozinho em 1 minuto. Depois disso, basta atualizar a aba **`https://onrender.com`** que o seu site visual completo vai abrir direto nela (e também no `manifest.xml` do Office se você apontar para `https://onrender.com`).

<FollowUp>
Atualizou o **`main.py`** no GitHub e recarregou **`https://onrender.com`** para ver a tela visual do seu site abrir?
</FollowUp>
