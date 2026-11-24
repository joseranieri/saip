"""
Módulo de Visualização: Abas Analíticas do Dashboard.

Contém a implementação isolada de cada uma das 6 abas de análise do SAIP:
  1. Visão Geral
  2. Estatísticas (Numéricas e Categóricas)
  3. Turmas e Grupos
  4. Habilidades (Matriz SAEB / BNCC)
  5. Qualidade dos Dados
  6. Relatórios e Exportação
"""

import json
import pandas as pd
import plotly.express as px
import streamlit as st

from src.skills_catalog import (
    DTYPE_LABELS_PT,
    METRIC_LABELS_PT,
    classify_proficiency,
    get_skills_catalog_df,
    match_column_to_skill,
    translate_metrics_dict,
)
from src.ui.components import (
    get_categorical_columns,
    get_numeric_columns,
    sanitize_dataframe_columns,
    show_dataframe,
)


def render_overview(df: pd.DataFrame, metrics: dict) -> None:
    """Aba 1: Exibe os cartões de resumo quantitativo da base analisada."""
    overview = metrics.get("overview", {})

    total_rows = overview.get("rows", len(df))
    total_columns = overview.get("columns", len(df.columns))
    missing = overview.get("missing_values", int(df.isna().sum().sum()))
    duplicated = overview.get("duplicate_rows", int(df.duplicated().sum()))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", f"{total_rows:,}")
    c2.metric("Variáveis", total_columns)
    c3.metric("Valores ausentes", f"{missing:,}")
    c4.metric("Duplicidades", f"{duplicated:,}")

    st.subheader("Resumo dos dados")

    numeric_count = len(get_numeric_columns(df))
    categorical_count = len(get_categorical_columns(df))

    c1, c2 = st.columns(2)
    c1.metric("Variáveis numéricas", numeric_count)
    c2.metric("Variáveis categóricas", categorical_count)


def render_descriptive_analysis(df: pd.DataFrame, metrics: dict) -> None:
    """Aba 2 (Parte 1): Estatísticas descritivas, histograma e diagrama de caixa."""
    numeric = metrics.get("numeric", {})
    numeric_columns = list(numeric.keys())

    if not numeric_columns:
        st.info("Não foram encontradas variáveis numéricas.")
        return

    st.subheader("Estatísticas descritivas")

    numeric_table = pd.DataFrame(numeric).T
    numeric_table = numeric_table.rename(
        columns=lambda col: METRIC_LABELS_PT.get(str(col).strip().lower(), col)
    )
    show_dataframe(numeric_table.reset_index(names="Variável"))

    selected = st.selectbox(
        "Selecione uma variável numérica",
        numeric_columns,
        key="descriptive_variable"
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x=selected,
            marginal="box",
            title=f"Distribuição de {selected}",
            labels={selected: selected, "count": "Frequência"},
            template="plotly_white",
            color_discrete_sequence=["#123B66"]
        )
        fig.update_layout(autosize=True, yaxis_title="Frequência")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(
            df,
            y=selected,
            title=f"Diagrama de caixa de {selected}",
            labels={selected: selected},
            template="plotly_white",
            color_discrete_sequence=["#123B66"]
        )
        fig.update_layout(autosize=True)
        st.plotly_chart(fig, use_container_width=True)


def render_categorical_analysis(df: pd.DataFrame) -> None:
    """Aba 2 (Parte 2): Tabela de frequência e gráfico de barras para variáveis categóricas."""
    categorical_columns = get_categorical_columns(df)

    if not categorical_columns:
        st.info("Não foram encontradas variáveis categóricas.")
        return

    selected = st.selectbox(
        "Selecione uma variável categórica",
        categorical_columns,
        key="categorical_variable"
    )

    frequency = (
        df[selected]
        .fillna("(Ausente)")
        .astype(str)
        .value_counts()
        .head(20)
        .rename_axis("Categoria")
        .reset_index(name="Frequência")
    )

    col1, col2 = st.columns([1, 1.5])

    with col1:
        show_dataframe(frequency)

    with col2:
        fig = px.bar(
            frequency,
            x="Categoria",
            y="Frequência",
            title=f"Frequência de {selected}",
            template="plotly_white",
            color_discrete_sequence=["#123B66"]
        )
        st.plotly_chart(fig, use_container_width=True)


