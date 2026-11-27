"""
Módulo de Visualização: Abas Analíticas do Dashboard.

Contém a implementação completa de todas as abas de análise do SAIP:
  1. Visão Geral (render_overview)
  2. Evolução Temporal 1º ao 8º Simulado (render_temporal_analysis)
  3. Habilidades SAEB / BNCC (render_skill_analysis)
  4. Estatísticas Numéricas e Categóricas (render_descriptive_analysis, render_categorical_analysis)
  5. Turmas e Grupos (render_group_analysis)
  6. Qualidade dos Dados (render_quality_analysis)
  7. Relatórios e Exportação PDF/CSV/JSON (render_report)
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import get_datasets_by_year, list_datasets
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


def _apply_responsive_legend(fig, bottom_margin: int = 105):
    """Posiciona a legenda horizontalmente abaixo do gráfico para melhor leitura no mobile."""
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            title_text="",
        ),
        margin=dict(l=20, r=20, t=55, b=bottom_margin),
    )
    return fig


def _classify_macro_eixo(codigo_saeb: str, eixo_saeb: str = "") -> str:
    """Agrupa códigos SAEB nos 4 Macro-Eixos Cognitivos para comparação temporal."""
    code = str(codigo_saeb).strip().upper()
    eixo = str(eixo_saeb).strip().lower()

    if code.startswith(("5AL", "9AL")):
        return "4. Análise Linguística e Coesão"

    if any(
        code.startswith(prefix)
        for prefix in ("5L1.1", "5L1.2", "9L1.2.I", "9L1.2.D", "9L1.3.G", "9L1.3.I")
    ) or "localizar informação" in eixo or "ideia central" in eixo:
        return "1. Compreensão e Localização Textual"

    if any(
        code.startswith(prefix)
        for prefix in (
            "5L2.6", "5L2.7", "5L2.8", "5L3.1",
            "9L2.3", "9L2.6", "9L2.7", "9L2.9",
            "9L1.1.C", "9L1.4",
        )
    ) or "inferir" in eixo or "fatos de opiniões" in eixo or "persuasivos" in eixo:
        return "3. Inferência, Semântica e Senso Crítico"

    if code.startswith(("5L", "9L")):
        return "2. Gêneros e Estrutura Composicional"

    return "Outros Indicadores"


def _build_skill_summary(df: pd.DataFrame, simulado_num: int | None = None) -> pd.DataFrame:
    """Calcula aproveitamento e metadados SAEB/BNCC das colunas numéricas."""
    ignore_meta_cols = {"Simulado", "Ordem_Simulado", "Ano_Letivo"}
    eval_df = df.drop(columns=[c for c in ignore_meta_cols if c in df.columns])
    numeric_columns = get_numeric_columns(eval_df)

    rows = []
    for col in numeric_columns:
        matched = match_column_to_skill(col, preferred_simulado_num=simulado_num)
        mean_val = float(eval_df[col].mean())

        max_val = float(eval_df[col].max()) if eval_df[col].notna().any() else 100.0
        if max_val <= 1.0:
            pct_val = round(mean_val * 100, 2)
        elif max_val <= 10.0:
            pct_val = round(mean_val * 10, 2)
        else:
            pct_val = round(mean_val, 2)

        codigo_saeb = matched["codigo_saeb"] if matched else "Não mapeado"
        eixo_saeb = matched["eixo_saeb"] if matched else "—"

        rows.append({
            "Coluna no Arquivo": col,
            "Código SAEB": codigo_saeb,
            "Código BNCC": matched["codigo_bncc"] if matched else "—",
            "Macro-Eixo": _classify_macro_eixo(codigo_saeb, eixo_saeb),
            "Descrição da Habilidade": (
                matched["descricao_bncc"]
                if matched
                else "Coluna numérica sem vínculo automático com código SAEB/BNCC."
            ),
            "Eixo SAEB": eixo_saeb,
            "Média Bruta": round(mean_val, 2),
            "Aproveitamento (%)": pct_val,
            "Mediana": round(float(eval_df[col].median()), 2),
            "Desvio Padrão": round(float(eval_df[col].std()), 2) if len(eval_df) > 1 else 0.0,
            "Registros Válidos": int(eval_df[col].count()),
            "Nível Pedagógico": classify_proficiency(pct_val),
        })

    return pd.DataFrame(rows)


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


def render_temporal_analysis(default_year: int = 2026) -> None:
    """Aba 2: Evolução Temporal (1º ao 8º Simulado)."""
    st.subheader("Evolução Temporal dos Simulados (Ciclo Anual de 8 Avaliações)")
    st.caption(
        "Acompanhe a progressão pedagógica do 1º ao 8º Simulado por média geral, "
        "Macro-Eixos Cognitivos e habilidades recorrentes."
    )

    all_items = list_datasets()
    available_years = sorted(
        {int(item.get("ano_letivo", default_year)) for item in all_items} | {int(default_year)},
        reverse=True,
    )

    selected_year = st.selectbox(
        "Ano Letivo de Referência",
        options=available_years,
        index=0,
        key="temporal_year_selector",
    )

    datasets = get_datasets_by_year(selected_year)

    if not datasets:
        st.info(
            f"Nenhum simulado foi salvo na base local para o ano de {selected_year}. "
            "Acesse Carga de Dados no menu lateral para enviar um arquivo CSV."
        )
        return

    loaded_nums = {int(d.get("simulado_num", 1)) for d in datasets}
    status_cols = st.columns(8)
    for idx in range(1, 9):
        with status_cols[idx - 1]:
            if idx in loaded_nums:
                st.success(f"**{idx}º Sim.**\n\nImportado")
            else:
                st.warning(f"**{idx}º Sim.**\n\nPendente")

    timeline_rows = []
    macro_rows = []
    skill_rows = []
    per_simulado_summaries = []

    for item in datasets:
        sim_num = int(item.get("simulado_num", 1))
        sim_label = f"{sim_num}º Simulado"
        sim_df = sanitize_dataframe_columns(pd.DataFrame(item["records"]))

        skill_summary = _build_skill_summary(sim_df, simulado_num=sim_num)
        if skill_summary.empty:
            continue

        mapped = skill_summary[skill_summary["Código SAEB"] != "Não mapeado"]
        eval_basis = mapped if not mapped.empty else skill_summary

        avg_pct = round(float(eval_basis["Aproveitamento (%)"].mean()), 2)
        std_pct = (
            round(float(eval_basis["Aproveitamento (%)"].std()), 2)
            if len(eval_basis) > 1
            else 0.0
        )

        timeline_rows.append({
            "Ordem": sim_num,
            "Simulado": sim_label,
            "Registros": item["row_count"],
            "Aproveitamento Médio (%)": avg_pct,
            "Dispersão entre Habilidades (DP)": std_pct,
        })

        per_simulado_summaries.append({
            "simulado_num": sim_num,
            "simulado_label": sim_label,
            "name": item.get("name", sim_label),
            "row_count": item.get("row_count", len(sim_df)),
            "summary_df": skill_summary,
        })

        if not mapped.empty:
            by_macro = (
                mapped.groupby("Macro-Eixo", as_index=False)["Aproveitamento (%)"]
                .mean()
            )
            for _, m_row in by_macro.iterrows():
                macro_rows.append({
                    "Ordem": sim_num,
                    "Simulado": sim_label,
                    "Macro-Eixo": m_row["Macro-Eixo"],
                    "Aproveitamento (%)": round(float(m_row["Aproveitamento (%)"]), 2),
                })

            for _, s_row in mapped.iterrows():
                skill_rows.append({
                    "Ordem": sim_num,
                    "Simulado": sim_label,
                    "Código SAEB": s_row["Código SAEB"],
                    "Descrição": s_row["Descrição da Habilidade"],
                    "Aproveitamento (%)": s_row["Aproveitamento (%)"],
                })

    if not timeline_rows:
        st.warning("Os simulados salvos não possuem colunas numéricas avaliáveis.")
        return

    timeline_df = pd.DataFrame(timeline_rows).sort_values("Ordem")
    timeline_df["Variação (Δ p.p.)"] = timeline_df["Aproveitamento Médio (%)"].diff().round(2)

    first_sim = timeline_df.iloc[0]
    last_sim = timeline_df.iloc[-1]
    net_gain = round(
        last_sim["Aproveitamento Médio (%)"] - first_sim["Aproveitamento Médio (%)"],
        2,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Simulados na Série", f"{len(timeline_df)} de 8")
    c2.metric(
        f"Linha de Base ({first_sim['Simulado']})",
        f"{first_sim['Aproveitamento Médio (%)']:.1f}%",
    )
    c3.metric(
        f"Último Aplicado ({last_sim['Simulado']})",
        f"{last_sim['Aproveitamento Médio (%)']:.1f}%",
        delta=f"{net_gain:+.1f} p.p. vs. base" if len(timeline_df) > 1 else None,
    )
    c4.metric(
        "Média Acumulada no Ano",
        f"{timeline_df['Aproveitamento Médio (%)'].mean():.1f}%",
    )

    fig_geral = px.line(
        timeline_df,
        x="Simulado",
        y="Aproveitamento Médio (%)",
        markers=True,
        text="Aproveitamento Médio (%)",
        title=f"Evolução do Aproveitamento Médio Geral — {selected_year}",
        template="plotly_white",
        color_discrete_sequence=["#123B66"],
        range_y=[0, 100],
    )
    fig_geral.update_traces(textposition="top center", line=dict(width=3))
    st.plotly_chart(fig_geral, use_container_width=True)

    show_dataframe(
        timeline_df[
            [
                "Simulado",
                "Registros",
                "Aproveitamento Médio (%)",
                "Variação (Δ p.p.)",
                "Dispersão entre Habilidades (DP)",
            ]
        ]
    )

    st.divider()

    if macro_rows:
        st.subheader("Evolução Contínua por Macro-Eixo Cognitivo")
        st.caption(
            "Consolida apenas as habilidades SAEB/BNCC mapeadas nos 4 domínios cognitivos "
            "para manter comparabilidade contínua entre edições."
        )
        macro_df = pd.DataFrame(macro_rows).sort_values("Ordem")

        simulados_ordenados = [
            f"{num}º Simulado" for num in sorted(macro_df["Ordem"].unique())
        ]
        eixos_ordenados = sorted(macro_df["Macro-Eixo"].unique())
        grade_completa = pd.MultiIndex.from_product(
            [simulados_ordenados, eixos_ordenados],
            names=["Simulado", "Macro-Eixo"],
        ).to_frame(index=False)

        macro_plot_df = grade_completa.merge(
            macro_df[["Simulado", "Macro-Eixo", "Aproveitamento (%)"]],
            on=["Simulado", "Macro-Eixo"],
            how="left",
        )

        fig_macro = px.line(
            macro_plot_df,
            x="Simulado",
            y="Aproveitamento (%)",
            color="Macro-Eixo",
            markers=True,
            title="Desempenho por Macro-Eixo ao Longo dos Simulados",
            template="plotly_white",
            range_y=[0, 100],
            category_orders={
                "Simulado": simulados_ordenados,
                "Macro-Eixo": eixos_ordenados,
            },
        )
        fig_macro.update_traces(line=dict(width=2.5), connectgaps=False)
        fig_macro.update_xaxes(type="category")
        _apply_responsive_legend(fig_macro, bottom_margin=115)
        st.plotly_chart(fig_macro, use_container_width=True)

    if skill_rows:
        st.divider()
        st.subheader("Evolução por Habilidade Específica (Pareamento SAEB)")
        skills_temp_df = pd.DataFrame(skill_rows).sort_values("Ordem")

        counts = skills_temp_df.groupby("Código SAEB")["Simulado"].nunique()
        recorrentes = sorted(counts[counts >= 2].index.tolist())
        todas = sorted(counts.index.tolist())

        desc_por_codigo = (
            skills_temp_df.drop_duplicates("Código SAEB")
            .set_index("Código SAEB")["Descrição"]
            .to_dict()
        )

        opcoes_formatadas = [
            f"{cod} — {desc_por_codigo.get(cod, '')}" for cod in todas
        ]
        default_codes = recorrentes[:5] if recorrentes else todas[:5]
        default_formatadas = [
            f"{cod} — {desc_por_codigo.get(cod, '')}" for cod in default_codes
        ]

        selecionadas_raw = st.multiselect(
            "Selecione os códigos SAEB para comparar ao longo das edições",
            options=opcoes_formatadas,
            default=default_formatadas,
            format_func=lambda item: item.split(" — ", 1)[0],
            help="Clique na caixa para pesquisar pelo código ou pela descrição da habilidade.",
            key="temporal_saeb_codes",
        )

        selecionadas = [item.split(" — ", 1)[0] for item in selecionadas_raw]

        if selecionadas:
            filtered_skills = skills_temp_df[
                skills_temp_df["Código SAEB"].isin(selecionadas)
            ]
            fig_saeb = px.line(
                filtered_skills,
                x="Simulado",
                y="Aproveitamento (%)",
                color="Código SAEB",
                markers=True,
                hover_data={"Descrição": True},
                title="Curva de Aprendizagem por Código SAEB",
                template="plotly_white",
                range_y=[0, 100],
            )
            _apply_responsive_legend(fig_saeb, bottom_margin=110)
            st.plotly_chart(fig_saeb, use_container_width=True)

            pivot_saeb = (
                filtered_skills.pivot_table(
                    index=["Código SAEB", "Descrição"],
                    columns="Simulado",
                    values="Aproveitamento (%)",
                    aggfunc="mean",
                )
                .reset_index()
            )
            show_dataframe(pivot_saeb)
    st.divider()
    st.subheader("Exportação do Relatório Geral Consolidado")
    st.caption(
        f"Gera um PDF único consolidando todos os {len(timeline_df)} simulados importados "
        f"em {selected_year}, incluindo evolução geral, Macro-Eixos, pareamento SAEB e detalhamento por edição."
    )

    if st.button(
        f"Gerar Relatório Geral Consolidado ({selected_year}) em PDF",
        type="primary",
        use_container_width=True,
        key="btn_generate_temporal_general_pdf",
    ):
        try:
            from src.pdf_exporter import generate_temporal_general_pdf_report

            with st.spinner("Consolidando todos os simulados e renderizando gráficos..."):
                logo_path = Path(__file__).resolve().parents[3] / "assets" / "logo.png"
                macro_df_export = (
                    pd.DataFrame(macro_rows).sort_values("Ordem")
                    if macro_rows
                    else None
                )
                skills_df_export = (
                    pd.DataFrame(skill_rows).sort_values("Ordem")
                    if skill_rows
                    else None
                )
                general_pdf_bytes = generate_temporal_general_pdf_report(
                    selected_year=selected_year,
                    timeline_df=timeline_df,
                    macro_df=macro_df_export,
                    skills_temp_df=skills_df_export,
                    per_simulado_summaries=per_simulado_summaries,
                    logo_path=logo_path,
                )
                st.session_state["temporal_general_pdf_bytes"] = general_pdf_bytes
                st.session_state["temporal_general_pdf_name"] = (
                    f"SAIP_Relatorio_Geral_Consolidado_{selected_year}.pdf"
                )
        except Exception as exc:
            st.error(f"Erro ao gerar o Relatório Geral em PDF: {exc}")

    if "temporal_general_pdf_bytes" in st.session_state:
        st.download_button(
            f"Baixar Relatório Geral Consolidado ({selected_year}) — PDF",
            data=st.session_state["temporal_general_pdf_bytes"],
            file_name=st.session_state["temporal_general_pdf_name"],
            mime="application/pdf",
            use_container_width=True,
            key="btn_download_temporal_general_pdf",
        )


def render_skill_analysis(df: pd.DataFrame, simulado_num: int | None = None) -> None:
    """Aba 3: Análise Pedagógica por Habilidades (SAEB / BNCC)."""
    st.subheader("Análise Pedagógica por Habilidades (SAEB / BNCC)")
    edicao_txt = f"{simulado_num}º Simulado SAEB" if simulado_num else "Simulados SAEB"
    st.caption(
        f"Matriz de referência: Língua Portuguesa — 8º Ano ({edicao_txt} — SEMEC Teresina)."
    )

    summary = _build_skill_summary(df, simulado_num=simulado_num)
    catalog_df = get_skills_catalog_df()

    if not summary.empty:
        mapped_count = (summary["Código SAEB"] != "Não mapeado").sum()
        best_row = summary.loc[summary["Aproveitamento (%)"].idxmax()]
        worst_row = summary.loc[summary["Aproveitamento (%)"].idxmin()]

        m1, m2, m3 = st.columns(3)
        m1.metric("Indicadores Analisados", len(summary))
        m2.metric("Habilidades SAEB Identificadas", mapped_count)
        m3.metric(
            "Aproveitamento Médio Geral",
            f"{summary['Aproveitamento (%)'].mean():.1f}%",
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
                unsafe_allow_html=True,
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
                unsafe_allow_html=True,
            )

        summary["Rótulo Gráfico"] = summary.apply(
            lambda r: (
                f"{r['Código SAEB']} ({r['Coluna no Arquivo']})"
                if r["Código SAEB"] != "Não mapeado"
                else r["Coluna no Arquivo"]
            ),
            axis=1,
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
            height=max(420, len(summary) * 45),
        )
        _apply_responsive_legend(fig, bottom_margin=100)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detalhamento Estatístico e Pedagógico")
        display_cols = [
            "Coluna no Arquivo",
            "Código SAEB",
            "Código BNCC",
            "Macro-Eixo",
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

    with st.expander(
        "Catálogo Oficial de Habilidades — Língua Portuguesa (8º Ano | SAEB)",
        expanded=summary.empty,
    ):
        f1, f2 = st.columns([1, 2])
        with f1:
            bloco_filter = st.selectbox(
                "Filtrar por Bloco do Simulado",
                ["Todos os Blocos", "Bloco 1", "Bloco 2", "Bloco 3", "Bloco 4"],
                key="skill_bloco_filter",
            )
        with f2:
            search_term = st.text_input(
                "Buscar habilidade por código ou palavra-chave",
                placeholder="Ex.: 9L2.1.G, EF69LP14, metáfora, reclamação, poema...",
                key="skill_search_term",
            )

        filtered_catalog = catalog_df.copy()

        if bloco_filter != "Todos os Blocos" and "Bloco" in filtered_catalog.columns:
            filtered_catalog = filtered_catalog[
                filtered_catalog["Bloco"].str.contains(bloco_filter, case=False, na=False)
            ]

        if search_term.strip():
            term = search_term.strip()
            mask = pd.Series(False, index=filtered_catalog.index)
            for col in filtered_catalog.columns:
                mask = mask | filtered_catalog[col].astype(str).str.contains(
                    term, case=False, na=False
                )
            filtered_catalog = filtered_catalog[mask]

        st.caption(f"Exibindo {len(filtered_catalog)} de {len(catalog_df)} habilidades mapeadas.")
        show_dataframe(filtered_catalog)


def render_descriptive_analysis(df: pd.DataFrame, metrics: dict) -> None:
    """Aba 4 (Parte 1): Estatísticas descritivas, histograma e diagrama de caixa."""
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
        key="descriptive_variable",
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
            color_discrete_sequence=["#123B66"],
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
            color_discrete_sequence=["#123B66"],
        )
        fig.update_layout(autosize=True)
        st.plotly_chart(fig, use_container_width=True)


def render_categorical_analysis(df: pd.DataFrame) -> None:
    """Aba 4 (Parte 2): Tabela de frequência e gráfico de barras para variáveis categóricas."""
    categorical_columns = get_categorical_columns(df)

    if not categorical_columns:
        st.info("Não foram encontradas variáveis categóricas.")
        return

    selected = st.selectbox(
        "Selecione uma variável categórica",
        categorical_columns,
        key="categorical_variable",
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
            color_discrete_sequence=["#123B66"],
        )
        st.plotly_chart(fig, use_container_width=True)


def render_group_analysis(df: pd.DataFrame) -> None:
    """Aba 5: Comparação de indicadores numéricos agrupados por turma, escola ou categoria."""
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
            key="group_column",
        )

    with c2:
        value_column = st.selectbox(
            "Indicador numérico",
            numeric_columns,
            key="group_value",
        )

    grouped = (
        df.groupby(group_column, dropna=False)[value_column]
        .agg(
            Quantidade="count",
            Média="mean",
            Mediana="median",
            **{"Desvio padrão": "std"},
            Mínimo="min",
            Máximo="max",
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
        color_discrete_sequence=["#123B66"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_quality_analysis(df: pd.DataFrame) -> None:
    """Aba 6: Diagnóstico de integridade, tipos de dados e completude por coluna."""
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
        ],
    })

    show_dataframe(quality)

    fig = px.bar(
        quality,
        x="Coluna",
        y="Completude (%)",
        title="Completude por variável",
        range_y=[0, 100],
        template="plotly_white",
        color_discrete_sequence=["#123B66"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_report(
    df: pd.DataFrame,
    metrics: dict,
    dataset_name: str | None = None,
    simulado_num: int | None = None,
    ano_letivo: int = 2026,
) -> None:
    """Aba 7: Exportação segmentada em PDF com gráficos, CSV e JSON."""
    st.subheader("Exportação dos resultados")
    st.caption(
        "Gere o relatório pedagógico completo em PDF (com todas as análises "
        "segmentadas, tabelas formatadas e gráficos) ou exporte os dados brutos."
    )

    nome_relatorio = (
        dataset_name
        or st.session_state.get("current_name")
        or "Analise_SAIP"
    )
    sim_atual = simulado_num or st.session_state.get("current_simulado_num")
    ano_atual = int(st.session_state.get("current_ano_letivo", ano_letivo))

    if st.button(
        "Gerar Relatório Completo em PDF (Segmentado com Gráficos)",
        type="primary",
        use_container_width=True,
        key="btn_generate_full_pdf",
    ):
        try:
            from src.pdf_exporter import generate_segmented_pdf_report

            with st.spinner("Renderizando gráficos e montando o relatório PDF..."):
                skill_summary = _build_skill_summary(df, simulado_num=sim_atual)

                temporal_timeline_df = None
                temporal_macro_df = None
                saved_datasets = get_datasets_by_year(ano_atual)
                if saved_datasets:
                    t_rows = []
                    m_rows = []
                    for item in saved_datasets:
                        s_num = int(item.get("simulado_num", 1))
                        s_label = f"{s_num}º Simulado"
                        s_df = sanitize_dataframe_columns(pd.DataFrame(item["records"]))
                        s_sum = _build_skill_summary(s_df, simulado_num=s_num)
                        if s_sum.empty:
                            continue
                        mapped = s_sum[s_sum["Código SAEB"] != "Não mapeado"]
                        basis = mapped if not mapped.empty else s_sum
                        t_rows.append({
                            "Ordem": s_num,
                            "Simulado": s_label,
                            "Registros": item["row_count"],
                            "Aproveitamento Médio (%)": round(float(basis["Aproveitamento (%)"].mean()), 2),
                            "Dispersão entre Habilidades (DP)": (
                                round(float(basis["Aproveitamento (%)"].std()), 2)
                                if len(basis) > 1
                                else 0.0
                            ),
                        })
                        if not mapped.empty:
                            by_m = mapped.groupby("Macro-Eixo", as_index=False)["Aproveitamento (%)"].mean()
                            for _, mr in by_m.iterrows():
                                m_rows.append({
                                    "Ordem": s_num,
                                    "Simulado": s_label,
                                    "Macro-Eixo": mr["Macro-Eixo"],
                                    "Aproveitamento (%)": round(float(mr["Aproveitamento (%)"]), 2),
                                })
                    if t_rows:
                        temporal_timeline_df = pd.DataFrame(t_rows).sort_values("Ordem")
                        temporal_timeline_df["Variação (Δ p.p.)"] = (
                            temporal_timeline_df["Aproveitamento Médio (%)"].diff().round(2)
                        )
                    if m_rows:
                        temporal_macro_df = pd.DataFrame(m_rows).sort_values("Ordem")

                logo_path = Path(__file__).resolve().parents[3] / "assets" / "logo.png"
                pdf_bytes = generate_segmented_pdf_report(
                    df=df,
                    metrics=metrics,
                    dataset_name=nome_relatorio,
                    skill_summary_df=skill_summary,
                    temporal_timeline_df=temporal_timeline_df,
                    temporal_macro_df=temporal_macro_df,
                    logo_path=logo_path,
                )
                st.session_state["generated_pdf_bytes"] = pdf_bytes
                st.session_state["generated_pdf_name"] = (
                    f"SAIP_Relatorio_{nome_relatorio.replace(' ', '_')}.pdf"
                )
        except Exception as exc:
            st.error(f"Erro ao gerar o PDF: {exc}")

    if "generated_pdf_bytes" in st.session_state:
        st.download_button(
            "Baixar Relatório PDF Pronto",
            data=st.session_state["generated_pdf_bytes"],
            file_name=st.session_state["generated_pdf_name"],
            mime="application/pdf",
            use_container_width=True,
            key="btn_download_full_pdf",
        )

    st.divider()

    clean_df = sanitize_dataframe_columns(df)
    csv_data = clean_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar dados analisados (CSV)",
        data=csv_data,
        file_name="saip_dados_analisados.csv",
        mime="text/csv",
        use_container_width=True,
    )

    translated_metrics = translate_metrics_dict(metrics)
    json_data = json.dumps(
        translated_metrics,
        ensure_ascii=False,
        indent=4,
        default=str,
    )

    st.download_button(
        "Baixar métricas (JSON)",
        data=json_data.encode("utf-8"),
        file_name="saip_metricas.json",
        mime="application/json",
        use_container_width=True,
    )