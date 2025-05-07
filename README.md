
# Avaliação de Currículo - App Streamlit

Este aplicativo permite que candidatos preencham a pontuação de seu currículo acadêmico com base em critérios específicos.

## Recursos

- Entrada da quantidade de itens realizados
- Cálculo automático da pontuação total
- Respeito aos limites máximos por item
- Geração de CSV com os dados preenchidos
- Geração de PDF com relatório nominal e detalhado

## Instruções

1. Faça upload do arquivo `formulario_pontuacao_do_curriculo.xlsx` no mesmo diretório do app.
2. Execute com:

```bash
streamlit run app.py
```

3. Preencha seu nome e quantidades conforme o formulário.
4. Baixe os arquivos gerados (CSV e PDF).

## Requisitos

- streamlit
- pandas
- reportlab
- openpyxl
