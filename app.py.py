import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pontuação do Currículo", layout="wide")

st.title("Sistema de Pontuação de Currículo")
st.markdown("Preencha a **quantidade** de itens que você possui em cada categoria. O sistema calculará automaticamente a pontuação, respeitando os limites máximos.")

# Dados base dos itens
data = [
    ["1.1 Artigo com percentil ≥ 75", 10.0, 999],
    ["1.2 Artigo com 50 ≤ percentil < 75", 8.0, 999],
    ["1.3 Artigo com 25 ≤ percentil < 50", 6.0, 12.0],
    ["1.4 Artigo com percentil < 25", 2.0, 4.0],
    ["1.5 Artigo sem percentil", 1.0, 2.0],
    ["2.1 Trabalhos completos em eventos (≥2p)", 0.6, 3.0],
    ["2.2 Resumos publicados (<2p)", 0.3, 1.5],
    ["3.1 Capítulo de livro ou boletim técnico", 1.0, 4.0],
    ["3.2 Livro na íntegra", 4.0, 4.0],
    ["4. Curso de especialização (min 320h)", 1.0, 1.0],
    ["5. Monitoria de disciplina", 0.6, 2.4],
    ["6.1 Iniciação científica com bolsa", 0.4, 16.0],
    ["6.2 Iniciação científica sem bolsa", 0.2, 8.0],
    ["7.1 Software/Aplicativo (INPI)", 1.0, 5.0],
    ["7.2 Patente (INPI)", 1.0, 5.0],
    ["7.3 Registro de cultivar (MAPA)", 1.0, 5.0],
    ["8. Orientação de alunos (IC/TCC/extensão)", 1.0, 2.0],
    ["9. Participação em bancas (TCC/especialização)", 0.25, 1.0],
    ["10.1 Docência no Ensino Superior", 1.0, 8.0],
    ["10.2 Docência no Fundamental/Médio", 0.3, 3.0],
    ["10.3 Atuação em EAD", 0.2, 2.0],
    ["10.4 Atividades profissionais nas áreas do edital", 0.25, 4.0],
]

# Criar DataFrame
df = pd.DataFrame(data, columns=["Item", "Pontuação por Item", "Pontuação Máxima por Item"])
df["Quantidade"] = 0
df["Total"] = 0.0

# Interface de preenchimento
for i in range(len(df)):
    df.at[i, "Quantidade"] = st.number_input(f"{df.at[i, 'Item']}", min_value=0, step=1, key=f"input_{i}")
    total = df.at[i, "Pontuação por Item"] * df.at[i, "Quantidade"]
    maximo = df.at[i, "Pontuação Máxima por Item"]
    df.at[i, "Total"] = min(total, maximo)

# Exibir tabela
st.markdown("### Resultado")
st.dataframe(df[["Item", "Pontuação por Item", "Pontuação Máxima por Item", "Quantidade", "Total"]], use_container_width=True)

# Total geral
total_geral = df["Total"].sum()
st.subheader(f"🧮 Pontuação Total: {total_geral:.2f}")
