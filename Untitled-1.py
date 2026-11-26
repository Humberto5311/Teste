import streamlit as st

# 1. Configura o título da aba e o visual da página
st.set_page_config(page_title="Assistente de Escritório IA", layout="centered")

# 2. Cabeçalho do Software
st.title("📂 Assistente Inteligente de Escritório")
st.write("Envie seu documento, dê a ordem e gere um relatório assinado.")
st.divider() # Cria uma linha cinza divisória para organizar a UI

# 3. Área de Upload (em vez de digitar o nome do arquivo no terminal)
arquivo = st.file_uploader("1. Escolha a planilha ou documento", type=["xlsx", "csv", "txt", "docx", "pdf", "pptx", "jpg", "png", "jpeg"])


# 4. Caixa de texto grande para você dar a ordem
comando = st.text_area("2. O que você quer analisar ou calcular?", placeholder="Ex: Calcule o total de vendas e faça um resumo executivo...")

# 5. Dados para a Assinatura no Relatório
st.subheader("3. Dados para Assinatura")
col1, col2 = st.columns(2) # Divide a tela em 2 colunas lado a lado
with col1:
    responsavel = st.text_input("Nome do Responsável")
with col2:
    cargo = st.text_input("Cargo / Setor (ex: Gerente Financeiro)")


# 6. Botão de Ação
if st.button("Gerar Relatório Oficial", type="primary"):
    if arquivo and comando and responsavel:
        st.success(f"Tudo pronto, {responsavel}! Agora vamos conectar a IA aqui.")
    else:
        st.warning("Por favor, preencha o arquivo, o comando e o seu nome.")

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def cerebro_ia_python(tabela, comando):
    comando = comando.lower() # Deixa tudo minúsculo para facilitar a leitura
    resultado = ""

    # 1. Inteligência de Interpretação (NLP básico)
    if "média" in comando or "media" in comando:
        # Calcula a média de todas as colunas numéricas automaticamente
        medias = tabela.mean(numeric_only=True)
        resultado += f"📊 **Médias Calculadas:**\n{medias.to_string()}\n\n"

    if "total" in comando or "soma" in comando:
        somas = tabela.sum(numeric_only=True)
        resultado += f"💰 **Soma Total:**\n{somas.to_string()}\n\n"

    # 2. Inteligência Preditiva (Machine Learning real com Scikit-Learn)
    if "prever" in comando or "futuro" in comando or "tendência" in comando:
        # Pega a primeira coluna de números da planilha para treinar o modelo
        colunas_numericas = tabela.select_dtypes(include=[np.number]).columns
        if len(colunas_numericas) > 0:
            alvo = colunas_numericas[0]
            y = tabela[alvo].dropna().values
            X = np.arange(len(y)).reshape(-1, 1) # Cria a linha do tempo (Mês 1, 2, 3...)

            # Treina a IA com os dados da planilha
            modelo = LinearRegression()
            modelo.fit(X, y)

            # Prevê o próximo passo (próximo mês/linha)
            proximo_passo = np.array([[len(y)]])
            previsao = modelo.predict(proximo_passo)[0]
            resultado += f"🔮 **Previsão da IA para o próximo período ({alvo}):** {previsao:.2f}\n\n"

    # Se não pediu nada específico, faz um raio-X estatístico completo
    if resultado == "":
        resultado = f"📋 **Resumo Geral dos Dados:**\n{tabela.describe().to_string()}"

    return resultado

import io
from docx import Document

# 1. Cria o documento Word em branco
doc = Document()
doc.add_heading("Relatório Executivo de Análise", level=1)
doc.add_paragraph(f"Arquivo analisado: {arquivo.name}")
doc.add_paragraph(f"Solicitação: {comando}\n")

# 2. Coloca o resultado que a sua IA Python calculou
doc.add_heading("Resultados e Estatísticas", level=2)
doc.add_paragraph(analise_pronta)

# 3. Cria o bloco oficial de assinatura no final da página
doc.add_paragraph("\n\n_________________________________________________")
doc.add_paragraph(f"{responsavel}\n{cargo}")

# 4. Salva na memória e cria o botão de baixar na tela
buffer_word = io.BytesIO()
doc.save(buffer_word)
buffer_word.seek(0)

st.download_button(
    label="📥 Baixar Relatório Oficial (.docx)",
    data=buffer_word,
    file_name=f"Relatorio_{responsavel}.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
