import streamlit as st
import pandas as pd
from io import BytesIO
from Modulo import *

# Lista de operações
operacoes = ["Somar", "Subtrair", "Multiplicar", "Dividir", "Contar", "Contagem Distinta", "Primeiro", "Média", "Porcentagem"]

# Nome na aba
st.set_page_config(page_title='Relatório Dinâmico', layout="wide")

st.markdown("<h1 style='text-align:center;font-size:80px; color:#006666; margin:2rem 0rem;'>📊 Relatório Dinâmico</h1>", unsafe_allow_html=True)

# Nome etapa
st.markdown("<h3 style='text-align:left;font-size:28px; color:#005654; margin:0rem 0rem;'>📂 Envie o arquivo Principal</h3>", unsafe_allow_html=True)

# Texto explicativo arquivo mãe
st.markdown("<h3 style='text-align:left;font-size:1apx; color:#00C0BB; margin:0rem 0rem;'>Este arquivo será usado como arquivo principal, mantendo todas as colunas.</h3>", unsafe_allow_html=True)

# Upload do arquivo mãe
arquivo_mae = st.file_uploader("📂", type=["csv", "xlsx", "xls"])
df_mae = converter_para_dataframe(arquivo_mae)

if df_mae is not None:
    st.markdown("<h3 style='text-align:left;font-size:15px; color:#005654; margin:0rem 0rem;'>📄 Visualização do Arquivo Principal</h3>", unsafe_allow_html=True)
    st.dataframe(df_mae.head(3))

    st.markdown("<h3 style='text-align:left;font-size:15px; color:#005654; margin:0rem 0rem;'>A coluna-chave deve existir em todos os arquivos.</h3>", unsafe_allow_html=True)

    chave_mae = st.selectbox("🔑 Selecione a COLUNA-CHAVE", sorted(df_mae.columns))

    df_mae = df_mae.rename(columns={chave_mae: "CHAVE_MERGE"})
    resultados = []

    st.markdown("---")

    if "adicionando_arquivos" not in st.session_state:
        st.session_state.adicionando_arquivos = False

    if st.button("Adicionar Arquivo"):
        st.session_state.adicionando_arquivos = True

    if not st.session_state.adicionando_arquivos:
        st.markdown('Combinar arquivos')

    if st.session_state.adicionando_arquivos:
        for i in range(3):
            st.markdown("<h3 style='text-align:left;font-size:15px; color:#00C0BB; margin:0rem 0rem;'>Apenas as colunas selecionadas nestes arquivos serão unidas ao arquivo principal.</h3>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='text-align:left;font-size:28px; color:#005654; margin:0rem 0rem;'>📂 Adicionar Arquivo {i+1}</h3>", unsafe_allow_html=True)

            arquivo_filho = st.file_uploader(f"📂 {i+1}", type=["csv", "xlsx", "xls"], key=f"filho_{i}")
            df_filho = converter_para_dataframe(arquivo_filho)

            if df_filho is not None:
                st.markdown("<h3 style='text-align:left;font-size:15px; color:#005654; margin:0rem 0rem;'>📄 Visualização do Arquivo</h3>", unsafe_allow_html=True)
                st.dataframe(df_filho.head(3))

                agrupamentos = []
                add_agrupamento = True
                j = 0

                try:
                    while add_agrupamento and j < 5:
                        st.markdown(f"<h3 style='text-align:left;font-size:22px; color:#005654; margin:0rem 0rem;'>🔗 Seleção {j+1} para arquivo {i+1}</h3>", unsafe_allow_html=True)
                        st.markdown("<h3 style='text-align:left;font-size:14px; color:#005654; margin:0rem 0rem;'>A coluna-chave deve existir em todos os arquivos; a partir dela, será feito o agrupamento das colunas selecionadas.</h3>", unsafe_allow_html=True)
                        
                        col_chave = st.selectbox(f"🔑 Selecione a coluna CHAVE", sorted(df_filho.columns.tolist()), key=f"chave_{i}_{j}")
                        colunas_escolhidas = st.multiselect(f"✅ Quais colunas agregar?", sorted(df_filho.columns.tolist()), key=f"cols_{i}_{j}")

                        col_ops = {}
                        novos_nomes = {}

                        for col in colunas_escolhidas:
                            op = st.selectbox(f"🛠️ Operação para '{col}'", operacoes, key=f"op_{i}_{j}_{col}")
                            novo_nome = st.text_input(f"✏️ Novo nome para '{col}'", value=f"{col}_{op}", key=f"novo_nome_{i}_{j}_{col}")
                            col_ops[col] = op
                            novos_nomes[col] = novo_nome

                        st.markdown("🎯 **Filtro opcional**")
                        col_filtro = st.selectbox("Coluna para aplicar filtro", ["Nenhum"] + sorted(df_filho.columns.tolist()), key=f"filtro_col_{i}_{j}")

                        df_filtrado = df_filho.copy()

                        if col_filtro != "Nenhum":
                            valores_unicos = df_filtrado[col_filtro].dropna().unique().tolist()
                            valores_selecionados = st.multiselect(f"Selecione os valores da coluna '{col_filtro}'", valores_unicos, key=f"filtro_vals_{i}_{j}")
                            if valores_selecionados:
                                df_filtrado = df_filtrado[df_filtrado[col_filtro].isin(valores_selecionados)]

                        if col_chave in df_filtrado.columns and col_ops:
                            def agg_func(x):
                                result = {}
                                for col, oper in col_ops.items():
                                    result[novos_nomes[col]] = aplicar_operacao(x[col], oper)
                                return pd.Series(result)

                            agrupado = df_filtrado.groupby(col_chave).apply(agg_func).reset_index()
                            agrupado = agrupado.rename(columns={col_chave: "CHAVE_MERGE"})
                            agrupamentos.append(agrupado)

                        add_agrupamento = st.checkbox("➕ Adicionar novo agrupamento?", key=f"add_agrup_{i}_{j}")
                        j += 1
                        st.markdown("---")

                    df_agregado = None
                    for agrup in agrupamentos:
                        if df_agregado is None:
                            df_agregado = agrup
                        else:
                            df_agregado = df_agregado.merge(agrup, on="CHAVE_MERGE", how='outer')

                    if df_agregado is not None:
                        resultados.append(df_agregado)

                    if resultados:
                        df_merge = df_mae.copy()
                        for idx, res in enumerate(resultados):
                            df_merge = df_merge.merge(res, on="CHAVE_MERGE", how='left')

                    df_merge = df_merge.rename(columns={"CHAVE_MERGE": "Coluna Chave"})

                except Exception as e:
                    st.error(f"❌ Selecione a Coluna Chave correta: {e}")

        if "adicionando_col" not in st.session_state:
            st.session_state.adicionando_col = False

        if st.button("Adicionar Coluna"):
            st.session_state.adicionando_col = True

        if not st.session_state.adicionando_col:
            st.markdown('Adicionar Coluna de Operação')

        if st.session_state.adicionando_col:
            if "df_nova_col" not in st.session_state:
                st.session_state.df_merge_snapshot = df_merge.copy()
                st.session_state.df_nova_col = df_merge.copy()

            if "contador_operacoes" not in st.session_state:
                st.session_state.contador_operacoes = 0

            try:
                add_nova_coluna = True
                while add_nova_coluna:
                    st.markdown("<h3 style='text-align:left;font-size:22px; color:#005654; margin:0rem 0rem;'>🔧 Nova Operação entre Colunas</h3>", unsafe_allow_html=True)

                    colunas_disponiveis = st.session_state.df_nova_col.columns.tolist()
                    unique_key = st.session_state.contador_operacoes

                    colA = st.selectbox("📌 Selecione a primeira coluna", options=colunas_disponiveis, key=f"nova_op_colA_{unique_key}")
                    oper = st.selectbox("⚙️ Selecione a operação", ["Somar", "Subtrair", "Multiplicar", "Dividir", "Porcentagem"], key=f"nova_op_{unique_key}")
                    colB = st.selectbox("📌 Selecione a segunda coluna", options=colunas_disponiveis, key=f"nova_op_colB_{unique_key}")
                    novo_nome = st.text_input("✏️ Nome da nova coluna", value=f"{colA}_{oper}_{colB}", key=f"nova_col_nome_{unique_key}")

                    if st.button("✅ Aplicar operação", key=f"btn_aplicar_{unique_key}"):
                        try:
                            serieA = pd.to_numeric(st.session_state.df_nova_col[colA], errors='coerce')
                            serieB = pd.to_numeric(st.session_state.df_nova_col[colB], errors='coerce')

                            if oper == "Somar":
                                st.session_state.df_nova_col[novo_nome] = serieA + serieB
                            elif oper == "Subtrair":
                                st.session_state.df_nova_col[novo_nome] = serieA - serieB
                            elif oper == "Multiplicar":
                                st.session_state.df_nova_col[novo_nome] = serieA * serieB
                            elif oper == "Dividir":
                                st.session_state.df_nova_col[novo_nome] = serieA / serieB.replace(0, pd.NA)
                            elif oper == "Porcentagem":
                                #st.session_state.df_nova_col[novo_nome] = (serieA / serieB.replace(0, pd.NA)) * 100
                                resultado = (serieA / serieB.replace(0, pd.NA)) * 100
                                st.session_state.df_nova_col[novo_nome] = resultado.astype(str) + '%'


                            st.success(f"✅ Coluna '{novo_nome}' criada com sucesso!")
                            st.session_state.contador_operacoes += 1

                        except Exception as e:
                            st.error(f"❌ Erro ao criar a nova coluna: {e}")

                    add_nova_coluna = st.checkbox("➕ Adicionar mais uma operação entre colunas?", key=f"nova_op_add_{unique_key}")

            except Exception as e:
                st.error(f"❌ Clique em Aplicar Operação antes de adicionar uma nova operação. {e}")

            st.dataframe(st.session_state.df_nova_col.head(10))

            df_final = st.session_state.df_nova_col
            output = BytesIO()

            df_final.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                "⬇️ Baixar Excel Final",
                data=output,
                file_name="relatorio_final.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


