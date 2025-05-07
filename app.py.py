
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Pontuação do Currículo", layout="centered")

st.title("Avaliação de Currículo do Candidato")
st.markdown("Preencha abaixo com seu nome e as quantidades de itens que se aplicam ao seu currículo.")

# Nome do candidato
dados = pd.read_excel("formulario_pontuacao_do_curriculo.xlsx", skiprows=3)
dados = dados[["Unnamed: 0", "Unnamed: 1", "Unnamed: 2"]]
dados.columns = ["Item", "Pontuacao_por_item", "Pontuacao_maxima"]
dados = dados.dropna(subset=["Pontuacao_por_item"]).reset_index(drop=True)
dados["Pontuacao_por_item"] = pd.to_numeric(dados["Pontuacao_por_item"], errors='coerce')
dados["Pontuacao_maxima"] = pd.to_numeric(dados["Pontuacao_maxima"], errors='coerce')

nome = st.text_input("Nome completo do(a) candidato(a):")
st.markdown("---")

quantidades = []
total_pontos = []

st.subheader("Itens Avaliados")
for idx, row in dados.iterrows():
    q = st.number_input(row["Item"], min_value=0, step=1, key=row["Item"])
    quantidades.append(q)
    total = row["Pontuacao_por_item"] * q
    if not pd.isna(row["Pontuacao_maxima"]):
        total = min(total, row["Pontuacao_maxima"])
    total_pontos.append(total)

dados["Quantidade"] = quantidades
dados["Total"] = total_pontos
pontuacao_total = sum(total_pontos)

st.markdown("---")
st.write("### Pontuação Final")
st.dataframe(dados[["Item", "Pontuacao_por_item", "Quantidade", "Total"]])
st.metric(label="Pontuação Total do Currículo", value=round(pontuacao_total, 2))

# Gerar PDF
def gerar_pdf(nome, dados, total):
    pdf_file = f"pontuacao_{nome.replace(' ', '_')}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "Relatório de Pontuação Curricular")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Nome: {nome}")
    c.drawString(50, height - 110, f"Pontuação Total: {round(total, 2)}")

    y = height - 140
    for _, row in dados.iterrows():
        if row["Quantidade"] > 0:
            texto = f"{row['Item'][:100]}... - Quantidade: {int(row['Quantidade'])} - Total: {round(row['Total'], 2)}"
            c.drawString(50, y, texto)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
    c.save()
    return pdf_file

if st.button("Gerar Relatório PDF e CSV"):
    if not nome.strip():
        st.warning("Por favor, preencha seu nome.")
    else:
        csv = dados.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar CSV", csv, file_name=f"pontuacao_{nome.replace(' ', '_')}.csv")
        pdf_path = gerar_pdf(nome.strip(), dados, pontuacao_total)
        with open(pdf_path, "rb") as f:
            st.download_button("Baixar Relatório em PDF", f.read(), file_name=pdf_path, mime="application/pdf")
