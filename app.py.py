import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Pontuação do Currículo", layout="wide")
st.title("Sistema de Pontuação de Currículo")
st.markdown("📝 **Atenção:** Os comprovantes de um dado item devem ser enviados em **um único arquivo PDF**. Por exemplo, se você tem dois artigos referentes ao item 1.1, estes devem ser mesclados em **um único arquivo PDF** a ser enviado para o item 1.1.")

nome = st.text_input("Nome completo do(a) candidato(a):")
st.markdown("Preencha a **quantidade** e envie os **comprovantes em PDF** para cada item. O sistema calculará automaticamente a pontuação, respeitando os limites definidos no Edital")

# Dados base dos itens com pontuações máximas revisadas corretamente
data = [
    ["1.1 Artigo com percentil ≥ 75", 10.0, 0],
    ["1.2 Artigo com 50 ≤ percentil < 75", 8.0, 0],
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
    ["10.4 Atividades profissionais relacionadas", 0.25, 4.0],
]

st.divider()
df = pd.DataFrame(data, columns=["Item", "Pontuação por Item", "Pontuação Máxima"])
df["Quantidade"] = 0
df["Total"] = 0.0
comprovantes = {}

# Novo campo: Histórico Escolar
st.divider()
st.markdown("### Histórico Escolar do(a) Candidato(a)")
historico_media = st.number_input("Média aritmética das disciplinas cursadas na graduação:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

for i in range(len(df)):
    item = df.at[i, "Item"]
    ponto = df.at[i, "Pontuação por Item"]
    maximo = df.at[i, "Pontuação Máxima"]
    if maximo > 0:
        max_qtd = round(maximo / ponto)
    else:
        max_qtd = 999
    col1, col2 = st.columns([3, 2])
    with col1:
        unit_label = "/mês" if "6.1" in item else "/mês" if "6.2" in item else "/semestre" if "10." in item or "5." in item else "/mês" if "6.2" in item else "/semestre" if "10." in item else "/artigo" if "1." in item else "/unidade"
        df.at[i, "Quantidade"] = st.number_input(f"{item} ({ponto}{unit_label})", min_value=0, max_value=max_qtd, step=1, key=f"qtd_{i}")
    with col2:
        comprovantes[item] = st.file_uploader(f"Comprovante único em PDF de '{item}'", type="pdf", key=f"file_{i}")
    df.at[i, "Total"] = ponto * df.at[i, "Quantidade"]

pontuacao_total = df["Total"].sum()
st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

if st.button("✉️ Gerar Relatório com Anexos"):
    if not nome.strip():
        st.warning("Por favor, informe o nome completo do(a) candidato(a).")
    elif historico_pdf is None:
        st.warning("O Histórico Escolar é obrigatório. Por favor, anexe o arquivo em PDF.")
    elif any(df["Quantidade"].iloc[i] > 0 and comprovantes[df.at[i, "Item"]] is None for i in range(len(df))):
        st.warning("Há itens com quantidade informada, mas sem comprovante anexado. Verifique todos os campos.")
        st.warning("Por favor, informe o nome completo do(a) candidato(a).")
    else:
        # Gerar PDF de relatório principal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph(f"Relatório de Pontuação - {nome}", styles['Title']), Spacer(1, 12)]
        data_table = [["Item", "Quantidade", "Total"]] + df[df["Quantidade"] > 0][["Item", "Quantidade", "Total"]].values.tolist()
        table = Table(data_table, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Pontuação Final: {pontuacao_total:.2f} pontos", styles['Normal']))
        doc.build(elements)

        # Montar PDF final com separadores e comprovantes
        merger = PdfMerger()
        merger.append(buffer)

        # Adiciona capa e histórico escolar antes dos demais comprovantes
        if historico_pdf is not None:
            capa_hist = BytesIO()
            capa_doc = SimpleDocTemplate(capa_hist, pagesize=A4)
            capa_elem = [Paragraph("Histórico Escolar", styles['Heading2']), Paragraph(f"Média Geral: {historico_media:.2f}", styles['Normal'])]
            capa_doc.build(capa_elem)
            merger.append(capa_hist)
            merger.append(historico_pdf)

        for item, arquivo in comprovantes.items():
            if arquivo is not None:
                capa_buffer = BytesIO()
                capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
                capa_elements = [Paragraph(f"Comprovante para o item: {item}", styles['Heading2'])]
                capa_doc.build(capa_elements)
                merger.append(capa_buffer)
                merger.append(arquivo)

        final_output = BytesIO()
        merger.write(final_output)
        merger.close()

        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="🔗 Baixar Relatório Final em PDF",
            data=final_output.getvalue(),
            file_name=f"relatorio_{nome.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
