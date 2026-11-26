"""
Módulo de Visualização: Histórico de Importações.

Lista os simulados salvos no banco SQLite local ordenados por ano letivo
e edição (1º ao 8º) e permite recarregá-los para o Dashboard.
"""

import pandas as pd
import streamlit as st

from src.database import get_dataset, list_datasets
from src.ui.components import sanitize_dataframe_columns, show_dataframe


def render_history_page() -> None:
    """Renderiza a página de consulta e carregamento de simulados salvos."""
    st.title("Histórico de Importações")
    st.caption("Consulte os simulados armazenados no SAIP por ano letivo e edição.")

    items = list_datasets()

    if not items:
        st.info(
            "Ainda não existem simulados importados na base local. "
            "Acesse **Carga de Dados** no menu lateral para enviar um arquivo."
        )
        return

    history = pd.DataFrame(items)
    if "simulado_num" in history.columns:
        history["Edição"] = history["simulado_num"].apply(lambda n: f"{n}º Simulado")

    history = history.rename(
        columns={
            "id": "Código",
            "ano_letivo": "Ano Letivo",
            "name": "Identificação",
            "original_filename": "Arquivo original",
            "row_count": "Registros",
            "created_at": "Data de importação",
            "created_by": "Usuário",
        }
    )

    expected_columns = [
        "Código",
        "Ano Letivo",
        "Edição",
        "Identificação",
        "Arquivo original",
        "Registros",
        "Data de importação",
        "Usuário",
    ]

    available_columns = [
        col for col in expected_columns if col in history.columns
    ]

    show_dataframe(history[available_columns])

    selected_id = st.selectbox(
        "Selecione um simulado salvo",
        options=[item["id"] for item in items],
        format_func=lambda value: next(
            f"#{item['id']} — {item['simulado_num']}º Simulado/{item['ano_letivo']} ({item['name']})"
            for item in items
            if item["id"] == value
        ),
    )

    if st.button(
        "Carregar análise salva",
        type="primary",
        use_container_width=True,
    ):
        item = get_dataset(selected_id)

        if item:
            loaded_df = sanitize_dataframe_columns(
                pd.DataFrame(item["records"])
            )

            st.session_state.current_df = loaded_df
            st.session_state.current_metrics = item["metrics"]
            st.session_state.current_name = item["name"]
            st.session_state.current_simulado_num = item["simulado_num"]
            st.session_state.current_ano_letivo = item["ano_letivo"]

            st.success(
                f"{item['simulado_num']}º Simulado/{item['ano_letivo']} carregado! "
                "Clique em **Dashboard** no menu lateral para visualizar os resultados."
            )