def render_group_analysis(df: pd.DataFrame) -> None:
    """Aba 3: Comparação de indicadores numéricos agrupados por turma, escola ou categoria."""
    columns = get_categorical_columns(df)
    numeric_columns = get_numeric_columns(df)

    if not columns or not numeric_columns:
        st.info(
            "Esta análise exige pelo menos uma variável categórica "
            "e uma variável numérica."
        )
        return

    c1, c2 = st.columns(2)

    with c1:
        group_column = st.selectbox(
            "Agrupar por",
            columns,
            key="group_column"
        )

    with c2:
        value_column = st.selectbox(
            "Indicador numérico",
            numeric_columns,
            key="group_value"
        )

    grouped = (
        df.groupby(group_column, dropna=False)[value_column]
        .agg(
            Quantidade="count",
            Média="mean",
            Mediana="median",
            **{"Desvio padrão": "std"},
            Mínimo="min",
            Máximo="max"
        )
        .reset_index()
        .rename(columns={group_column: "Grupo"})
    )

    show_dataframe(grouped)

    fig = px.bar(
        grouped,
        x="Grupo",
        y="Média",
        title=f"Média de {value_column} por {group_column}",
        template="plotly_white",
        color_discrete_sequence=["#123B66"]
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_analysis(df: pd.DataFrame) -> None:
    """
    Aba 4: Análise Pedagógica por Habilidades (SAEB / BNCC).
    Cruza os indicadores do CSV com a matriz oficial de Língua Portuguesa (8º Ano)
    e disponibiliza o catálogo completo para consulta e filtro.
    """
    st.subheader("Análise Pedagógica por Habilidades (SAEB / BNCC)")
    st.caption(
        "Matriz de referência: Língua Portuguesa — 8º Ano "
        "(1º Simulado SAEB/2026 — SEMEC Teresina)."
    )

    numeric_columns = get_numeric_columns(df)
    catalog_df = get_skills_catalog_df()

    if numeric_columns:
        rows = []
        for col in numeric_columns:
            matched = match_column_to_skill(col)
            mean_val = float(df[col].mean())

            # Normaliza a escala para percentual (0-1 -> 0-100%; 0-10 -> 0-100%)
            max_val = float(df[col].max()) if df[col].notna().any() else 100.0
            if max_val <= 1.0:
                pct_val = round(mean_val * 100, 2)
            elif max_val <= 10.0:
                pct_val = round(mean_val * 10, 2)
            else:
                pct_val = round(mean_val, 2)

            rows.append({
                "Coluna no Arquivo": col,
                "Código SAEB": matched["codigo_saeb"] if matched else "Não mapeado",
                "Código BNCC": matched["codigo_bncc"] if matched else "—",
                "Descrição da Habilidade": (
                    matched["descricao_bncc"]
                    if matched
                    else "Coluna numérica sem vínculo automático com código SAEB/BNCC."
                ),
                "Eixo SAEB": matched["eixo_saeb"] if matched else "—",
                "Média Bruta": round(mean_val, 2),
                "Aproveitamento (%)": pct_val,
                "Mediana": round(float(df[col].median()), 2),
                "Desvio Padrão": round(float(df[col].std()), 2) if len(df) > 1 else 0.0,
                "Registros Válidos": int(df[col].count()),
                "Nível Pedagógico": classify_proficiency(pct_val),
            })

        summary = pd.DataFrame(rows)
        mapped_count = (summary["Código SAEB"] != "Não mapeado").sum()

        # Identifica o maior e o menor aproveitamento para destaque pedagógico
        best_row = summary.loc[summary["Aproveitamento (%)"].idxmax()]
        worst_row = summary.loc[summary["Aproveitamento (%)"].idxmin()]

        m1, m2, m3 = st.columns(3)
        m1.metric("Indicadores Analisados", len(summary))
        m2.metric("Habilidades SAEB Identificadas", mapped_count)
        m3.metric(
            "Aproveitamento Médio Geral",
            f"{summary['Aproveitamento (%)'].mean():.1f}%"
        )

        c_best, c_worst = st.columns(2)
        with c_best:
            st.markdown(
                f"""
                <div class="skill-card skill-card-success">
                    <strong>Maior Domínio: {best_row['Coluna no Arquivo']} ({best_row['Código SAEB']})</strong><br>
                    <span style="font-size: 13px; color: #276749;">
                        Aproveitamento médio: <b>{best_row['Aproveitamento (%)']:.1f}%</b> — {best_row['Nível Pedagógico']}
                    </span><br>
                    <span style="font-size: 12px; color: #172B4D;">
                        {best_row['Descrição da Habilidade']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c_worst:
            st.markdown(
                f"""
                <div class="skill-card skill-card-warning">
                    <strong>Foco de Recomposição: {worst_row['Coluna no Arquivo']} ({worst_row['Código SAEB']})</strong><br>
                    <span style="font-size: 13px; color: #9B2C2C;">
                        Aproveitamento médio: <b>{worst_row['Aproveitamento (%)']:.1f}%</b> — {worst_row['Nível Pedagógico']}
                    </span><br>
                    <span style="font-size: 12px; color: #172B4D;">
                        {worst_row['Descrição da Habilidade']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        summary["Rótulo Gráfico"] = summary.apply(
            lambda r: (
                f"{r['Código SAEB']} ({r['Coluna no Arquivo']})"
                if r["Código SAEB"] != "Não mapeado"
                else r["Coluna no Arquivo"]
            ),
            axis=1
        )

        color_map = {
            "Adequado (≥ 70%)": "#2F855A",
            "Intermediário (50% - 69%)": "#D69E2E",
            "Crítico / Recomposição (< 50%)": "#C53030",
            "Sem dados": "#718096",
        }

        fig = px.bar(
            summary.sort_values("Aproveitamento (%)", ascending=True),
            x="Aproveitamento (%)",
            y="Rótulo Gráfico",
            color="Nível Pedagógico",
            orientation="h",
            title="Desempenho por Habilidade / Indicador (%)",
            template="plotly_white",
            color_discrete_map=color_map,
            hover_data={
                "Código BNCC": True,
                "Descrição da Habilidade": True,
                "Média Bruta": True,
                "Rótulo Gráfico": False,
            },
            range_x=[0, 100],
        )
        fig.update_layout(
            yaxis_title="Habilidade / Indicador",
            xaxis_title="Aproveitamento Médio (%)",
            legend_title="Classificação Pedagógica",
            height=max(380, len(summary) * 45),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detalhamento Estatístico e Pedagógico")
        display_cols = [
            "Coluna no Arquivo",
            "Código SAEB",
            "Código BNCC",
            "Descrição da Habilidade",
            "Média Bruta",
            "Aproveitamento (%)",
            "Mediana",
            "Desvio Padrão",
            "Nível Pedagógico",
        ]
        show_dataframe(summary[display_cols])

    else:
        st.info(
            "Nenhuma coluna numérica foi encontrada na base atual. "
            "Para cruzamento automático, nomeie as colunas do CSV com o código "
            "da habilidade (ex.: 9L2.1.G ou EF69LP14) ou da questão (ex.: B1_Q12)."
        )

    st.divider()

    # Catálogo interativo de consulta das habilidades oficiais
    with st.expander(
        "Catálogo Oficial de Habilidades — Língua Portuguesa (8º Ano | SAEB 2026)",
        expanded=not bool(numeric_columns)
    ):
        f1, f2 = st.columns([1, 2])
        with f1:
            bloco_filter = st.selectbox(
                "Filtrar por Bloco do Simulado",
                ["Todos os Blocos", "Bloco 1", "Bloco 2"],
                key="skill_bloco_filter"
            )
        with f2:
            search_term = st.text_input(
                "Buscar habilidade por código ou palavra-chave",
                placeholder="Ex.: 9L2.1.G, EF69LP14, metáfora, reclamação, poema...",
                key="skill_search_term"
            )

        filtered_catalog = catalog_df.copy()

        if bloco_filter != "Todos os Blocos":
            filtered_catalog = filtered_catalog[
                filtered_catalog["Bloco"].str.contains(bloco_filter, case=False, na=False)
            ]

        if search_term.strip():
            term = search_term.strip()
            mask = (
                filtered_catalog["Código SAEB"].str.contains(term, case=False, na=False)
                | filtered_catalog["Código BNCC"].str.contains(term, case=False, na=False)
                | filtered_catalog["Habilidade SAEB"].str.contains(term, case=False, na=False)
                | filtered_catalog["Descrição BNCC"].str.contains(term, case=False, na=False)
            )
            filtered_catalog = filtered_catalog[mask]

        st.caption(f"Exibindo {len(filtered_catalog)} de {len(catalog_df)} habilidades mapeadas.")

        catalog_display_cols = [
            "Código SAEB",
            "Código BNCC",
            "Bloco",
            "Questões Bloco 1 (Gab.)",
            "Questões Bloco 2 (Gab.)",
            "Habilidade SAEB",
            "Descrição BNCC",
        ]
        show_dataframe(filtered_catalog[catalog_display_cols])


def render_quality_analysis(df: pd.DataFrame) -> None:
    """Aba 5: Diagnóstico de integridade, tipos de dados e completude por coluna."""
    quality = pd.DataFrame({
        "Coluna": list(df.columns),
        "Tipo de dado": [
            DTYPE_LABELS_PT.get(str(df[col].dtype), str(df[col].dtype))
            for col in df.columns
        ],
        "Valores ausentes": [
            int(df[col].isna().sum()) for col in df.columns
        ],
        "Valores distintos": [
            int(df[col].nunique(dropna=True)) for col in df.columns
        ],
        "Completude (%)": [
            round(df[col].notna().mean() * 100, 2)
            for col in df.columns
        ]
    })

    show_dataframe(quality)

    fig = px.bar(
        quality,
        x="Coluna",
        y="Completude (%)",
        title="Completude por variável",
        range_y=[0, 100],
        template="plotly_white",
        color_discrete_sequence=["#123B66"]
    )
    st.plotly_chart(fig, use_container_width=True)


def render_report(df: pd.DataFrame, metrics: dict) -> None:
    """Aba 6: Exportação da base tratada em CSV e das métricas traduzidas em JSON."""
    st.subheader("Exportação dos resultados")

    clean_df = sanitize_dataframe_columns(df)
    csv_data = clean_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar dados analisados (CSV)",
        data=csv_data,
        file_name="saip_dados_analisados.csv",
        mime="text/csv",
        use_container_width=True
    )

    translated_metrics = translate_metrics_dict(metrics)
    json_data = json.dumps(
        translated_metrics,
        ensure_ascii=False,
        indent=4,
        default=str
    )

    st.download_button(
        "Baixar métricas (JSON)",
        data=json_data.encode("utf-8"),
        file_name="saip_metricas.json",
        mime="application/json",
        use_container_width=True
    )
