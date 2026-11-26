"""
Módulo de Componentes Reutilizáveis de Interface do SAIP.

Fornece sanitização de nomes de colunas, substituição de valores vazios/None
por hífen ('-') nas tabelas e detecção de colunas numéricas e categóricas.
"""

import re
import pandas as pd
import streamlit as st


def sanitize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Substitui nomes de colunas genéricos em inglês (como 'Unnamed: 0')
    por rótulos claros em português ('Coluna sem nome 1').
    """
    cleaned = df.copy()
    new_columns = []
    unnamed_counter = 1

    for col in cleaned.columns:
        col_str = str(col).strip()
        if not col_str or re.match(r"^unnamed(?::\s*\d+)?$", col_str, re.IGNORECASE):
            new_columns.append(f"Coluna sem nome {unnamed_counter}")
            unnamed_counter += 1
        else:
            new_columns.append(col_str)

    cleaned.columns = new_columns
    return cleaned


def _format_empty_values_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Substitui valores ausentes (NaN, None, strings vazias ou literais 'None'/'nan')
    por '-' apenas na camada de exibição das tabelas.
    """
    display_df = sanitize_dataframe_columns(df).copy()

    for col in display_df.columns:
        series = display_df[col]
        # Converte para object para permitir inserir '-' mesmo em colunas numéricas na exibição
        obj_series = series.astype(object)
        mask_null = pd.isna(series)
        mask_literal = obj_series.apply(
            lambda v: isinstance(v, str)
            and v.strip().lower() in {"", "none", "nan", "nat", "null", "<na>"}
        )
        obj_series[mask_null | mask_literal] = "-"
        display_df[col] = obj_series

    return display_df


def show_dataframe(df: pd.DataFrame) -> None:
    """Exibe DataFrames padronizados em português e com '-' nos campos vazios."""
    formatted_df = _format_empty_values_for_display(df)
    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True,
    )


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Retorna a lista de colunas numéricas do DataFrame."""
    return list(df.select_dtypes(include="number").columns)


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    """Retorna a lista de colunas categóricas/textuais do DataFrame."""
    return list(
        df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns
    )