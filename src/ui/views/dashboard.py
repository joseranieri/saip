"""
Módulo de Visualização: Carga de Dados e Dashboard Analítico.

Separa a interface de envio/importação de CSV (render_upload_page)
da interface de análise pedagógica e temporal (render_dashboard_page).
"""

import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

from src.analyzer import (
    analyze_dataframe,
    detect_identifier_columns,
    read_csv_safely,
)
from src.database import get_datasets_by_year, save_dataset
from src.ui.components import sanitize_dataframe_columns, show_dataframe
from src.ui.styles import show_logo
from src.ui.views.tabs import (
    render_categorical_analysis,
    render_descriptive_analysis,
    render_group_analysis,
    render_overview,
    render_quality_analysis,
    render_report,
    render_skill_analysis,
    render_temporal_analysis,
)

SIMULADOS_OPCOES = {
    i: f"{i}º Simulado SAEB" for i in range(1, 9)
}

EXTRA_NAME_PATTERNS = re.compile(
    r"(?:^|_|\b)(nome|aluno|estudante|discente|candidato|matricula|matrícula|cpf|rg|ra|inep|id_aluno)(?:_|\b|$)",
    re.IGNORECASE,
)


def _remove_student_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove automaticamente colunas com nomes ou identificadores de alunos."""
    detected = set(detect_identifier_columns(df.columns))
    extra = {col for col in df.columns if EXTRA_NAME_PATTERNS.search(str(col))}
    cols_to_drop = list(detected | extra)
    return df.drop(columns=cols_to_drop, errors="ignore")


def render_upload_page(logo_path: Path) -> None:
    """Renderiza a tela dedicada exclusivamente à Carga de Dados (1º ao 8º Simulado)."""
    
    st.title("Carga de Dados")
    st.caption(
        "Selecione a edição do simulado (1º ao 8º), envie o arquivo CSV para "
        "anonimização automática e gravação na base de dados local."
    )

    st.divider()

    c_sim, c_ano = st.columns([1.5, 1])

    with c_sim:
        simulado_num = st.selectbox(
            "Qual simulado você está enviando?",
            options=list(SIMULADOS_OPCOES.keys()),
            format_func=lambda k: SIMULADOS_OPCOES[k],
            key="upload_simulado_num",
        )

    with c_ano:
        ano_letivo = st.number_input(
            "Ano Letivo",
            min_value=2020,
            max_value=2035,
            value=datetime.now().year,
            step=1,
            key="upload_ano_letivo",
        )

    uploaded = st.file_uploader(
        f"Selecione o arquivo CSV do {simulado_num}º Simulado SAEB ({int(ano_letivo)})",
        type=["csv"],
        key="csv_upload",
    )

    if uploaded is not None:
        if st.button(
            f"Processar e salvar {simulado_num}º Simulado",
            type="primary",
            use_container_width=True,
        ):
            try:
                raw_df = read_csv_safely(uploaded)
                clean_df = sanitize_dataframe_columns(raw_df)
                analysis_df = _remove_student_identifiers(clean_df)

                if analysis_df.empty:
                    st.error("Não existem colunas válidas disponíveis para análise.")
                else:
                    dataset_name = f"{simulado_num}º Simulado SAEB/{int(ano_letivo)}"

                    analysis_df = analysis_df.copy()
                    analysis_df["Simulado"] = f"{simulado_num}º Simulado"
                    analysis_df["Ordem_Simulado"] = int(simulado_num)
                    analysis_df["Ano_Letivo"] = int(ano_letivo)

                    metrics = analyze_dataframe(analysis_df)

                    st.session_state.current_df = analysis_df
                    st.session_state.current_metrics = metrics
                    st.session_state.current_name = dataset_name
                    st.session_state.current_simulado_num = int(simulado_num)
                    st.session_state.current_ano_letivo = int(ano_letivo)

                    records = (
                        analysis_df
                        .astype(object)
                        .where(pd.notna(analysis_df), None)
                        .to_dict(orient="records")
                    )

                    save_dataset(
                        name=dataset_name,
                        original_filename=uploaded.name,
                        row_count=len(analysis_df),
                        column_names=list(analysis_df.columns),
                        records=records,
                        metrics=metrics,
                        username=st.session_state.username,
                        simulado_num=int(simulado_num),
                        ano_letivo=int(ano_letivo),
                    )

                    st.success(
                        f"{dataset_name} processado ({len(analysis_df):,} registros anonimizados) "
                        "e salvo na base local! Acesse o menu **Dashboard** para visualizar os gráficos."
                    )

            except Exception as exc:
                st.error(f"Erro ao processar o arquivo: {exc}")

    # Resumo rápido das edições já carregadas no ano selecionado
    st.divider()
    st.subheader(f"Status das Importações — {int(ano_letivo)}")
    datasets_ano = get_datasets_by_year(int(ano_letivo))
    loaded_nums = {int(d.get("simulado_num", 1)) for d in datasets_ano}

    cols = st.columns(8)
    for idx in range(1, 9):
        with cols[idx - 1]:
            if idx in loaded_nums:
                st.success(f"**{idx}º Sim.**\n\nSalvo")
            else:
                st.warning(f"**{idx}º Sim.**\n\nPendente")


def render_dashboard_page(logo_path: Path) -> None:
    """Renderiza exclusivamente o Painel Analítico (Dashboard)."""
    

    st.title("Dashboard — Inteligência Pedagógica")
    st.caption(
        "Explore indicadores, desempenho por habilidade SAEB/BNCC e a evolução "
        "temporal dos simulados."
    )

    st.divider()

    has_current = (
        "current_df" in st.session_state
        and "current_metrics" in st.session_state
    )

    if has_current:
        df = _remove_student_identifiers(
            sanitize_dataframe_columns(st.session_state.current_df)
        )
        metrics = st.session_state.current_metrics
        sim_atual = st.session_state.get("current_simulado_num", 1)
        ano_atual = st.session_state.get("current_ano_letivo", datetime.now().year)

        st.subheader(f"Resultados em análise: {st.session_state.current_name}")

        tabs = st.tabs([
            "Visão Geral",
            "Evolução Temporal (1º ao 8º)",
            "Habilidades",
            "Estatísticas",
            "Turmas e Grupos",
            "Qualidade dos Dados",
            "Relatórios",
        ])

        with tabs[0]:
            render_overview(df, metrics)
            st.subheader("Visualização da base (anonimizada)")
            show_dataframe(df.head(20))

        with tabs[1]:
            render_temporal_analysis(default_year=ano_atual)

        with tabs[2]:
            render_skill_analysis(df, simulado_num=sim_atual)

        with tabs[3]:
            render_descriptive_analysis(df, metrics)
            st.divider()
            render_categorical_analysis(df)

        with tabs[4]:
            render_group_analysis(df)

        with tabs[5]:
            render_quality_analysis(df)

        with tabs[6]:
            render_report(df, metrics)

    else:
        st.info(
            "Nenhum simulado selecionado para análise individual no momento. "
            "Use **Carga de Dados** para enviar um arquivo ou **Histórico de Importações** "
            "para carregar uma edição salva. Abaixo está a série temporal consolidada:"
        )
        render_temporal_analysis(default_year=datetime.now().year)