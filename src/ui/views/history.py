"""
Módulo de Visualização: Histórico de Importações.

Lista os conjuntos de dados persistidos no banco SQLite local e permite
recarregá-los para a sessão ativa do Dashboard.
"""

import pandas as pd
import streamlit as st

from src.database import get_dataset, list_datasets
from src.ui.components import sanitize_dataframe_columns, show_dataframe


def render_history_page() -> None:
    """Renderiza a página de consulta e carregamento de bases salvas."""
    st.title("Histórico de importações")
    st.caption("Consulte os conjuntos de dados armazenados no SAIP.")

    items = list_datasets()

    if not items:
        st.info("Ainda não existem conjuntos de dados importados.")
        return

    history = pd.DataFrame(items).rename(
        columns={
            "id": "Código",
            "name": "Nome da importação",
            "original_filename": "Arquivo original",
            "row_count": "Registros",
            "created_at": "Data de importação",
            "created_by": "Usuário",
        }
    )

    expected_columns = [
        "Código",
        "Nome da importação",
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
        "Selecione uma importação",
        options=[item["id"] for item in items],
        format_func=lambda value: next(
            f"#{item['id']} — {item['name']}"
            for item in items
            if item["id"] == value
        )
    )

    if st.button(
        "Carregar análise salva",
        type="primary",
        use_container_width=True
    ):
        item = get_dataset(selected_id)

        if item:
            loaded_df = sanitize_dataframe_columns(
                pd.DataFrame(item["records"])
            )

            st.session_state.current_df = loaded_df
            st.session_state.current_metrics = item["metrics"]
            st.session_state.current_name = item["name"]

            st.success(
                "Dados carregados. Acesse o Dashboard para visualizar."
            )
