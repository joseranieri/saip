"""
Módulo de Visualização: Painel Principal (Dashboard).

Gerencia a importação de arquivos CSV, pré-visualização, anonimização/exclusão
de colunas identificadoras, persistência opcional no banco local e a exibição
das abas analíticas.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

from src.analyzer import (
    analyze_dataframe,
    detect_identifier_columns,
    read_csv_safely,
)
from src.database import save_dataset
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
)


def render_dashboard_page(logo_path: Path) -> None:
    """Renderiza a página principal do Painel de Inteligência Pedagógica."""
    st.title("Painel de Inteligência Pedagógica")
    st.caption(
        "Importe seus dados e explore indicadores, estatísticas "
        "e informações para apoiar a análise pedagógica."
    )

    st.divider()

    # Seção de upload e configuração do tratamento dos dados
    with st.expander("Importar novo arquivo CSV", expanded=True):
        uploaded = st.file_uploader(
            "Selecione um arquivo CSV",
            type=["csv"],
            key="csv_upload"
        )

        if uploaded is not None:
            try:
                raw_df = read_csv_safely(uploaded)
                preview_df = sanitize_dataframe_columns(raw_df)

                st.success(
                    f"Arquivo carregado: {len(preview_df):,} registros "
                    f"e {len(preview_df.columns)} colunas."
                )

                st.write("Pré-visualização")
                show_dataframe(preview_df.head(10))

                # Sugere automaticamente colunas com dados pessoais/identificadores
                suggested = detect_identifier_columns(preview_df.columns)

                excluded = st.multiselect(
                    "Colunas que não devem participar da análise "
                    "nem ser armazenadas",
                    options=list(preview_df.columns),
                    default=suggested
                )

                persist = st.checkbox(
                    "Salvar os dados processados na base local"
                )

                dataset_name = st.text_input(
                    "Nome da importação",
                    value=uploaded.name.rsplit(".", 1)[0]
                )

                if st.button(
                    "Processar dados",
                    type="primary",
                    use_container_width=True
                ):
                    analysis_df = preview_df.drop(
                        columns=excluded,
                        errors="ignore"
                    )

                    if analysis_df.empty:
                        st.error("Não existem colunas disponíveis para análise.")
                    else:
                        metrics = analyze_dataframe(analysis_df)

                        st.session_state.current_df = analysis_df
                        st.session_state.current_metrics = metrics
                        st.session_state.current_name = dataset_name

                        if persist:
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
                                username=st.session_state.username
                            )

                            st.success(
                                "Dados processados e armazenados com sucesso."
                            )
                        else:
                            st.success(
                                "Análise concluída. Os dados permanecerão "
                                "disponíveis apenas nesta sessão."
                            )

            except Exception as exc:
                st.error(f"Erro ao processar o arquivo: {exc}")

    # Exibição dos resultados caso exista uma base processada na sessão
    if (
        "current_df" in st.session_state
        and "current_metrics" in st.session_state
    ):
        df = sanitize_dataframe_columns(st.session_state.current_df)
        metrics = st.session_state.current_metrics

        st.divider()
        st.subheader(f"Resultados da análise: {st.session_state.current_name}")

        tabs = st.tabs([
            "Visão Geral",
            "Estatísticas",
            "Turmas e Grupos",
            "Habilidades",
            "Qualidade dos Dados",
            "Relatórios"
        ])

        with tabs[0]:
            render_overview(df, metrics)
            st.subheader("Visualização da base")
            show_dataframe(df.head(20))

        with tabs[1]:
            render_descriptive_analysis(df, metrics)
            st.divider()
            render_categorical_analysis(df)

        with tabs[2]:
            render_group_analysis(df)

        with tabs[3]:
            render_skill_analysis(df)

        with tabs[4]:
            render_quality_analysis(df)

        with tabs[5]:
            render_report(df, metrics)

    else:
        st.info(
            "Importe um arquivo CSV e clique em Processar dados "
            "para visualizar as análises."
        )
