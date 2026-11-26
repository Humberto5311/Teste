import io
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches
from pypdf import PdfReader
from sklearn.linear_model import LinearRegression

# 1. Configuração da Página (UI/UX)
st.set_page_config(page_title="Assistente de Escritório IA", page_icon="📂", layout="centered")

st.title("📂 Assistente Inteligente de Escritório")
st.write("Envie planilhas ou documentos, dê a ordem e baixe seu relatório assinado.")
st.divider()

# 2. Função que lê QUALQUER arquivo (1990 até 2026)
def ler_qualquer_arquivo(arquivo):
    nome = arquivo.name.lower()

    if nome.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".ods")):
        return pd.read_excel(arquivo), "tabela"
    
    elif nome.endswith(".csv"):
        try:
            return pd.read_csv(arquivo), "tabela"
        except Exception:
            arquivo.seek(0)
            return pd.read_csv(arquivo, sep=";"), "tabela"

    elif nome.endswith(".tsv"):
        return pd.read_csv(arquivo, sep="\t"), "tabela"

    elif nome.endswith(".docx"):
        doc = Document(arquivo)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return texto, "texto"

    elif nome.endswith(".pdf"):
        leitor = PdfReader(arquivo)
        texto = "\n".join([pagina.extract_text() or "" for pagina in leitor.pages])
        return texto, "texto"

    elif nome.endswith(".txt"):
        return arquivo.read().decode("utf-8", errors="ignore"), "texto"

    else:
        return "Formato não suportado para leitura automática.", "erro"

# 3. Cérebro Próprio de IA e Estatística em Python
def cerebro_ia_python(dados, tipo, comando):
    comando_lower = comando.lower()
    resultado = ""

    if tipo == "tabela":
        if "média" in comando_lower or "media" in comando_lower:
            medias = dados.mean(numeric_only=True)
            resultado += f"📊 MÉDIAS CALCULADAS:\n{medias.to_string()}\n\n"

        if "total" in comando_lower or "soma" in comando_lower:
            somas = dados.sum(numeric_only=True)
            resultado += f"💰 SOMA TOTAL:\n{somas.to_string()}\n\n"

        if "prever" in comando_lower or "futuro" in comando_lower or "tendência" in comando_lower:
            colunas_num = dados.select_dtypes(include=[np.number]).columns
            if len(colunas_num) > 0:
                alvo = colunas_num
                y = dados[alvo].dropna().values
                if len(y) > 1:
                    X = np.arange(len(y)).reshape(-1, 1)
                    modelo = LinearRegression()
                    modelo.fit(X, y)
                    previsao = modelo.predict(np.array([[len(y)]]))
                    resultado += f"🔮 PREVISÃO DA IA ({alvo}): {previsao:.2f}\n\n"

        if resultado == "":
            resultado = f"📋 RESUMO ESTATÍSTICO COMPLETO:\n{dados.describe().to_string()}"

    elif tipo == "texto":
        palavras = dados.split()
        linhas = [l for l in dados.splitlines() if l.strip()]
        resultado = (
            f"📄 RESUMO DO DOCUMENTO DE TEXTO:\n"
            f"- Total de linhas lidas: {len(linhas)}\n"
            f"- Total de palavras: {len(palavras)}\n\n"
            f"Trecho extraído:\n{dados[:1500]}..."
        )
    else:
        resultado = dados

    return resultado

# 4. Interface do Usuário (Perguntas)
arquivo = st.file_uploader("1. Arraste ou escolha qualquer arquivo do escritório")

dados_lidos = None
tipo_arquivo = None
col_x = None
col_y = None

# Se um arquivo foi enviado, mostra a prévia e opções de gráfico na hora
if arquivo is not None:
    dados_lidos, tipo_arquivo = ler_qualquer_arquivo(arquivo)
    
    if tipo_arquivo == "tabela":
        st.subheader("📊 Prévia da Planilha")
        st.dataframe(dados_lidos.head(20))

        colunas = dados_lidos.columns.tolist()
        if len(colunas) >= 2:
            st.subheader("📈 Configurar Gráfico")
            c1, c2 = st.columns(2)
            with c1:
                col_x = st.selectbox("Eixo Horizontal (ex: Mês, Nome):", colunas, index=0)
            with c2:
                col_y = st.selectbox("Eixo Vertical (Valores):", colunas, index=1)
            
            try:
                st.bar_chart(dados_lidos.set_index(col_x)[col_y])
            except Exception:
                st.info("Selecione uma coluna de números no Eixo Vertical para ver o gráfico.")

st.divider()

comando = st.text_area("2. O que você quer que a IA faça?", placeholder="Ex: Calcule o total, a média e faça uma previsão para o próximo mês...")

st.subheader("3. Dados para Assinatura")
col1, col2 = st.columns(2)
with col1:
    responsavel = st.text_input("Nome do Responsável")
with col2:
    cargo = st.text_input("Cargo / Setor (ex: Gerente Financeiro)")

# 5. Botão Final: Processa e Gera o Word Assinado
if st.button("✨ Gerar Relatório Oficial", type="primary"):
    if arquivo is not None and comando and responsavel:
        analise_pronta = cerebro_ia_python(dados_lidos, tipo_arquivo, comando)
        
        st.subheader("✅ Resultado da Análise")
        st.text(analise_pronta)

        # Monta o documento Word (.docx)
        doc = Document()
        doc.add_heading("Relatório Executivo de Análise", level=1)
        doc.add_paragraph(f"Arquivo analisado: {arquivo.name}")
        doc.add_paragraph(f"Solicitação: {comando}\n")

        doc.add_heading("Resultados e Estatísticas", level=2)
        doc.add_paragraph(analise_pronta)

        # Se for tabela e tiver gráfico válido, salva a imagem do gráfico dentro do Word
        if tipo_arquivo == "tabela" and col_x and col_y:
            try:
                fig, ax = plt.subplots(figsize=(6, 3))
                dados_lidos.plot(kind="bar", x=col_x, y=col_y, ax=ax, color="#1f77b4", legend=False)
                plt.title(f"{col_y} por {col_x}")
                plt.tight_layout()
                
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format="png")
                img_buffer.seek(0)
                plt.close(fig)

                doc.add_heading("Análise Visual", level=2)
                doc.add_picture(img_buffer, width=Inches(5.5))
            except Exception:
                pass

        # Linha de Assinatura no final
        doc.add_paragraph("\n\n_________________________________________________")
        doc.add_paragraph(f"{responsavel}\n{cargo}")

        # Prepara o download
        buffer_word = io.BytesIO()
        doc.save(buffer_word)
        buffer_word.seek(0)

        st.download_button(
            label="📥 Baixar Relatório Oficial (.docx)",
            data=buffer_word,
            file_name=f"Relatorio_{responsavel}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("Por favor, envie um arquivo, escreva o comando e preencha o nome do responsável.")
