"""
Módulo de Componentes Reutilizáveis da Interface (UI).

Contém funções auxiliares para sanitização de colunas de DataFrames,
exibição padronizada de tabelas e identificação de tipos de variáveis.
"""

import re
import pandas as pd
import streamlit as st


def sanitize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Substitui nomes de colunas genéricos em inglês (como 'Unnamed: 0')
    ou vazios por rótulos claros em português ('Coluna sem nome 1').
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


def show_dataframe(df: pd.DataFrame) -> None:
    """
    Renderiza um DataFrame no Streamlit ocupando toda a largura disponível,
    ocultando o índice numérico e garantindo nomes de colunas sanitizados.
    """
    st.dataframe(
        sanitize_dataframe_columns(df),
        use_container_width=True,
        hide_index=True
    )


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Retorna uma lista com os nomes das colunas numéricas do DataFrame."""
    return list(df.select_dtypes(include="number").columns)


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    """Retorna uma lista com os nomes das colunas categóricas/textuais do DataFrame."""
    return list(
        df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns
    )
